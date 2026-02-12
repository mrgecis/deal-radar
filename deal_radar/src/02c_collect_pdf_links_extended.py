"""
02c_collect_pdf_links_extended.py – Sammelt neueste Reports für NEUE Firmen (nicht 2024-only).
"""

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
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'pdf_links_extended.csv')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

# Nur neue Firmen
TARGET_COMPANIES = [
    'canon_deutschland', 't_systems', 'mobotix', 'konica_minolta', 
    'accenture', 'atos_origin', 'hexaware', 'ltts', 'apptio'
]

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'collect_pdf_links_extended.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PRIORITY_KEYWORDS = [
    'annual report', 'jahresbericht', 'universal registration document',
    'integrated report', 'financial report', 'financial statements',
    'geschäftsbericht', 'geschaeftsbericht', 'results presentation',
    'form 20-f', '10-k', 'full year results', 'half year results',
    'annual results', 'annual review'
]

ANNUAL_KEYWORDS = [
    'annual report', 'jahresbericht', 'universal registration document',
    'integrated report', 'geschäftsbericht', 'geschaeftsbericht',
    'full year', 'form 20-f', '10-k', 'annual review', 'annual results',
    'fy', 'urd'
]

PARTIAL_KEYWORDS = [
    'half year', 'half-year', 'q1', 'q2', 'q3', 'q4', 'quarterly',
    'interim', 'halbjahr', 'hyfr', 'semestriel', 'h1', 'h2',
    'us gaap', 'us_gaap'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
}


def guess_year(text_or_url):
    matches = re.findall(r'20[1-2][0-9]', text_or_url)
    if matches:
        return max(matches)
    return "unknown"


def looks_like_pdf_url(url):
    parsed = urlparse(url.lower())
    return parsed.path.endswith('.pdf')


def is_relevant_pdf(link_text, link_url):
    if not looks_like_pdf_url(link_url):
        return False
    combined = (link_text + " " + unquote(link_url)).lower()
    for kw in PRIORITY_KEYWORDS:
        if kw in combined:
            return True
    return False


def is_annual(pdf):
    combined = (pdf['pdf_title'] + " " + unquote(pdf['pdf_url'])).lower()
    for kw in PARTIAL_KEYWORDS:
        if kw in combined:
            return False
    return True


def scrape_page_static(url):
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
    links = []
    try:
        with sync_playwright() as p:
            browser = p.webkit.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=30000, wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
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
                pass
            
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
        logger.warning(f"Playwright Error: {e}")
    return links


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    companies = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        companies = [row for row in reader if row['company_id'] in TARGET_COMPANIES]

    found_pdfs = []
    
    print(f"Suche neueste Reports für {len(companies)} neue Unternehmen...")

    for company in tqdm(companies):
        c_name = company['company_name']
        ir_url = company.get('ir_url', '').strip()
        
        if not ir_url:
            logger.warning(f"Keine IR-URL für {c_name}, überspringe.")
            continue
        
        logger.info(f"Scrape: {c_name} ({ir_url})")
        
        raw_links, soup = scrape_page_static(ir_url)
        if len(raw_links) < 5:
            logger.info(f"  Wenig Links, nutze Playwright für {c_name}...")
            raw_links = get_links_dynamic(ir_url)

        count = 0
        current_pdfs = set()

        for text, href in raw_links:
            full_url = urljoin(ir_url, href)
            if full_url in current_pdfs:
                continue

            if is_relevant_pdf(text, full_url):
                year = guess_year(text + " " + unquote(full_url))
                if year == 'unknown':
                    continue
                
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

    # Nur 1 pro Firma (neuester)
    from collections import defaultdict
    
    def is_strongly_annual(pdf):
        combined = (pdf['pdf_title'] + " " + unquote(pdf['pdf_url'])).lower()
        for kw in ANNUAL_KEYWORDS:
            if kw in combined:
                return True
        return False
    
    by_company = defaultdict(list)
    for pdf in found_pdfs:
        if pdf['year_guess'] != 'unknown':
            by_company[pdf['company_id']].append(pdf)
    
    best_per_company = {}
    for cid, pdfs in by_company.items():
        annuals = [p for p in pdfs if is_annual(p)]
        strong_annuals = [p for p in annuals if is_strongly_annual(p)]
        candidates = strong_annuals if strong_annuals else (annuals if annuals else pdfs)
        best = max(candidates, key=lambda p: p['year_guess'])
        best_per_company[cid] = best
        logger.info(f"  Bester Report für {cid}: {best['year_guess']} – {best['pdf_title'][:80]}")

    filtered_pdfs = list(best_per_company.values())
    filtered_pdfs.sort(key=lambda x: x['company_id'])

    keys = ['company_id', 'company_name', 'source_page', 'pdf_url', 'pdf_title', 'year_guess']
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=';')
        writer.writeheader()
        writer.writerows(filtered_pdfs)

    print(f"Fertig. {len(filtered_pdfs)} neueste Reports gefunden.")
    print(f"Gespeichert in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
