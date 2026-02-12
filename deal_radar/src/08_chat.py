"""
08_chat.py – RAG-Chat über die indexierten Investorenberichte.

Nutzung:
  export OPENAI_API_KEY="sk-..."
  python src/08_chat.py

Features:
  - Natürliche Fragen an die Reports stellen
  - Relevante Textstellen werden per Similarity Search gefunden
  - OpenAI GPT beantwortet auf Basis der gefundenen Stellen
  - Filtert optional nach Company oder Jahr
  - Konversations-Kontext wird beibehalten

Beispiel-Fragen:
  > Welche Unternehmen planen Divestments?
  > Was sagt Atos über Restrukturierung in 2024?
  > Welche Firmen haben loss-making Segmente?
  > Zeige mir alle Carve-out-Signale bei CGI
"""

import os
import sys
import json
import logging
import chromadb
from openai import OpenAI

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')
COLLECTION_NAME = 'deal_radar_reports'

# Scoring-Daten laden für Kontext
HITS_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'report_hits.jsonl')
DEAL_RADAR_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'deal_radar.csv')

TOP_K = 10  # Anzahl relevanter Chunks pro Frage
MODEL = "gpt-4o-mini"  # Günstig und schnell; alternativ "gpt-4o" für bessere Qualität

SYSTEM_PROMPT = """Du bist ein Experte für M&A-Analyse und Carve-out-Opportunitäten im IT/Business-Services-Bereich.

Du analysierst Investorenberichte (Jahresberichte, Registration Documents, Financial Statements) 
von Unternehmen und hilfst dem Nutzer, Carve-out-fähige Geschäftsbereiche zu identifizieren.

Fokus:
- Business Services (IT Managed Services, BPO, Infrastructure Services) – EXTERNES Geschäft, nicht interne SSCs
- Zielgröße: 10–100 Mio EUR Umsatz
- Besonders relevant: loss-making Segmente, Restrukturierung, Strategic Review, Divestment-Signale

Regeln:
- Antworte auf Deutsch, es sei denn die Frage ist auf Englisch
- Zitiere relevante Textstellen mit Quelle (Firma, Jahr)
- Wenn du dir unsicher bist, sage es klar
- Gib konkrete, strukturierte Antworten (Tabellen, Bullet Points)
- Beziehe dich NUR auf die bereitgestellten Kontext-Informationen
"""


def load_deal_radar_summary():
    """Lädt eine Zusammenfassung der Scoring-Ergebnisse."""
    if not os.path.exists(DEAL_RADAR_FILE):
        return ""
    
    try:
        import pandas as pd
        df = pd.read_csv(DEAL_RADAR_FILE, sep=';')
        top = df.head(10)
        summary = "DEAL RADAR SCORING (Top-Kandidaten):\n"
        for _, row in top.iterrows():
            summary += f"  - {row.get('company_name', '?')} ({row.get('year', '?')}): Score {row.get('score', '?')} – {row.get('top_reasons', '')}\n"
        return summary
    except Exception:
        return ""


def search_chunks(collection, query, company_filter=None, year_filter=None, n_results=TOP_K):
    """Sucht relevante Chunks im Vektor-Index."""
    where_filter = None
    
    # Filter bauen
    conditions = []
    if company_filter:
        conditions.append({"company_id": {"$eq": company_filter}})
    if year_filter:
        conditions.append({"year": {"$eq": year_filter}})
    
    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter
    )
    
    return results


def format_context(results):
    """Formatiert die Suchergebnisse als Kontext für das LLM."""
    if not results or not results['documents'] or not results['documents'][0]:
        return "Keine relevanten Dokumente gefunden."
    
    context_parts = []
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        company = meta.get('company_id', '?')
        year = meta.get('year', '?')
        source = meta.get('source_file', '?')
        
        context_parts.append(
            f"--- Quelle {i+1}: {company} ({year}) [{source}] ---\n{doc}\n"
        )
    
    return "\n".join(context_parts)


def detect_filters(query):
    """Einfache Heuristik: Erkennt Company-/Jahres-Filter in der Frage."""
    import re
    
    company_filter = None
    year_filter = None
    
    # Bekannte Company-IDs
    known_companies = [
        'atos', 'cgi', 'deutsche_telekom', 'fujitsu', 'sap', 'siemens',
        'capgemini', 'bertelsmann', 'infosys', 'thales', 'wipro', 'tcs',
        'hcl', 'dxc', 'unisys', 'conduent', 'kyndryl', 'sopra_steria',
        'tietoevry', 'cancom', 'bechtle', 'computacenter', 'gft', 'datagroup'
    ]
    
    query_lower = query.lower()
    for cid in known_companies:
        # Match company ID or display name
        display_name = cid.replace('_', ' ')
        if cid in query_lower or display_name in query_lower:
            company_filter = cid
            break
    
    # Jahr erkennen
    year_match = re.search(r'20[1-2][0-9]', query)
    if year_match:
        year_filter = year_match.group(0)
    
    return company_filter, year_filter


def chat_loop():
    """Hauptschleife für den Chat."""
    # Check API Key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("=" * 60)
        print("FEHLER: OPENAI_API_KEY nicht gesetzt!")
        print()
        print("Setze den Key so:")
        print('  export OPENAI_API_KEY="sk-..."')
        print()
        print("Oder erstelle eine .env Datei im Projektroot:")
        print('  OPENAI_API_KEY=sk-...')
        print("=" * 60)
        
        # Versuche .env zu laden
        env_file = os.path.join(BASE_DIR, '.env')
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                        os.environ['OPENAI_API_KEY'] = api_key
                        print("API Key aus .env geladen.")
                        break
        
        if not api_key:
            return

    # ChromaDB laden
    print("Lade Vektor-Index...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        print("Index nicht gefunden. Bitte erst 07_build_index.py ausführen.")
        return
    
    doc_count = collection.count()
    print(f"Index geladen: {doc_count} Chunks verfügbar.")
    
    # Deal Radar Summary laden
    radar_summary = load_deal_radar_summary()
    
    # OpenAI Client
    openai_client = OpenAI()
    
    # Konversations-Historie
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    if radar_summary:
        messages.append({
            "role": "system", 
            "content": f"Hier ist eine Übersicht der aktuellen Scoring-Ergebnisse:\n{radar_summary}"
        })

    print()
    print("=" * 60)
    print("  DEAL RADAR – RAG Chat")
    print("  Stelle Fragen zu den Investorenberichten.")
    print()
    print("  Beispiele:")
    print("  > Welche Unternehmen planen Divestments?")
    print("  > Was sagt Atos über Restrukturierung?")
    print("  > Vergleiche die IT-Services von CGI und Fujitsu")
    print()
    print("  Befehle: /quit, /reset, /stats")
    print("=" * 60)
    print()

    while True:
        try:
            query = input("Du > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        
        if not query:
            continue
        
        if query.lower() in ['/quit', '/exit', '/q']:
            print("Bye!")
            break
        
        if query.lower() == '/reset':
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if radar_summary:
                messages.append({"role": "system", "content": f"Scoring-Übersicht:\n{radar_summary}"})
            print("Konversation zurückgesetzt.\n")
            continue
        
        if query.lower() == '/stats':
            print(f"  Index: {doc_count} Chunks")
            print(f"  Konversation: {len(messages)} Nachrichten")
            print(f"  Modell: {MODEL}")
            if radar_summary:
                print(f"\n{radar_summary}")
            print()
            continue

        # 1. Filter erkennen
        company_filter, year_filter = detect_filters(query)
        filter_info = ""
        if company_filter:
            filter_info += f" [Filter: {company_filter}]"
        if year_filter:
            filter_info += f" [Jahr: {year_filter}]"
        
        # 2. Relevante Chunks suchen
        results = search_chunks(collection, query, company_filter, year_filter)
        context = format_context(results)
        
        # 3. Prompt zusammenbauen
        augmented_query = f"""Frage des Nutzers: {query}
{filter_info}

Hier sind die relevantesten Textstellen aus den Investorenberichten:

{context}

Beantworte die Frage basierend auf diesen Informationen. Zitiere die Quellen (Firma, Jahr)."""

        messages.append({"role": "user", "content": augmented_query})
        
        # 4. LLM aufrufen
        try:
            response = openai_client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})
            
            print(f"\n🤖 {answer}\n")
            
        except Exception as e:
            print(f"\nFehler bei OpenAI-Aufruf: {e}\n")
            messages.pop()  # Fehlgeschlagene Frage entfernen


if __name__ == "__main__":
    chat_loop()
