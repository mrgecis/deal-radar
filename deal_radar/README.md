# Deal Radar

Automatisierte Pipeline zur Analyse von Investorenberichten für Carve-out-Opportunitäten.

## Setup

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

2. Playwright Browser installieren:
   ```bash
   playwright install
   ```

3. OCR-Engine (Tesseract) muss auf dem System installiert sein.
   - macOS: `brew install tesseract`

## Nutzung

Die Pipeline besteht aus nummerierten Skripten in `src/`, die nacheinander ausgeführt werden sollten:

1. **IR-Seiten finden**: `python src/01_discover_ir.py`
2. **PDF-Links sammeln**: `python src/02_collect_pdf_links.py`
3. **Download**: `python src/03_download_pdfs.py`
4. **Text Extraktion**: `python src/04_extract_text.py`
5. **Analyse**: `python src/05_scan_reports.py`
6. **Scoring & Export**: `python src/06_score_and_export.py`
7. **Vektor-Index bauen**: `python src/07_build_index.py`
8. **RAG-Chat starten**: `python src/08_chat.py`

Ergebnisse landen in `data/outputs/deal_radar.csv`.

## RAG-Chat

Nach dem Index-Aufbau kannst du mit deinen Report-Daten chatten:

```bash
export OPENAI_API_KEY="sk-..."
python src/08_chat.py
```

Beispiel-Fragen:
- "Welche Unternehmen planen Divestments?"
- "Was sagt Atos über Restrukturierung in 2024?"
- "Vergleiche die IT-Services-Segmente von CGI und Fujitsu"
- "Welche Firmen haben loss-making Segmente?"
