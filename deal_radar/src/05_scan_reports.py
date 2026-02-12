import os
import json
import logging
from glob import glob
from tqdm import tqdm

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_DIR = os.path.join(BASE_DIR, 'data', 'extracted_text')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'report_hits.jsonl')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

MAX_HITS_PER_KEYWORD = 3  # Begrenze Treffer pro Keyword pro Datei

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'scan_reports.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Keyword Definitionen
# Nur spezifische, mehrwort-Begriffe verwenden um False Positives zu minimieren
KEYWORDS = {
    'carve_out': [
        'divestment', 'divestiture', 'disposal of', 'strategic review',
        'portfolio simplification', 'non-core', 'carve-out', 'carve out',
        'discontinued operations', 'planned separation', 'divest'
    ],
    'loss_stress': [
        'loss-making', 'operating loss', 'negative margin', 'margin pressure',
        'impairment charge', 'onerous contract', 'turnaround plan',
        'underperforming', 'profit warning', 'restructuring charge'
    ],
    'biz_services': [
        'managed services', 'it services', 'infrastructure services',
        'application support', 'helpdesk', 'cloud operations',
        'outsourcing', 'business process outsourcing',
        'customer experience services', 'contact center services',
        'technical operations services'
    ],
    'external_revenue': [
        'external customers', 'third-party revenue', 'client contracts',
        'revenues from customers', 'commercial customers', 'market-facing',
        'third party customers', 'external revenue'
    ]
}

def get_snippet(text, index, window=300):
    start = max(0, index - window)
    end = min(len(text), index + window)
    return text[start:end].replace('\n', ' ').strip()

def scan_text(text, company_id, year, filename):
    hits = []
    text_lower = text.lower()
    
    for category, terms in KEYWORDS.items():
        for term in terms:
            hit_count = 0
            start_index = 0
            while hit_count < MAX_HITS_PER_KEYWORD:
                idx = text_lower.find(term, start_index)
                if idx == -1:
                    break
                
                # Snippet extrahieren
                snippet = get_snippet(text, idx)
                
                hits.append({
                    'company_id': company_id,
                    'year': year,
                    'source_file': filename,
                    'hit_type': category,
                    'keyword': term,
                    'snippet': snippet
                })
                
                start_index = idx + len(term)
                hit_count += 1
                
    return hits

def main():
    # Alle Textfiles finden
    txt_files = glob(os.path.join(EXTRACT_DIR, '**', '*.txt'), recursive=True)
    
    if not txt_files:
        print("Keine Textdateien gefunden. Bitte erst 04_extract_text.py ausführen.")
        return
    
    print(f"Scanne {len(txt_files)} Berichte nach Signalen...")
    
    # Output vorbereiten (JSONL append mode)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Datei leeren vor Neustart
    with open(OUTPUT_FILE, 'w') as f:
        pass
        
    all_hits = 0
    
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f_out:
        for txt_path in tqdm(txt_files):
            # Metadaten aus Pfad (relativ zu EXTRACT_DIR)
            rel_path = os.path.relpath(txt_path, EXTRACT_DIR)
            parts = rel_path.split(os.sep)
            
            if len(parts) >= 3:
                company_id = parts[0]
                year = parts[1]
                filename = parts[-1]
            else:
                logger.warning(f"Unerwarteter Pfad: {txt_path}")
                continue
            
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                hits = scan_text(content, company_id, year, filename)
                
                for hit in hits:
                    f_out.write(json.dumps(hit) + '\n')
                    all_hits += 1
                    
            except Exception as e:
                print(f"Fehler beim Lesen von {txt_path}: {e}")

    print(f"Fertig. {all_hits} Treffer gefunden.")
    print(f"Gespeichert in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
