import pandas as pd
import os
import json
import logging

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HITS_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'report_hits.jsonl')
COMPANIES_FILE = os.path.join(BASE_DIR, 'data', 'companies_enriched.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'data', 'outputs', 'deal_radar.csv')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'score_export.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Scoring Regeln
SCORES = {
    'carve_out': 3,
    'loss_stress': 3,
    'biz_services': 1,
    'external_revenue': 2
}

NEGATIVE_TERMS = [
    'shared service center', 'internal services', 'intra-group', 'intercompany', 'for group companies'
]

def calculate_score(group):
    """Berechnet den Score für eine Gruppe (Company + Year)."""
    score = 0
    reasons = set()
    snippets = []
    
    # Positive Scores
    for hit_type in group['hit_type'].unique():
        if hit_type in SCORES:
            score += SCORES[hit_type]
            reasons.add(hit_type)
            
    # Check Negative Terms in Snippets (einfache Logik)
    # Wenn "shared service center" oft vorkommt, Score reduzieren
    all_snippets = " ".join(group['snippet'].tolist()).lower()
    for term in NEGATIVE_TERMS:
        if term in all_snippets:
            score -= 3
            reasons.add(f"negative_signal_found")
            break # Einmal Abzug reicht
            
    # Cap score 0-10
    score = max(0, min(10, score))
    
    # Beste Snippets auswählen (z.B. eines pro Kategorie)
    unique_snippets = group.drop_duplicates(subset=['hit_type']).head(3)['snippet'].tolist()
    
    return pd.Series({
        'score': score,
        'top_reasons': ", ".join(reasons),
        'snippet_examples': " | ".join([s[:100] + "..." for s in unique_snippets]),
        'source_files': ", ".join(group['source_file'].unique())
    })

def main():
    if not os.path.exists(HITS_FILE):
        print("Keine Hits gefunden. Bitte erst 05_scan_reports.py ausführen.")
        return
        
    print("Lade Daten...")
    
    # 1. Hits laden
    hits_data = []
    with open(HITS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            hits_data.append(json.loads(line))
            
    if not hits_data:
        print("Keine Hits zum Auswerten.")
        return
        
    df_hits = pd.DataFrame(hits_data)
    
    # 2. Companies laden (für den Namen)
    df_companies = pd.read_csv(COMPANIES_FILE, sep=';')
    company_map = dict(zip(df_companies['company_id'], df_companies['company_name']))
    
    print("Berechne Scores...")
    
    # Gruppieren nach Company + Year
    results = df_hits.groupby(['company_id', 'year'], group_keys=False).apply(calculate_score).reset_index()
    
    # Company Name mappen
    results['company_name'] = results['company_id'].map(company_map)
    
    # Sortieren nach Score
    results = results.sort_values(by='score', ascending=False)
    
    # Spalten ordnen
    cols = ['company_id', 'company_name', 'year', 'score', 'top_reasons', 'snippet_examples', 'source_files']
    results = results[cols]
    
    # Speichern
    results.to_csv(OUTPUT_CSV, sep=';', index=False, encoding='utf-8-sig') # utf-8-sig für Excel
    
    print("-" * 50)
    print("Top 10 Kandidaten:")
    print(results[['company_name', 'score', 'top_reasons']].head(10).to_string(index=False))
    print("-" * 50)
    print(f"Export gespeichert: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
