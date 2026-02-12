import csv
import os
import logging
import requests
from urllib.parse import urljoin
from tqdm import tqdm

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'companies.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'companies_enriched.csv')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'discover_ir.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Heuristische Pfade, die geprüft werden, wenn ir_url leer ist
COMMON_IR_PATHS = [
    '/investors',
    '/investor-relations',
    '/investors/financial-reports',
    '/investors/results-center',
    '/investors/results',
    '/finance',
    '/en/investors',
    '/en/investor-relations',
    '/group/en/investors',
    '/about-us/investor-relations',
    '/corporate/investor-relations',
    '/about/investors',
]

# Keywords, die auf eine echte IR-Seite hindeuten
IR_KEYWORDS = [
    'investor relations', 'annual report', 'financial report',
    'financial results', 'financial statements', 'annual results',
    'geschäftsbericht', 'jahresbericht', 'shareholders'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
}

def check_url(url):
    """Prüft, ob eine URL existiert und nach IR-Seite aussieht."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            content = response.text.lower()
            # Prüfe ob mindestens eines der IR-Keywords vorkommt
            for kw in IR_KEYWORDS:
                if kw in content:
                    logger.info(f"  [+] IR-Seite gefunden: {response.url} (matched: '{kw}')")
                    return response.url
    except requests.exceptions.Timeout:
        logger.debug(f"  Timeout: {url}")
    except requests.exceptions.ConnectionError:
        logger.debug(f"  Connection Error: {url}")
    except Exception as e:
        logger.debug(f"  Error checking {url}: {e}")
    return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Fehler: Datei {INPUT_FILE} nicht gefunden.")
        return

    companies = []
    
    # Datei einlesen
    with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            companies.append(row)

    print(f"Starte IR-Discovery für {len(companies)} Unternehmen...")
    logger.info(f"Starte IR-Discovery für {len(companies)} Unternehmen")
    print("-" * 50)

    enriched_count = 0

    for company in tqdm(companies):
        name = company.get('company_name')
        base_url = company.get('website')
        current_ir = company.get('ir_url', '').strip()

        # Wenn URL fehlt oder leer ist
        if not current_ir and base_url:
            logger.info(f"Suche IR-Seite für: {name} ({base_url})")
            
            # Normalisiere Base URL (kein trailing slash)
            base_url = base_url.rstrip('/')
            
            found_url = None
            for path in COMMON_IR_PATHS:
                test_url = base_url + path
                real_url = check_url(test_url)
                if real_url:
                    found_url = real_url
                    break
            
            if found_url:
                company['ir_url'] = found_url
                enriched_count += 1
            else:
                logger.warning(f"Keine IR-Seite gefunden für: {name}")
        elif current_ir:
            logger.info(f"IR-URL vorhanden für {name}: {current_ir}")

    # Speichern
    fieldnames = ['company_id', 'company_name', 'country', 'website', 'ir_url']
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(companies)

    print("-" * 50)
    print(f"Fertig. {enriched_count} fehlende URLs ergänzt.")
    print(f"Ergebnis gespeichert in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
