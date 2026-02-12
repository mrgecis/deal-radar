"""
07_build_index.py – Baut einen Vektor-Index (ChromaDB) über alle extrahierten Report-Texte.

Chunking-Strategie:
  - Jeder Text wird in Chunks von ~1000 Zeichen gesplittet (mit Overlap).
  - Jeder Chunk bekommt Metadaten: company_id, year, source_file.

ChromaDB nutzt ein lokales Embedding-Modell (all-MiniLM-L6-v2) –
kein API-Key nötig für den Index-Aufbau.
"""

import os
import json
import logging
from glob import glob
from tqdm import tqdm
import chromadb

# Konfiguration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_DIR = os.path.join(BASE_DIR, 'data', 'extracted_text')
CHROMA_DIR = os.path.join(BASE_DIR, 'data', 'chroma_db')
LOG_DIR = os.path.join(BASE_DIR, 'data', 'logs')

CHUNK_SIZE = 1000       # Zeichen pro Chunk
CHUNK_OVERLAP = 200     # Overlap zwischen Chunks
COLLECTION_NAME = 'deal_radar_reports'

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'build_index.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Splittet Text in überlappende Chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Nur Chunks mit Substanz speichern
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
        
        start += chunk_size - overlap
    return chunks


def main():
    # Alle Textfiles finden
    txt_files = glob(os.path.join(EXTRACT_DIR, '**', '*.txt'), recursive=True)
    
    if not txt_files:
        print("Keine Textdateien gefunden. Bitte erst Schritt 04 ausführen.")
        return

    print(f"Baue Vektor-Index über {len(txt_files)} Dokumente...")

    # ChromaDB Client (persistent, lokal)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Collection löschen und neu anlegen (für sauberen Rebuild)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        logger.info("Bestehende Collection gelöscht.")
    except Exception:
        pass
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    total_chunks = 0
    batch_ids = []
    batch_docs = []
    batch_metas = []
    BATCH_SIZE = 200  # ChromaDB Batch-Limit

    for txt_path in tqdm(txt_files):
        # Metadaten aus Pfad
        rel_path = os.path.relpath(txt_path, EXTRACT_DIR)
        parts = rel_path.split(os.sep)
        
        if len(parts) >= 3:
            company_id = parts[0]
            year = parts[1]
            filename = parts[-1]
        else:
            continue

        # Meta-JSON laden falls vorhanden
        meta_path = txt_path.replace('.txt', '_meta.json')
        extra_meta = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    extra_meta = json.load(f)
            except Exception:
                pass

        # Text lesen
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.warning(f"Fehler beim Lesen von {txt_path}: {e}")
            continue
        
        if len(text.strip()) < 100:
            continue

        # Chunken
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{company_id}_{year}_{filename}_{i}"
            
            metadata = {
                'company_id': company_id,
                'year': year,
                'source_file': filename,
                'chunk_index': i,
                'char_count': len(chunk),
                'extraction_method': extra_meta.get('method', 'unknown')
            }
            
            batch_ids.append(chunk_id)
            batch_docs.append(chunk)
            batch_metas.append(metadata)
            total_chunks += 1
            
            # Batch einfügen wenn voll
            if len(batch_ids) >= BATCH_SIZE:
                collection.add(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas
                )
                batch_ids = []
                batch_docs = []
                batch_metas = []

    # Restliche Chunks einfügen
    if batch_ids:
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas
        )

    print("-" * 50)
    print(f"Fertig. {total_chunks} Chunks aus {len(txt_files)} Dokumenten indexiert.")
    print(f"Index gespeichert in: {CHROMA_DIR}")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
