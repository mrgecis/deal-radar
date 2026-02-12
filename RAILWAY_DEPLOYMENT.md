# 🚀 Backend auf Railway deployen - Schritt für Schritt

## Das Frontend ist live! 🎉
- **URL**: https://dealpipeline.netlify.app

Jetzt müssen Sie nur noch das **Python-Backend** deployen.

---

## Schritt 1: Railway-Account erstellen

1. Gehen Sie zu https://railway.app
2. Klicken Sie auf **"Start with GitHub"**
3. Authentifizieren Sie sich mit GitHub (mrgecis)
4. Railway wird Ihren Account erstellen

---

## Schritt 2: Neues Projekt erstellen

1. Im Railway Dashboard: Klicken Sie auf **"New Project"**
2. Wählen Sie **"Deploy from GitHub repo"**
3. Wählen Sie: `mrgecis/deal-radar`
4. Klicken Sie auf **"Deploy Now"**

---

## Schritt 3: Railway konfigurieren

Nach dem Auswählen des Repos müssen Sie 3 Dinge konfigurieren:

### A. Environment Variables

1. Gehen Sie in das Railway Projekt Dashboard
2. Klicken Sie auf **"Variables"**
3. Fügen Sie hinzu:
   ```
   OPENAI_API_KEY = sk-... (Ihre OpenAI API Key)
   ```

### B. Start Command

1. Klicken Sie auf den **"Deploy"** Tab
2. Scrollt zu **"Run Command"** (oder "Start Command")
3. Setzen Sie:
   ```
   cd deal_radar/webapp && python3 server.py $PORT
   ```

### C. Root Directory (wenn nötig)

Wenn Railway Sie danach fragt, setzen Sie:
```
deal_radar
```

---

## Schritt 4: Deploy starten

Railway sollte automatisch deployieren. Nach ~2-3 Minuten:

1. Sie sehen einen **grünen Checkmark** = erfolgreich!
2. Railway gibt Ihnen eine Public URL, z.B.:
   ```
   https://deal-radar-prod-xyzabc.up.railway.app
   ```

**Notieren Sie diese URL!**

---

## Schritt 5: Frontend mit Backend verbinden

Jetzt müssen Sie die Backend-URL im Frontend setzen:

### Option A: Direkt in der Datei (einfach)

1. Öffnen Sie: `/deal_radar/webapp/app.js`
2. Finden Sie Zeile ~6:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' 
     ? 'http://localhost:8000'
     : (window.__API_BASE_URL__ || '');
   ```

3. Ändern Sie zu:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' 
     ? 'http://localhost:8000'
     : 'https://deal-radar-prod-xyzabc.up.railway.app';  // ← Ihre Railway-URL
   ```

4. Speichern und committen:
   ```bash
   git add deal_radar/webapp/app.js
   git commit -m "Set production backend URL"
   git push
   ```

5. Netlify deployed automatisch neu!

### Option B: Über Umgebungsvariablen (besser)

1. Gehen Sie zu Netlify: https://app.netlify.com/sites/dealpipeline
2. Site settings → Build & deploy → Environment
3. Klicken Sie auf **"Edit variables"**
4. Fügen Sie hinzu:
   ```
   API_BASE_URL = https://deal-radar-prod-xyzabc.up.railway.app
   ```

Dann müssen Sie in `app.js` ändern:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : (window.location.origin + process.env.API_BASE_URL) || '';
```

---

## Schritt 6: Testen

1. Öffnen Sie: https://dealpipeline.netlify.app
2. Warten Sie, bis die Companies geladen sind
3. Klicken Sie auf eine Firma
4. Scrollt zu "EVIDENCE & SIGNALS"
5. Sie sollten jetzt die Signale sehen! ✅

---

## 🔗 Wichtige Links

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://dealpipeline.netlify.app | ✅ Live |
| **Backend** | https://deal-radar-prod-*.up.railway.app | ⏳ Sie deployen |
| **Repository** | https://github.com/mrgecis/deal-radar | ✅ GitHub |
| **Netlify Project** | https://app.netlify.com/sites/dealpipeline | ✅ Linked |

---

## ⚠️ Fehlerbehandlung

### "API calls fail / 404 errors"

→ Das Backend läuft nicht. Prüfen Sie Railway Deployment Logs:
- Railway Dashboard → Deployments → Klicken Sie auf den fehlgeschlagenen Deploy
- Schauen Sie sich die Logs an

### "CORS errors in Browser Console"

→ Das ist okay, das Backend hat CORS enabled. Prüfen Sie, dass die URL richtig ist.

### "Python dependencies missing"

→ Railway sollte automatisch `pip install -r requirements.txt` ausführen.  
Wenn nicht, prüfen Sie die requirements.txt im Root und in `deal_radar/`.

---

## 💡 Nach dem Deployment

Nach 5-10 Minuten können Sie testen:

```bash
# Terminal
curl https://deal-radar-prod-xyzabc.up.railway.app/api/stats
```

Sollte zurückgeben:
```json
{"companies": 4, "pdfs": 207, "signals": 1008, "chunks": 13111, "avg_score": 8.1}
```

Wenn ja → **Alles funktioniert!** 🎉

---

Fragen? Ich helfe gerne weiter!
