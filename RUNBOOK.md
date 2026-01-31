# Bollettometro 2030 — RUNBOOK

## Prerequisiti

- Docker e Docker Compose installati
- Variabile `OPENAI_API_KEY` (per estrazione bollette)
- Opzionale: Git

## Setup

### 1. Clona/copia il progetto

```bash
cd D:\passaporto energetico
```

### 2. Variabili ambiente

```bash
copy .env.example .env
```

Modifica `.env` e imposta almeno:

- `OPENAI_API_KEY` — chiave API OpenAI (obbligatoria per l’estrazione)
- `SECRET_KEY` — stringa casuale lunga (es. `openssl rand -hex 32`)

### 3. Avvio stack

```bash
docker compose up -d --build
```

Servizi:

- **postgres** — porta 5432
- **redis** — porta 6379
- **backend** — porta 8000 (FastAPI)
- **worker** — Celery (nessuna porta)
- **frontend** — porta 3000 (Next.js)

### 4. Migrazioni database

Le migrazioni vanno eseguite la prima volta (o dopo pull di nuove migration):

```bash
docker compose exec backend alembic upgrade head
```

Se il backend non ha un entrypoint che le esegue, eseguile manualmente come sopra.

### 5. Verifica

- **Backend health:** `curl http://localhost:8000/health`
- **Frontend:** apri `http://localhost:3000`
- **API docs:** `http://localhost:8000/docs`

## Flusso utente

1. **Landing** (`/`) — “La tua spesa è in linea con i tuoi vicini?” → CTA “Tu dove sei?”
2. **Trust** (`/trust`) — messaggio di fiducia → “Procedi”
3. **Upload** (`/upload`) — avvio sessione, CAP, caricamento 2 bollette (recent + old) → “Avvia analisi”
4. **Processing** — polling stato job fino a “verified”
5. **Result** (`/result/[sessionId]`) — badge posizione (verde/giallo/rosso), grafico, “Scarica Passaporto”, “Condividi”, eventuale “Procedi al riallineamento”
6. **Share** (`/share/[sessionId]`) — genera share card, “Aggiungi il mio punto alla mappa”
7. **Riallineamento** (`/riallineamento/[sessionId]`) — testo orientato all’azione e CTA

## Dove sono i file generati

- **Upload:** `LOCAL_STORAGE_PATH/uploads/{session_id}/`
- **Passport PDF:** `LOCAL_STORAGE_PATH/passports/{session_id}.pdf`
- **Share card:** `LOCAL_STORAGE_PATH/share_cards/{session_id}.png`

In Docker i volumi sono in `backend_uploads` (vedi `docker compose.yml`).

## TTL (cancellazione upload)

- Il task Celery `ttl_cleanup` può essere schedulato (cron o Celery Beat) per eliminare file in `LOCAL_STORAGE_PATH` più vecchi di `UPLOAD_TTL_HOURS` (default 24).
- I dati estratti (DB) restano; vengono rimossi solo i file raw.

## Test

### Backend

```bash
docker compose exec backend pytest tests/ -v
```

### Frontend

```bash
docker compose exec frontend npm run build
```

## Comandi utili

```bash
# Log backend
docker compose logs -f backend

# Log worker
docker compose logs -f worker

# Log frontend
docker compose logs -f frontend

# Restart servizi
docker compose restart backend worker frontend

# Stop tutto
docker compose down
```

## Limitazioni note

- **OpenAI:** obbligatoria per l’estrazione; senza chiave l’analisi fallirà.
- **Mappa:** coordinate approssimate (CAP → lat/lng con jitter); nessuna mappa reale, solo punti aggregati per zona.
- **Riallineamento:** pagina presente; l’azione “Procedi alla proposta di riallineamento” è un placeholder (nessun backend dedicato).
