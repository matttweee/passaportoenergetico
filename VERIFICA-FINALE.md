# Verifica Finale - Passaporto Energetico

## Checklist Build & Run

### 1. Build pulita
```bash
docker compose build --no-cache
```
**Atteso:** Build completa senza errori.

### 2. Up pulito
```bash
docker compose up
```
**Atteso:** Nessun loop di crash su backend. Backend attende DB e parte correttamente.

### 3. Health reale
```bash
curl http://localhost:8000/health
```
**Atteso:**
```json
{
  "ok": true,
  "checks": {
    "database": "ok",
    "storage": "ok"
  }
}
```

### 4. Upload 2 file
- Da UI: carica 2 file (PDF o immagini)
- **Atteso:** Nessun errore 413 (troppo grande) o 415 (tipo non supportato)

### 5. Upload 1 file
- Da UI: carica solo 1 file
- **Atteso:** Funziona, ma report mostra warning "Confronto limitato: è stata caricata solo 1 bolletta..."

### 6. Upload >2 file
- Da UI: prova a caricare 3 file
- **Atteso:** Frontend blocca prima del submit. Backend rifiuta con 400 se bypassato.

### 7. PDF scannerizzato
- Carica un PDF scannerizzato (immagine, non testo)
- **Atteso:** pdfplumber ritorna vuoto → OCR parte automaticamente → state "running" non si blocca → completa correttamente

### 8. Error handling
- Carica un file rotto/zero bytes
- **Atteso:** `analysis_state=error` + messaggio chiaro in UI

### 9. Admin
- `/admin` → login con password da `.env`
- `/admin/submissions` → lista visibile
- Click su submission → dettaglio visibile
- Click "Scarica" su file → download funziona con nome corretto

### 10. Cookie secure
- In `.env` imposta `BASE_URL=https://...` o `ENV=prod`
- Login admin
- **Atteso:** Cookie `pe_admin` ha flag `Secure` in DevTools

## 6 Micro-Test Manuali (curl)

### 1) Health
```bash
curl -s http://localhost:8000/health | jq .
```

### 2) Crea submission
```bash
curl -s -X POST http://localhost:8000/api/submissions \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","phone":"","consent":true}' | jq .
```
**Salva `id` dalla risposta.**

### 3) Upload diretto (sostituisci SUB_ID)
```bash
# Sostituisci SUB_ID con l'id ottenuto al punto 2
# Sostituisci il path del file
curl -s -X POST "http://localhost:8000/api/submissions/SUB_ID/files?kind=latest" \
  -F "file=@./testdata/bolletta.pdf" | jq .
```

### 4) Avvia analisi
```bash
curl -s -X POST http://localhost:8000/api/submissions/SUB_ID/analyze | jq .
```

### 5) Poll stato
```bash
curl -s http://localhost:8000/api/submissions/SUB_ID/status | jq .
```
**Ripeti finché `analysis_state` diventa "done". Salva `share_token`.**

### 6) Report pubblico
```bash
# Sostituisci SHARE_TOKEN
curl -s http://localhost:8000/api/report/SHARE_TOKEN | jq .
```

## Test Rate Limiting

```bash
# Esegui 15 richieste rapide (burst=10, quindi le ultime 5 devono dare 429)
for i in {1..15}; do
  curl -s -X POST http://localhost:8000/api/submissions \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","consent":true}' \
    -w "\nStatus: %{http_code}\n"
  sleep 0.1
done
```
**Atteso:** Prime 10 OK (200), poi 429 Too Many Requests.

## Note Finali

- **Rate limiting:** 1 req/sec per IP, burst 10 (in-memory)
- **Cleanup job:** Esegue ogni ora, cancella submission pending >24h senza analyze
- **Download admin:** Headers corretti (Content-Disposition, Content-Type, Content-Length)
- **Warning comparazione:** Mostrato automaticamente se solo 1 file caricato
