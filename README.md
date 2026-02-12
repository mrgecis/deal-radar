# Deal Radar – M&A Intelligence Platform

Eine KI-gestützte Plattform zur Analyse von Geschäftsberichten und Identifikation von M&A-Opportunities basierend auf Distressed-Signalen.

## Features

- 🔍 **Intelligente Signalanalyse**: Erkennung von Carve-outs, Financial Distress und Business Services Opportunities
- 🤖 **AI-Chat**: OpenAI gpt-4o-mini für kontextuelle Analysen
- 📚 **ChromaDB Vector Search**: Effiziente Suche über 13.000+ Chunks
- 📄 **PDF-Integration**: Automatische Extraktion und Indizierung von Geschäftsberichten
- 🌐 **Web-UI**: Interaktive Oberfläche zum Erkunden von Unternehmen und Signalen

## Technologie

- **Backend**: Python 3 mit FastHTTP Server
- **Vector Database**: ChromaDB mit OpenAI Embeddings
- **Frontend**: Vanilla JavaScript mit responsivem Design
- **AI**: OpenAI API (gpt-4o-mini)

## Lokale Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/deal-radar.git
cd deal-radar

# Python Dependencies installieren
pip install -r deal_radar/requirements.txt

# Server starten
cd deal_radar/webapp
python3 server.py 8000
```

Die Webapp läuft dann unter: **http://localhost:8000**

## Deployment auf Netlify

Diese Webapp ist optimiert für Netlify Deployment:

1. **GitHub verbinden**: Repo mit Netlify verknüpfen
2. **Build Command**: `echo "No build required"`
3. **Publish Directory**: `deal_radar/webapp`
4. **Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Weitere sind optional

Die Python-Backend wird lokal ausgeführt, die Frontend-Assets (HTML, CSS, JS) werden über Netlify serviert.

## Umgebungsvariablen

Erstelle eine `.env` Datei im `deal_radar/` Verzeichnis:

```
OPENAI_API_KEY=sk-...
```

## Projektstruktur

```
deal_radar/
├── webapp/              # Web-UI (Frontend + Backend Server)
│   ├── server.py        # Python HTTP Server
│   ├── index.html       # Main UI
│   ├── app.js           # Frontend Logic
│   ├── styles.css       # Styling
│   └── pipeline_queue.py
├── src/                 # Pipeline Scripts
│   ├── 01_discover_ir.py
│   ├── 02_collect_pdf_links.py
│   ├── 03_download_pdfs.py
│   ├── 04_extract_text.py
│   ├── 05_scan_reports.py
│   ├── 06_score_and_export.py
│   ├── 07_build_index.py
│   └── 08_chat.py
├── data/
│   ├── chroma_db/       # Vector Database
│   ├── downloads/       # PDF Files
│   ├── extracted_text/  # Extracted Text
│   └── outputs/         # Results (CSV, JSONL)
└── requirements.txt
```

## API Endpoints

- `GET /api/companies` – Liste aller Unternehmen
- `GET /api/stats` – Übersichtsstatistiken
- `GET /api/report?company=<id>` – Analyse für ein Unternehmen
- `POST /api/chat` – AI Chat

## Author

Tobi

## License

MIT
