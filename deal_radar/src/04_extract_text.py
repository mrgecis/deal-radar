import os
import json
import logging
from glob import glob
from tqdm import tqdm
from pypdf import PdfReader
# Optional: OCR Imports (nur laden wenn benötigt)
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'data', 'downloads')
EXTRACT_DIR = os.path.join(BASE_DIR, 'data', 'extracted_text')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

MIN_TEXT_LENGTH = 2000  # Wenn weniger Zeichen extrahiert werden, versuche OCR

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'extract_text.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_text_pypdf(filepath):
    """Versucht Text mit pypdf zu extrahieren."""
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
        logger.warning(f"  Error pypdf for {filepath}: {e}")
    return text, page_count

def extract_text_ocr(filepath):
    """Fallback: Rendert PDF zu Bildern und nutzt Tesseract OCR."""
    if not OCR_AVAILABLE:
        return ""
    
    text = ""
    try:
        images = convert_from_path(filepath, first_page=1, last_page=30)
        
        for img in images:
            t = pytesseract.image_to_string(img)
            text += t + "\n"
    except Exception as e:
        logger.warning(f"  Error OCR for {filepath}: {e}")
    return text

def parse_path_info(filepath):
    """Extrahiert company_id und year aus dem Dateipfad, robust gegen verschiedene Tiefen."""
    # Erwartet: .../downloads/{company_id}/{year}/{filename}.pdf
    rel_path = os.path.relpath(filepath, DOWNLOAD_DIR)
    parts = rel_path.split(os.sep)
    
    if len(parts) >= 3:
        company_id = parts[0]
        year = parts[1]
        filename = parts[-1]
    elif len(parts) == 2:
        company_id = parts[0]
        year = "unknown"
        filename = parts[1]
    else:
        company_id = "unknown"
        year = "unknown"
        filename = parts[0]
    
    return company_id, year, filename

def process_file(filepath):
    company_id, year, filename = parse_path_info(filepath)
    
    # Zielpfad
    target_dir = os.path.join(EXTRACT_DIR, company_id, year)
    target_file = os.path.join(target_dir, filename.replace('.pdf', '.txt'))
    meta_file = os.path.join(target_dir, filename.replace('.pdf', '_meta.json'))
    
    if os.path.exists(target_file):
        return # Skip
        
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Schnelle Extraktion
    text, page_count = extract_text_pypdf(filepath)
    method = "pypdf"
    
    # 2. Check Quality / OCR Fallback
    if len(text.strip()) < MIN_TEXT_LENGTH and OCR_AVAILABLE:
        logger.info(f"  OCR Fallback für {filename} ({len(text)} Zeichen mit pypdf)...")
        ocr_text = extract_text_ocr(filepath)
        if len(ocr_text) > len(text):
            text = ocr_text
            method = "ocr"
    
    # Speichern
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(text)
        
    # Metadaten
    meta = {
        'source_file': filepath,
        'char_count': len(text),
        'page_count': page_count,
        'method': method
    }
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f)

def main():
    # Alle PDFs finden
    pdf_files = glob(os.path.join(DOWNLOAD_DIR, '**', '*.pdf'), recursive=True)
    
    print(f"Starte Text-Extraktion für {len(pdf_files)} Dateien...")
    if not OCR_AVAILABLE:
        print("WARNUNG: pytesseract/pdf2image nicht verfügbar - OCR Fallback deaktiviert.")
        
    for pdf_path in tqdm(pdf_files):
        process_file(pdf_path)
        
    print("Fertig.")

if __name__ == "__main__":
    main()
