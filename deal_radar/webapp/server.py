#!/usr/bin/env python3
"""
Deal Radar Webapp – Backend mit AI Chat, echten Distressed-Signalen aus ChromaDB
und direkten PDF-Links.
"""

import os
import sys
import json
import glob
import csv
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── .env laden BEVOR OpenAI importiert wird ──────────────────────────────────
_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(_env):
    for line in open(_env):
        if line.startswith('OPENAI_API_KEY='):
            os.environ['OPENAI_API_KEY'] = line.split('=', 1)[1].strip()

import chromadb
from openai import OpenAI
from pipeline_queue import queue

# ── Globale Singletons ───────────────────────────────────────────────────────
BASE_DIR      = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
CHROMA_DIR    = os.path.join(BASE_DIR, 'data', 'chroma_db')
DOWNLOADS_DIR = os.path.join(BASE_DIR, 'data', 'downloads')
HITS_FILE     = os.path.join(BASE_DIR, 'data', 'outputs', 'report_hits.jsonl')
SCORES_FILE   = os.path.join(BASE_DIR, 'data', 'outputs', 'deal_radar.csv')

chroma   = chromadb.PersistentClient(path=CHROMA_DIR)
coll     = chroma.get_collection('deal_radar_reports')
openai_c = OpenAI()

HIT_TYPE_LABELS = {
    'carve_out':        'Carve-out / Divestment',
    'loss_stress':      'Verlust / Financial Distress',
    'biz_services':     'Business Services (extern)',
    'external_revenue': 'Externe Umsaetze',
}

# ── Daten beim Start laden ───────────────────────────────────────────────────

def load_hits():
    hits = {}
    if not os.path.exists(HITS_FILE):
        return hits
    with open(HITS_FILE) as f:
        for line in f:
            h = json.loads(line)
            cid = h['company_id']
            hits.setdefault(cid, []).append(h)
    return hits

def load_scores():
    scores = {}
    if not os.path.exists(SCORES_FILE):
        return scores
    with open(SCORES_FILE, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f, delimiter=';'):
            cid = row['company_id']
            year = row.get('year', '?')
            scores[f"{cid}_{year}"] = row
    return scores

def load_pdfs():
    pdfs = {}
    for p in glob.glob(os.path.join(DOWNLOADS_DIR, '**', '*.pdf'), recursive=True):
        rel   = os.path.relpath(p, DOWNLOADS_DIR)
        parts = rel.split(os.sep)
        if len(parts) >= 2:
            cid = parts[0]
            pdfs.setdefault(cid, []).append({
                'year':     parts[1],
                'filename': parts[-1],
                'url':      '/pdfs/' + rel.replace(os.sep, '/'),
                'size_kb':  round(os.path.getsize(p) / 1024),
            })
    for cid in pdfs:
        pdfs[cid].sort(key=lambda x: x['year'], reverse=True)
    return pdfs

ALL_HITS   = load_hits()
ALL_SCORES = load_scores()
ALL_PDFS   = load_pdfs()

# ── Hilfsfunktion: txt-Dateiname → PDF-URL ───────────────────────────────────

def _txt_to_pdf_url(company_id, year, txt_filename):
    """Wandelt z.B. 'fujitsu_2012_b7f7fb43.txt' → '/pdfs/fujitsu/2012/fujitsu_2012_b7f7fb43.pdf'"""
    if not txt_filename or txt_filename == '?':
        return None
    pdf_name = txt_filename.replace('.txt', '.pdf')
    pdf_path = os.path.join(DOWNLOADS_DIR, company_id, str(year), pdf_name)
    if os.path.isfile(pdf_path):
        return f'/pdfs/{company_id}/{year}/{pdf_name}'
    # Fallback: in allen Jahresordnern suchen
    for y_dir in sorted(os.listdir(os.path.join(DOWNLOADS_DIR, company_id)), reverse=True) \
            if os.path.isdir(os.path.join(DOWNLOADS_DIR, company_id)) else []:
        candidate = os.path.join(DOWNLOADS_DIR, company_id, y_dir, pdf_name)
        if os.path.isfile(candidate):
            return f'/pdfs/{company_id}/{y_dir}/{pdf_name}'
    return None

# ── API-Logik ────────────────────────────────────────────────────────────────

def api_companies():
    companies = {}
    for cid, hits in ALL_HITS.items():
        c = companies.setdefault(cid, {
            'company_id': cid, 'name': cid.replace('_', ' ').title(),
            'years': set(), 'hit_types': set(), 'hit_count': 0,
            'hits_by_type': {}, 'pdfs': ALL_PDFS.get(cid, []),
        })
        for h in hits:
            c['years'].add(h.get('year', '?'))
            c['hit_types'].add(h['hit_type'])
            c['hit_count'] += 1
            c['hits_by_type'][h['hit_type']] = c['hits_by_type'].get(h['hit_type'], 0) + 1

    for key, row in ALL_SCORES.items():
        cid = row['company_id']
        if cid in companies:
            companies[cid]['name'] = row.get('company_name', companies[cid]['name'])

    # Jahres-Scores für Trend-Chart sammeln
    yearly_scores = {}
    for key, row in ALL_SCORES.items():
        cid = row['company_id']
        y = row.get('year', '?')
        if y != '?' and y != 'unknown':
            yearly_scores.setdefault(cid, []).append({'year': y, 'score': int(row['score'])})
    for cid in yearly_scores:
        yearly_scores[cid].sort(key=lambda x: x['year'])

    SCORE_WEIGHTS = {'carve_out': 3, 'loss_stress': 3, 'external_revenue': 2, 'biz_services': 1}

    result = []
    for cid, c in companies.items():
        best_year = max(c['years']) if c['years'] else '?'
        sk = f"{cid}_{best_year}"
        score = int(ALL_SCORES[sk]['score']) if sk in ALL_SCORES else min(10, len(c['hit_types'])*2 + min(c['hit_count']//5, 4))

        breakdown = []
        for ht, cnt in sorted(c['hits_by_type'].items(), key=lambda x: -SCORE_WEIGHTS.get(x[0], 0)):
            w = SCORE_WEIGHTS.get(ht, 0)
            label = HIT_TYPE_LABELS.get(ht, ht)
            breakdown.append({'type': ht, 'label': label, 'count': cnt, 'weight': w})

        result.append({
            'company_id': cid, 'name': c['name'], 'year': best_year,
            'score': score, 'hit_types': sorted(c['hit_types']),
            'hit_count': c['hit_count'], 'pdfs': c['pdfs'],
            'score_breakdown': breakdown,
            'yearly_scores': yearly_scores.get(cid, []),
        })
    result.sort(key=lambda x: x['score'], reverse=True)
    return result

def api_evidence(company_id, max_per_type=5):
    by_type = {}
    for h in ALL_HITS.get(company_id, []):
        t = h['hit_type']
        lst = by_type.setdefault(t, [])
        if len(lst) < max_per_type:
            src = h.get('source_file', '?')
            year = h.get('year', '?')
            lst.append({
                'keyword': h['keyword'], 'snippet': h['snippet'][:500],
                'source_file': src, 'year': year,
                'pdf_url': _txt_to_pdf_url(company_id, year, src),
            })
    return by_type

def api_relevance(company_id):
    """AI-basierte Relevanzpruefung: Filtert false positives aus den Signalen."""
    evidence = api_evidence(company_id, max_per_type=4)
    if not evidence:
        return {'adjusted_score': 0, 'signals': [], 'false_positives': 0}

    items_for_ai = []
    for hit_type, items in evidence.items():
        label = HIT_TYPE_LABELS.get(hit_type, hit_type)
        for i, item in enumerate(items):
            items_for_ai.append({
                'id': f"{hit_type}_{i}",
                'type': label, 'keyword': item['keyword'],
                'snippet': item['snippet'][:400],
            })

    prompt_items = '\n'.join(
        f"[{it['id']}] Typ: {it['type']} | Keyword: \"{it['keyword']}\" | "
        f"Zitat: \"{it['snippet']}\""
        for it in items_for_ai
    )

    resp = openai_c.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content':
             'Du bist ein M&A-Analyst. Bewerte fuer jedes Signal ob es ein ECHTES Distressed-Signal ist '
             '(z.B. tatsaechlicher Verkauf von Geschaeftsbereichen, echte Verluste, reale Restrukturierung) '
             'oder ein FALSE POSITIVE (z.B. rein buchhalterische Erwaehnung, Accounting-Standards, '
             'regulaere Geschaeftsberichte ohne echtes Stress-Signal).\n'
             'Antworte als JSON-Array: [{"id":"...", "relevant": true/false, "reason":"kurze Begruendung"}].\n'
             'Nur JSON, kein Markdown.'},
            {'role': 'user', 'content': f'Signale:\n\n{prompt_items}'}
        ],
        temperature=0.1, max_tokens=1500,
    )

    import re as _re
    raw = resp.choices[0].message.content.strip()
    # Extract JSON from potential markdown code blocks
    m = _re.search(r'\[.*\]', raw, _re.DOTALL)
    try:
        results = json.loads(m.group() if m else raw)
    except:
        results = []

    relevance_map = {r['id']: r for r in results if isinstance(r, dict)}
    fp_count = sum(1 for r in results if isinstance(r, dict) and not r.get('relevant', True))
    real_count = len(results) - fp_count

    signals = []
    for it in items_for_ai:
        r = relevance_map.get(it['id'], {})
        signals.append({
            'id': it['id'], 'type': it['type'], 'keyword': it['keyword'],
            'relevant': r.get('relevant', True),
            'reason': r.get('reason', ''),
            'snippet': it['snippet'][:200],
        })

    # Adjusted score: reduce for false positives
    orig_score = 0
    for key, row in ALL_SCORES.items():
        if row['company_id'] == company_id:
            try: orig_score = max(orig_score, int(row['score']))
            except: pass
    penalty = min(fp_count, 4)
    adjusted = max(1, orig_score - penalty)

    return {
        'original_score': orig_score, 'adjusted_score': adjusted,
        'total_signals': len(results), 'real_signals': real_count,
        'false_positives': fp_count, 'signals': signals,
    }

def api_report(company_id):
    evidence = api_evidence(company_id, max_per_type=3)
    if not evidence:
        return {'report': 'Keine Distressed-Signale gefunden.', 'sources': []}

    quotes = []
    sources = []
    for hit_type, items in evidence.items():
        label = HIT_TYPE_LABELS.get(hit_type, hit_type)
        for item in items:
            quotes.append(
                f"[{label}] Keyword: \"{item['keyword']}\" | "
                f"Quelle: {item['source_file']} ({item['year']})\n"
                f"Zitat: \"{item['snippet']}\""
            )
            sources.append({
                'type': label, 'keyword': item['keyword'],
                'file': item['source_file'], 'year': item['year'],
                'excerpt': item['snippet'][:250],
                'pdf_url': item.get('pdf_url'),
            })

    name = company_id.replace('_', ' ').title()
    for row in ALL_SCORES.values():
        if row['company_id'] == company_id:
            name = row.get('company_name', name)
            break

    resp = openai_c.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content':
             'Du bist ein M&A-Analyst. Du erstellst Berichte ausschliesslich auf Basis '
             'der gelieferten Originalzitate. Du halluzinierst NICHT. Jede Aussage wird '
             'mit der exakten Quelle [Datei, Jahr] belegt. Antworte auf Deutsch.'},
            {'role': 'user', 'content':
             f'Erstelle einen strukturierten Analysebericht ueber Distressed-Signale bei {name}.\n\n'
             f'REGELN:\n'
             f'- Zitiere NUR die unten stehenden Textpassagen. Erfinde NICHTS dazu.\n'
             f'- Jede Aussage MUSS mit [Datei, Jahr] belegt sein.\n'
             f'- Struktur: 1) Executive Summary  2) Identifizierte Signale  3) Bewertung\n'
             f'- Wenn unklar, sage das ehrlich.\n\n'
             f'ORIGINALE TEXTPASSAGEN:\n\n' + '\n\n'.join(quotes)}
        ],
        temperature=0.15, max_tokens=2000,
    )
    return {'report': resp.choices[0].message.content, 'sources': sources}

def api_chat(message):
    results = coll.query(query_texts=[message], n_results=8)
    parts, sources = [], []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        cid  = meta.get('company_id', '?')
        year = meta.get('year', '?')
        src  = meta.get('source_file', '?')
        parts.append(f"[{cid}, {year}, {src}]: {doc[:600]}")
        pdf_url = _txt_to_pdf_url(cid, year, src) if src != '?' else None
        sources.append({'company': cid, 'year': year, 'file': src,
                        'excerpt': doc[:200], 'pdf_url': pdf_url})

    resp = openai_c.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content':
             'Du bist ein M&A-Analyst. Antworte auf Deutsch. '
             'Zitiere NUR die gelieferten Textpassagen. '
             'Belege jede Aussage mit [Unternehmen, Jahr, Datei]. '
             'Halluziniere NICHT.'},
            {'role': 'user', 'content':
             f'Originaltexte:\n\n' + '\n\n'.join(parts) +
             f'\n\nFrage: {message}\n\nAntworte praezise mit Quellenangaben.'}
        ],
        temperature=0.2, max_tokens=1200,
    )
    return {'answer': resp.choices[0].message.content, 'sources': sources}

def api_stats():
    total_companies = len(ALL_HITS)
    total_pdfs = sum(len(v) for v in ALL_PDFS.values())
    total_hits = sum(len(v) for v in ALL_HITS.values())
    total_chunks = coll.count()
    scores = []
    for row in ALL_SCORES.values():
        try: scores.append(int(row['score']))
        except: pass
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    return {
        'companies': total_companies, 'pdfs': total_pdfs,
        'signals': total_hits, 'chunks': total_chunks,
        'avg_score': avg_score,
    }

def api_upload_csv():
    """Beispiel: CSV zum Hochladen vorbereitet."""
    return {'message': 'Use POST /api/upload/csv with CSV content in body'}

def api_recognize_company(company_name):
    """Erkenne Firma anhand ihres Namens mittels AI."""
    try:
        from pipeline_queue import recognize_company_by_name
        company_data = recognize_company_by_name(company_name)
        # Starte sofort die Pipeline
        task_id = queue.add_task('add_company_manual', company_data)
        return {
            'task_id': task_id,
            'company': company_data,
            'status': 'queued',
            'message': f'Added {company_data["company_name"]} to processing queue'
        }
    except Exception as e:
        return {'error': f'Failed to recognize company: {str(e)}'}

def api_add_company(data):
    """Füge Einzelunternehmen zur Queue hinzu (manuelle Eingabe)."""
    required_fields = ['company_id', 'company_name', 'country', 'website']
    if not all(k in data for k in required_fields):
        return {'error': f'Missing required fields. Need: {", ".join(required_fields)}'}
    
    task_id = queue.add_task('add_company_manual', data)
    return {'task_id': task_id, 'status': 'queued'}

def api_upload_csv_file(csv_content):
    """Verarbeite hochgeladene CSV-Datei."""
    try:
        # CSV-Inhalt validieren
        lines = csv_content.strip().split('\n')
        if not lines:
            return {'error': 'Empty CSV file'}
        
        # Task zur Queue hinzufügen
        task_id = queue.add_task('add_company_csv', csv_content)
        return {'task_id': task_id, 'status': 'queued', 'message': 'CSV added to processing queue'}
    except Exception as e:
        return {'error': f'CSV parsing error: {str(e)}'}

def api_task_status(task_id):
    """Hole Task-Status."""
    status = queue.get_task(task_id)
    if not status:
        return {'error': 'Task not found'}
    return status

def api_task_list():
    """Liste letzte Tasks."""
    return {'tasks': queue.list_tasks()}

def api_task_cancel(task_id):
    """Breche Task ab."""
    if queue.cancel_task(task_id):
        return {'message': 'Task cancelled'}
    return {'error': 'Task not found or already completed'}


# ── HTTP Handler ─────────────────────────────────────────────────────────────

class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path
        qs   = parse_qs(urlparse(self.path).query)

        if path == '/api/companies':
            return self._json(api_companies())
        if path == '/api/stats':
            return self._json(api_stats())
        if path == '/api/evidence':
            return self._json(api_evidence(qs.get('company', [''])[0]))
        if path == '/api/relevance':
            return self._json(api_relevance(qs.get('company', [''])[0]))
        if path == '/api/report':
            return self._json(api_report(qs.get('company', [''])[0]))
        
        # ── Task Management Endpoints ────
        if path == '/api/tasks':
            return self._json(api_task_list())
        if path.startswith('/api/tasks/'):
            task_id = path[len('/api/tasks/'):]
            return self._json(api_task_status(task_id))

        # PDF serving
        if path.startswith('/pdfs/'):
            pdf_path = os.path.join(DOWNLOADS_DIR, path[6:])
            if os.path.isfile(pdf_path) and pdf_path.endswith('.pdf'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition',
                                 f'inline; filename="{os.path.basename(pdf_path)}"')
                self.send_header('Content-Length', str(os.path.getsize(pdf_path)))
                self.end_headers()
                with open(pdf_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404)
            return

        # Static files
        if path == '/':
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length).decode('utf-8')
        except:
            return self.send_error(400)

        if path == '/api/chat':
            try:
                body = json.loads(body_data)
                return self._json(api_chat(body.get('message', '')))
            except:
                return self.send_error(400)
        
        # ── Company Upload Endpoints ────
        elif path == '/api/upload/csv':
            result = api_upload_csv_file(body_data)
            return self._json(result)
        
        elif path == '/api/recognize-company':
            try:
                body = json.loads(body_data)
                company_name = body.get('company_name', '').strip()
                if not company_name:
                    return self._json({'error': 'Missing company_name'})
                result = api_recognize_company(company_name)
                return self._json(result)
            except Exception as e:
                return self._json({'error': str(e)})
        
        elif path == '/api/add-company':
            try:
                body = json.loads(body_data)
                result = api_add_company(body)
                return self._json(result)
            except Exception as e:
                return self._json({'error': str(e)})
        
        elif path.startswith('/api/tasks/') and path.endswith('/cancel'):
            task_id = path[len('/api/tasks/'):-len('/cancel')]
            result = api_task_cancel(task_id)
            return self._json(result)
        
        self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, fmt, *args):
        if '/api/' in (args[0] if args else ''):
            sys.stderr.write(f"  API  {args[0]}\n")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"""
╔═══════════════════════════════════════════════════════╗
║       Deal Radar – M&A Intelligence Platform          ║
╚═══════════════════════════════════════════════════════╝

  🌐  http://localhost:{port}
  📚  ChromaDB:  {coll.count():,} Chunks
  📄  Reports:   {sum(len(v) for v in ALL_PDFS.values())} PDFs
  🔍  Signale:   {sum(len(v) for v in ALL_HITS.values())} Treffer
  🤖  AI Chat:   OpenAI gpt-4o-mini
  Ctrl+C zum Beenden
""")
    HTTPServer(('', port), Handler).serve_forever()
