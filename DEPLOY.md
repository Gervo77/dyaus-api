# Dyaus API — Railway Deployment

## Wat zit erin
- `app.py` — Flask server met `/api/dyaus/chat` endpoint
- `dyaus_bot.py` — Conversatie-engine (twee stemmen, intake, spiegel-methode)
- `dyaus_stem_engine.py` — Planetaire berekeningen (Swiss Ephemeris)
- `cloud_client.py` — Claude API client
- `charts.py` — Natale dataset (familie Vos)
- `ephemeris/` — Swiss Ephemeris bestanden (4MB, dekking 1800-2400)
- `Procfile` — Railway/Heroku process definitie
- `requirements.txt` — Python dependencies

## Stappen

### 1. Nieuw Railway project
- Ga naar https://railway.app
- Klik "New Project" → "Deploy from GitHub repo" OF "Empty project"
- Als je GitHub gebruikt: push de `dyaus_api/` map naar een nieuwe repo

### 2. Environment variable
Stel in op Railway (Settings → Variables):
```
ANTHROPIC_API_KEY=sk-ant-api03-...jouw-key...
```

### 3. Deploy
- Bij GitHub: Railway deployt automatisch
- Bij handmatig: gebruik Railway CLI
  ```bash
  npm install -g @railway/cli
  railway login
  cd dyaus_api/
  railway up
  ```

### 4. URL noteren
Na deployment krijg je een URL zoals:
```
https://dyaus-api-production.up.railway.app
```

### 5. dyaus.html updaten
Open `orakel_systeem/web_portal/dyaus.html` en wijzig de Railway URL:
```javascript
: 'https://JOUW-RAILWAY-URL.up.railway.app';
```

### 6. Test
```bash
curl -X POST https://JOUW-URL.up.railway.app/api/dyaus/chat \
  -H "Content-Type: application/json" \
  -d '{"sessie_id":"test-1","bericht":"hallo"}'
```

## Kosten
- Railway: ~$5/maand (Hobby plan)
- Claude Sonnet: ~€0.01 per bericht
- 1000 berichten/maand = ~€10 Claude + €5 Railway = €15 totaal
