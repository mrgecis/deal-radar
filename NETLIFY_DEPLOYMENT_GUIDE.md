# Netlify Deployment Guide – Deal Radar

## 🚀 Option 1: Frontend-only auf Netlify (empfohlen)

Diese Variante deployed nur die Frontend-Dateien auf Netlify, während der Python-Backend auf einem anderen Server läuft.

### Schritt 1: Python-Server woanders hosten

Sie haben mehrere Optionen für das Backend-Hosting:

#### A. **Railway (empfohlen, kostenlos bis 5$/mo)**
1. Gehen Sie zu https://railway.app
2. Melden Sie sich mit GitHub an
3. Erstellen Sie eine neue „Empty Service"
4. Verbinden Sie Ihr GitHub Repository
5. Setzen Sie folgende Environment Variables:
   - `OPENAI_API_KEY`: Ihre OpenAI API Key
6. Definieren Sie den **Start Command**:
   ```bash
   cd deal_radar/webapp && python3 server.py 8000
   ```
7. Railway wird eine URL wie `https://deal-radar-prod.up.railway.app` generieren

#### B. **Render (kostenlos)**
1. Gehen Sie zu https://render.com
2. Melden Sie sich mit GitHub an
3. Erstellen Sie einen neuen **Web Service**
4. Wählen Sie Ihr Repository
5. **Build Command**: `pip install -r deal_radar/requirements.txt`
6. **Start Command**: `cd deal_radar/webapp && python3 server.py $PORT`
7. Setzen Sie Environment Variables (wie oben)

#### C. **Heroku (zahlungspflichtig, $7/mo)**
Ähnlicher Prozess wie Railway/Render

### Schritt 2: Backend-URL notieren

Nach dem Deployment sollten Sie eine URL wie folgende haben:
```
https://deal-radar-prod.up.railway.app
```

### Schritt 3: Frontend auf Netlify deployen

1. Gehen Sie zu https://netlify.com
2. Klicken Sie auf **"Add new site"** → **"Import an existing project"**
3. Wählen Sie GitHub und das Repository `mrgecis/deal-radar`
4. **Build-Einstellungen**:
   - **Build command**: `echo "No build"`
   - **Publish directory**: `deal_radar/webapp`

5. Klicken Sie auf **"Deploy site"**

### Schritt 4: API-URL konfigurieren

Nach dem Deployment wird Netlify eine URL zuweisen (z.B. `https://deal-radar.netlify.app`).

Um diese mit Ihrem Backend zu verbinden, haben Sie zwei Optionen:

#### Option A: Environment Variable (besser)
1. Gehen Sie in Netlify zu **Site Settings** → **Build & deploy** → **Environment**
2. Fügen Sie hinzu:
   ```
   REACT_APP_API_URL = https://deal-radar-prod.up.railway.app
   ```
3. Erstellen Sie eine `_redirects`-Datei in `deal_radar/webapp/`:

```
/api/*  https://deal-radar-prod.up.railway.app/api/:splat  200
```

4. Triggern Sie einen neuen Deploy (git push)

#### Option B: Direkt in app.js setzen (schneller)

Öffnen Sie `deal_radar/webapp/app.js` und ändern Sie:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://deal-radar-prod.up.railway.app';  // ← Ändern Sie dies
```

Pushen Sie die Änderung zu GitHub → Netlify deployed automatisch.

---

## 🔧 Option 2: Vollständiges Deployment auf eigenem Server (Advanced)

Wenn Sie auf einem eigenen VPS/Server deployen möchten:

### VPS (Digital Ocean, Linode, Hetzner)

```bash
# 1. Server Setup
ssh root@your-server.com
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv

# 2. Repository klonen
git clone https://github.com/mrgecis/deal-radar.git
cd deal-radar

# 3. Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r deal_radar/requirements.txt

# 4. Mit systemd starten (persistent)
sudo tee /etc/systemd/system/deal-radar.service > /dev/null <<EOF
[Unit]
Description=Deal Radar Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/deal-radar/deal_radar/webapp
ExecStart=/root/deal-radar/venv/bin/python3 server.py 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start deal-radar
sudo systemctl enable deal-radar

# 5. Nginx als Reverse Proxy
sudo apt install nginx
sudo tee /etc/nginx/sites-available/deal-radar > /dev/null <<'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/deal-radar /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## ✅ Testing

Nach dem Deploy:

1. Öffnen Sie die Netlify-URL: `https://deal-radar.netlify.app`
2. Die Seite sollte laden
3. Klicken Sie auf eine Firma
4. Prüfen Sie, ob die "EVIDENCE & SIGNALS" Daten angezeigt werden
5. Testen Sie den AI Chat

---

## 🐛 Troubleshooting

### "API calls fail with CORS errors"

**Lösung**: Ihr Backend muss CORS-Header setzen. Das ist bereits im Server implementiert:

```python
self.send_header('Access-Control-Allow-Origin', '*')
self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
```

Wenn Sie noch Fehler haben, Ihr Backend-Provider blockiert möglicherweise externe Zugriffe.

### "API calls to localhost"

Das Frontend versucht immer noch, `localhost:8000` zu erreichen.

**Lösung**: Stellen Sie sicher, dass Sie die API_BASE_URL richtig gesetzt haben (siehe Schritt 4 oben).

### "404 – API endpoint not found"

Prüfen Sie, ob Ihr Backend tatsächlich läuft:

```bash
curl https://your-backend-url.com/api/stats
```

---

## 💡 Zusammenfassung

| Komponente | Hosting | Status |
|-----------|---------|--------|
| Frontend (HTML/CSS/JS) | **Netlify** | ✅ Statisch |
| Python Backend Server | **Railway/Render/Heroku** | ✅ Serverless/Compute |
| ChromaDB + PDFs | Local oder S3 | Lokal oder Cloud Storage |

---

Fragen? Kontaktieren Sie mich!
