"""
03_download_pdfs.py – Lädt PDFs herunter, extrahiert Text und indiziert in ChromaDB.

Alles in einem Schritt: Download → Extraktion → Vektor-Index.
"""

import csv
import os
import json
import requests
import hashlib
import time
import logging
from tqdm import tqdm
from pypdf import PdfReader
import chromadb

# Optional: OCR Imports
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'outputs', 'pdf_links.csv')
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'data', 'downloads')
EXTRACT_DIR = os.path.join(BASE_DIR, 'data', 'extracted_text')
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'download.log')

TIMEOUT = 60
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB
MIN_TEXT_LENGTH = 2000  # Unter diesem Wert wird OCR versucht
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
COLLECTION_NAME = 'deal_radar_reports'

for d in [LOG_DIR, DOWNLOAD_DIR, EXTRACT_DIR, CHROMA_DIR]:
    os.makedirs(d, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
}


# ── Text-Extraktion ─────────────────────────────────────────────────

def extract_text_pypdf(filepath):
    """Extrahiert Text mit pypdf."""
    text = ""
    page_count = 0
    try:
        reader = PdfReader(filepath)
        page_count = len(reader.pages)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        logger.warning(f"  pypdf error: {e}")
    return text, page_count


def extract_text_ocr(filepath):
    """Fallback: OCR via Tesseract (max 30 Seiten)."""
    if not OCR_AVAILABLE:
        return ""
    text = ""
    try:
        images = convert_from_path(filepath, first_page=1, last_page=30)
        for img in images:
            t = pytesseract.image_to_string(img)
            text += t + "\n"
    except Exception as e:
        logger.warning(f"  OCR error: {e}")
    return text


def extract_text(filepath):
    """Extrahiert Text aus PDF (pypdf + OCR fallback)."""
    text, page_count = extract_text_pypdf(filepath)
    method = "pypdf"
    if len(text.strip()) < MIN_TEXT_LENGTH and OCR_AVAILABLE:
        logger.info(f"  OCR Fallback ({len(text)} Zeichen)...")
        ocr_text = extract_text_ocr(filepath)
        if len(ocr_text) > len(text):
            text = ocr_text
            method = "ocr"
    return text, page_count, method


# ── Chunking ────────────────────────────────────────────────────────

def chunk_text(text):
    """Splittet Text in überlappende Chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ── Download + Extract + Index ──────────────────────────────────────

def get_safe_filename(company_id, year, url):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    return f"{company_id}_{year}_{url_hash}.pdf"


def process_one(row, collection):
    """Lädt ein PDF herunter, extrahiert Text und indiziert es sofort."""
    company_id = row['company_id']
    year = row['year_guess']
    pdf_url = row['pdf_url']

    # ── 1. Download ──────────────────────────────────────────────
    target_dir = os.path.join(DOWNLOAD_DIR, company_id, year)
    os.makedirs(target_dir, exist_ok=True)

    filename = get_safe_filename(company_id, year, pdf_url)
    filepath = os.path.join(target_dir, filename)
    already_existed = os.path.exists(filepath)

    if not already_existed:
        try:
            time.sleep(0.5)
            response = requests.get(pdf_url, headers=HEADERS, timeout=TIMEOUT, stream=True)
            if response.status_code != 200:
                logger.info(f"FAILED ({response.status_code}): {company_id} - {pdf_url}")
                return 'failed'

            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                logger.info(f"SKIPPED (Content-Type: {content_type}): {company_id} - {pdf_url}")
                return 'failed'

            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                logger.info(f"SKIPPED (too large): {company_id} - {pdf_url}")
                return 'failed'

            downloaded_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)

            if downloaded_size < 1024:
                os.remove(filepath)
                logger.info(f"REMOVED (too small: {downloaded_size}B): {company_id} - {pdf_url}")
                return 'failed'

            logger.info(f"DOWNLOADED ({downloaded_size // 1024}KB): {company_id} - {pdf_url}")
        except Exception as e:
            logger.error(f"ERROR download: {company_id} - {pdf_url} - {e}")
            return 'error'

    # ── 2. Text-Extraktion ───────────────────────────────────────
    txt_dir = os.path.join(EXTRACT_DIR, company_id, year)
    os.makedirs(txt_dir, exist_ok=True)
    base_name = filename.replace('.pdf', '')
    txt_path = os.path.join(txt_dir, base_name + '.txt')
    meta_path = os.path.join(txt_dir, base_name + '_meta.json')

    # Nur extrahieren wenn noch nicht vorhanden
    if not os.path.exists(txt_path):
        text, page_count, method = extract_text(filepath)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        meta = {
            'source_file': filepath,
            'source_url': pdf_url,
            'char_count': len(text),
            'page_count': page_count,
            'method': method
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f)
        logger.info(f"EXTRACTED ({len(text)} chars, {method}): {company_id}/{year}/{base_name}")
    else:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        method = 'cached'

    # ── 3. In ChromaDB indizieren ────────────────────────────────
    if len(text.strip()) < 100:
        logger.warning(f"SKIP INDEX (zu wenig Text): {company_id}/{year}/{base_name}")
        if already_existed:
            return 'skipped'
        return 'success'

    # Prüfen ob schon indiziert (erster Chunk als Indikator)
    first_chunk_id = f"{company_id}_{year}_{base_name}_0"
    try:
        existing = collection.get(ids=[first_chunk_id])
        if existing and existing['ids']:
            logger.info(f"INDEX SKIP (bereits im Index): {company_id}/{year}")
            if already_existed:
                return 'skipped'
            return 'success'
    except Exception:
        pass

    chunks = chunk_text(text)
    batch_ids, batch_docs, batch_metas = [], [], []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{company_id}_{year}_{base_name}_{i}"
        metadata = {
            'company_id': company_id,
            'year': year,
            'source_file': base_name + '.txt',
            'chunk_index': i,
            'char_count': len(chunk),
            'extraction_method': method
        }
        batch_ids.append(chunk_id)
        batch_docs.append(chunk)
        batch_metas.append(metadata)

        if len(batch_ids) >= 200:
            collection.add(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
            batch_ids, batch_docs, batch_metas = [], [], []

    if batch_ids:
        collection.add(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)

    logger.info(f"INDEXED ({len(chunks)} chunks): {company_id}/{year}/{base_name}")

    if already_existed:
        return 'skipped'
    return 'success'


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input {INPUT_FILE} not found. Bitte erst 02_collect_pdf_links.py ausführen.")
        return

    links = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        links = list(reader)

    print(f"Verarbeite {len(links)} PDFs (Download → Extraktion → Index)...")

    # ChromaDB vorbereiten
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        existing_count = collection.count()
        print(f"ChromaDB: {existing_count} Chunks im bestehenden Index.")
    except Exception as e:
        logger.error(f"ChromaDB Error: {e}")
        return

    success_count = 0
    skipped_count = 0
    error_count = 0

    for row in tqdm(links):
        result = process_one(row, collection)
        if result == 'success':
            success_count += 1
        elif result == 'skipped':
            skipped_count += 1
        else:
            error_count += 1

    final_count = collection.count()
    print("-" * 50)
    print(f"Fertig.")
    print(f"  Neu heruntergeladen & indiziert: {success_count}")
    print(f"  Übersprungen (existierten bereits): {skipped_count}")
    print(f"  Fehler: {error_count}")
    print(f"  Chunks im Index: {final_count}")
    print(f"Logs: {LOG_FILE}")


if __name__ == "__main__":
    main()
