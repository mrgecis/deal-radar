import csv
import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlparse
from tqdm import tqdm
from playwright.sync_api import sync_playwright

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'companies_enriched.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'pdf_links.csv')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'collect_pdf_links.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Keywords für Priorisierung (Lowercase)
PRIORITY_KEYWORDS = [
    'annual report', 'jahresbericht', 'universal registration document',
    'integrated report', 'financial report', 'financial statements',
    'geschäftsbericht', 'geschaeftsbericht', 'results presentation',
    'form 20-f', '10-k', 'full year results', 'half year results',
    'annual results', 'annual review'
]

# Annual-Report-Keywords (für Priorisierung über Halbjahresberichte)
ANNUAL_KEYWORDS = [
    'annual report', 'jahresbericht', 'universal registration document',
    'integrated report', 'geschäftsbericht', 'geschaeftsbericht',
    'full year', 'form 20-f', '10-k', 'annual review', 'annual results',
    'fy', 'urd'
]

# Keywords die auf Halbjahres-/Quartalsberichte hinweisen (weniger relevant)
PARTIAL_KEYWORDS = [
    'half year', 'half-year', 'q1', 'q2', 'q3', 'q4', 'quarterly',
    'interim', 'halbjahr', 'hyfr', 'semestriel', 'h1', 'h2',
    'us gaap', 'us_gaap'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
}

def guess_year(text_or_url):
    """Extrahiert eine 4-stellige Jahreszahl (2018-2026). Bevorzugt neuere Jahre."""
    matches = re.findall(r'20[1-2][0-9]', text_or_url)
    if matches:
        # Neuestes Jahr bevorzugen
        return max(matches)
    return "unknown"

def looks_like_pdf_url(url):
    """Prüft ob URL auf ein PDF zeigt (auch mit Query-Strings)."""
    parsed = urlparse(url.lower())
    path = parsed.path
    return path.endswith('.pdf')

def is_relevant_pdf(link_text, link_url):
    """Entscheidet, ob ein PDF relevant klingt."""
    if not looks_like_pdf_url(link_url):
        return False
    
    combined = (link_text + " " + unquote(link_url)).lower()
    
    for kw in PRIORITY_KEYWORDS:
        if kw in combined:
            return True
    
    return False

def get_links_static(url):
    """Versuch 1: Schnelles Scrapen mit Requests."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            logger.warning(f"  HTTP {r.status_code} für {url}")
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            links.append((a.get_text(strip=True), a['href']))
        return links
    except Exception as e:
        logger.warning(f"  Static scrape error: {e}")
        return []

def get_sub_pages(url, soup):
    """Findet Sub-Seiten der IR-Seite die weitere PDFs enthalten könnten."""
    sub_urls = []
    base_domain = urlparse(url).netloc
    sub_keywords = ['report', 'download', 'publication', 'document', 'result', 'financial', 'annual']
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        full_url = urljoin(url, href)
        
        # Gleiche Domain, kein PDF, klingt nach Unterseite mit Reports
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain and not looks_like_pdf_url(full_url):
            combined = (text + " " + full_url).lower()
            for kw in sub_keywords:
                if kw in combined:
                    sub_urls.append(full_url)
                    break
    
    # Nur die ersten 5 Sub-Seiten, um nicht zu aggressiv zu crawlen
    return list(set(sub_urls))[:5]

def scrape_page_static(url):
    """Scrapt eine einzelne Seite und gibt Links + BeautifulSoup zurück."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return [], None
        soup = BeautifulSoup(r.text, 'html.parser')
        links = [(a.get_text(strip=True), a['href']) for a in soup.find_all('a', href=True)]
        return links, soup
    except Exception:
        return [], None

def get_links_dynamic(url):
    """Versuch 2: Playwright (für JavaScript-lastige Seiten)."""
    links = []
    try:
        with sync_playwright() as p:
            # Nutzt WebKit (Safari Engine) für maximale Kompatibilität auf Mac
            browser = p.webkit.launch(headless=True) 
            page = browser.new_page()
            try:
                page.goto(url, timeout=30000, wait_until='domcontentloaded')
                # Warte auf dynamischen Content + scrolle
                page.wait_for_timeout(3000)
                
                # Scroll down um lazy-loaded content zu triggern
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                # Klicke auf "Show more" / "Load more" Buttons falls vorhanden
                for selector in ['button:has-text("more")', 'a:has-text("more")', 
                                 'button:has-text("All")', 'button:has-text("alle")']:
                    try:
                        btn = page.query_selector(selector)
                        if btn and btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(2000)
                    except:
                        pass
                        
            except Exception:
                pass # Timeout oder Fehler
            
            # Links extrahieren - auch aus iframes
            elements = page.query_selector_all('a[href]')
            for el in elements:
                try:
                    txt = el.inner_text()
                    href = el.get_attribute('href')
                    if href:
                        links.append((txt, href))
                except:
                    continue
            browser.close()
    except Exception as e:
        logger.warning(f"    Playwright Error: {e}")
    return links

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found. Please run 01_discover_ir.py first.")
        return

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    companies = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        companies = list(reader)

    found_pdfs = []
    
    print(f"Suche PDF-Links für {len(companies)} Unternehmen...")

    for company in tqdm(companies):
        c_name = company['company_name']
        ir_url = company.get('ir_url', '').strip()
        
        if not ir_url:
            logger.warning(f"Keine IR-URL für {c_name}, überspringe.")
            continue
        
        logger.info(f"Scrape: {c_name} ({ir_url})")
            
        # 1. Hauptseite statisch scrapen
        raw_links, soup = scrape_page_static(ir_url)
        
        # 2. Sub-Seiten crawlen (eine Ebene tief)
        if soup:
            sub_pages = get_sub_pages(ir_url, soup)
            for sub_url in sub_pages:
                sub_links, _ = scrape_page_static(sub_url)
                raw_links.extend(sub_links)
                logger.debug(f"  Sub-Seite: {sub_url} → {len(sub_links)} Links")
        
        # 3. Wenn immer noch wenig, Playwright Fallback
        if len(raw_links) < 5:
            logger.info(f"  Wenig Links, nutze Playwright für {c_name}...")
            raw_links = get_links_dynamic(ir_url)

        # 3. Filtern und Aufbereiten
        count = 0
        current_pdfs = set() # Duplikate vermeiden pro Company

        for text, href in raw_links:
            full_url = urljoin(ir_url, href)
            
            if full_url in current_pdfs:
                continue

            if is_relevant_pdf(text, full_url):
                year = guess_year(text + " " + unquote(full_url))
                
                found_pdfs.append({
                    'company_id': company['company_id'],
                    'company_name': c_name,
                    'source_page': ir_url,
                    'pdf_url': full_url,
                    'pdf_title': text.replace(';', ',').replace('\n', ' ').strip()[:200],
                    'year_guess': year
                })
                current_pdfs.add(full_url)
                count += 1
        
        logger.info(f"  → {count} relevante PDFs gefunden bei {c_name}")

    # --- NUR DEN NEUESTEN JAHRESABSCHLUSS PRO FIRMA BEHALTEN ---
    from collections import defaultdict
    
    def is_annual(pdf):
        """Prüft ob PDF ein Jahresabschluss ist (kein Quartal/Halbjahr)."""
        combined = (pdf['pdf_title'] + " " + unquote(pdf['pdf_url'])).lower()
        # Wenn explizit partial → nicht annual
        for kw in PARTIAL_KEYWORDS:
            if kw in combined:
                return False
        return True
    
    def is_strongly_annual(pdf):
        """Prüft ob PDF explizit ein Jahresbericht ist."""
        combined = (pdf['pdf_title'] + " " + unquote(pdf['pdf_url'])).lower()
        for kw in ANNUAL_KEYWORDS:
            if kw in combined:
                return True
        return False
    
    # Pro Firma gruppieren
    by_company = defaultdict(list)
    for pdf in found_pdfs:
        if pdf['year_guess'] != 'unknown':
            by_company[pdf['company_id']].append(pdf)
    
    best_per_company = {}
    for cid, pdfs in by_company.items():
        # Schritt 1: Bevorzuge Jahresberichte
        annuals = [p for p in pdfs if is_annual(p)]
        strong_annuals = [p for p in annuals if is_strongly_annual(p)]
        
        candidates = strong_annuals if strong_annuals else (annuals if annuals else pdfs)
        
        # Schritt 2: Neuestes Jahr
        best = max(candidates, key=lambda p: p['year_guess'])
        best_per_company[cid] = best
        logger.info(f"  Bester Report für {cid}: {best['year_guess']} – {best['pdf_title'][:80]}")

    filtered_pdfs = list(best_per_company.values())
    filtered_pdfs.sort(key=lambda x: x['company_id'])
    
    logger.info(f"Filter: {len(found_pdfs)} PDFs → {len(filtered_pdfs)} (nur neuester Jahresabschluss pro Firma)")

    # Speichern
    keys = ['company_id', 'company_name', 'source_page', 'pdf_url', 'pdf_title', 'year_guess']
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=';')
        writer.writeheader()
        writer.writerows(filtered_pdfs)

    print(f"Fertig. {len(filtered_pdfs)} PDF-Links (neuester Report pro Firma) aus {len(found_pdfs)} Kandidaten.")
    print(f"Gespeichert in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
