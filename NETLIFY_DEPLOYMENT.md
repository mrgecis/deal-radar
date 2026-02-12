# Netlify Deployment Guide

## ✅ Voraussetzungen erfüllt

- ✅ GitHub Repository: https://github.com/mrgecis/deal-radar
- ✅ netlify.toml Konfiguration vorhanden
- ✅ Code auf GitHub gepusht

## 📋 Schritte zum Deployment auf Netlify

### 1. **Netlify-Konto verbinden**

Gehen Sie zu https://app.netlify.com und melden Sie sich an (oder erstellen Sie ein neues Konto).

### 2. **Neues Projekt erstellen**

- Klicken Sie auf **"Add new site"**
- Wählen Sie **"Import an existing project"**
- Authentifizieren Sie mit GitHub
- Wählen Sie das Repository: **`mrgecis/deal-radar`**

### 3. **Build-Einstellungen konfigurieren**

Im Deploy-Dialog folgende Einstellungen vornehmen:

- **Branch to deploy**: `main`
- **Build command**: (leer lassen oder `echo "No build"`)
- **Publish directory**: `deal_radar/webapp`

### 4. **Environment Variables hinzufügen**

Unter "Advanced" → "Environment variables" folgende Variable hinzufügen:

```
OPENAI_API_KEY = sk-... (Ihre OpenAI API Key)
```

### 5. **Deploy starten**

- Klicken Sie auf **"Deploy site"**
- Netlify führt das Build aus und deployted automatisch
- Nach ~1-2 Minuten ist die Seite live

## 📊 Was wird deployed?

- **Frontend**: HTML, CSS, JavaScript (aus `deal_radar/webapp/`)
- **Konfiguration**: netlify.toml wird gelesen
- **Environment**: OPENAI_API_KEY wird bereitgestellt

## ⚠️ Wichtige Hinweise

### Python Server lokal vs. Remote

**Aktuelles Setup**: Der Python-Server (`server.py`) muss lokal ausgeführt werden.

Für echtes Netlify-Deployment mit Python-Backend haben Sie zwei Optionen:

#### Option A: Netlify Functions (empfohlen)
Konvertieren Sie die Python-APIs zu Netlify Functions (serverless):

```
functions/
├── chat.py
├── report.py
└── companies.py
```

#### Option B: Externer API-Server
Hosten Sie den Python-Server separat (z.B. auf Heroku, Railway, Render) und ändern Sie die Frontend-URLs:

```javascript
// In app.js
const API_URL = 'https://deal-radar-api.herokuapp.com/api';
```

## 🚀 Sofort-Deployment ohne Python-Backend

Wenn Sie nur die Frontend-Seite deployen möchten:

1. Ändern Sie die Publish directory zu: `deal_radar/webapp`
2. Netlify wird die HTML/CSS/JS-Dateien servieren
3. API-Calls müssen an einen externen Server gehen

## 🔗 Wichtige Links

- **GitHub Repo**: https://github.com/mrgecis/deal-radar
- **Netlify App**: https://app.netlify.com
- **OpenAI API Keys**: https://platform.openai.com/account/api-keys

---

Fragen? Kontaktieren Sie mich!
