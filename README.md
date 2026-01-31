# Bollettometro 2030

**La tua spesa è in linea con i tuoi vicini?**

Web app per confrontare il proprio andamento di spesa energetica con quello della zona (CAP), con passaporto PDF, share card e mappa anonima del quartiere.

## Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend:** FastAPI + PostgreSQL + Redis + Celery
- **Storage:** filesystem locale (o S3 in produzione)
- **Estrazione:** OpenAI (GPT-4o-mini / vision) con schema JSON rigoroso
- **Migrazioni:** Alembic
- **Test:** pytest (schema, trend)

## Avvio locale

1. Copia le variabili ambiente:

```bash
copy .env.example .env
```

2. Imposta almeno `OPENAI_API_KEY` e `SECRET_KEY` in `.env`.

3. Avvia lo stack:

```bash
docker compose up -d --build
```

4. Migrazioni (se non eseguite dall’entrypoint):

```bash
docker compose exec backend alembic upgrade head
```

5. Apri:

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Flusso utente

1. **Landing** — “Tu dove sei?” → Trust → Upload (CAP + 2 bollette) → Analisi in background
2. **Risultato** — Posizione (verde/giallo/rosso), grafico utente vs zona, “Scarica Passaporto”, “Condividi”
3. **Share** — Share card 1080×1080, “Aggiungi il mio punto alla mappa”
4. **Riallineamento** — Se fuori trend, CTA verso proposta di riallineamento

## Documentazione operativa

Vedi **RUNBOOK.md** per:

- Prerequisiti e setup
- Comandi per migrazioni, test, log
- Dove sono i file generati
- TTL upload e limitazioni

## Limitazioni

- **OpenAI:** obbligatoria per l’estrazione bollette.
- **Mappa:** punti anonimi per zona (CAP); coordinate approssimate.
- **Riallineamento:** pagina presente; backend dedicato non incluso in questa versione.
