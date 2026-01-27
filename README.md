# Passaporto Energetico (Italia) – Web App

Web app “diagnostica” per caricare 1–2 bollette (recente + vecchia), eseguire controlli automatici e produrre un report chiaro, con condivisione tramite link e un pannello admin minimale.

## Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI (Python) + PostgreSQL
- **Storage**: filesystem in dev, S3-compatible in produzione (MinIO support)
- **OCR**: Tesseract (pytesseract) + `pdfplumber` + fallback OCR
- **Migrations**: Alembic
- **Tests**: pytest (unit + API basics)
- **Logging**: JSON structured logs

## Avvio locale (1 comando)

1) Copia il file env:

```bash
copy .env.example .env
```

2) Avvia tutto:

```bash
docker compose up --build
```

3) Apri:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000/docs`

## Migrazioni DB (Alembic)

Eseguite automaticamente all’avvio del container backend. Se vuoi eseguirle manualmente:

```bash
docker compose exec backend alembic upgrade head
```

## Test backend

In un altro terminale:

```bash
docker compose exec backend pytest -q
```

## Test manuali (curl)

Dopo aver avviato i servizi, puoi eseguire i test manuali:

**Linux/Mac:**
```bash
chmod +x test-manual.sh
./test-manual.sh
```

**Windows (PowerShell):**
```powershell
.\test-manual.ps1
```

Oppure usa i comandi curl direttamente (vedi `test-manual.sh` o `test-manual.ps1`).

## Note su OCR in Docker
L’immagine backend include `tesseract-ocr` e `poppler-utils` per estrazione testo PDF e OCR fallback.

## Deploy produzione (VPS Ubuntu 24.04 + Nginx + SSL + DNS)

### Setup VPS (Docker + Compose)
- **Docker**:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Rientra via SSH per applicare il gruppo `docker`.

### Nginx reverse proxy
- Copia `nginx/passaportoenergetico.conf.example` in `/etc/nginx/sites-available/passaportoenergetico.conf`
- Abilita:

```bash
sudo ln -s /etc/nginx/sites-available/passaportoenergetico.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### SSL (Let’s Encrypt / Certbot)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d passaportoenergetico.it -d www.passaportoenergetico.it
```

### DNS (Cloudflare consigliato)
Opzione A (consigliata):
- **Nameserver**: imposta i nameserver del dominio su quelli forniti da Cloudflare.
- In Cloudflare crea:
  - **A**: `passaportoenergetico.it` → IP del VPS
  - **CNAME**: `www` → `passaportoenergetico.it`

Opzione B (senza Cloudflare):
- Nel pannello del registrar crea:
  - **A**: `@` → IP del VPS
  - **CNAME**: `www` → `@` (o `passaportoenergetico.it`)

### Variabili ambiente produzione

Crea `.env` sul VPS con:

```bash
# Database (usa password forte)
POSTGRES_PASSWORD=password-forte-qui
DATABASE_URL=postgresql+psycopg://pe:password-forte-qui@postgres:5432/passaporto_energetico

# Backend URLs
BASE_URL=https://passaportoenergetico.it
CORS_ORIGINS=https://passaportoenergetico.it,https://www.passaportoenergetico.it

# Admin (usa password forte)
ADMIN_PASSWORD=password-admin-forte-qui
SECRET_KEY=secret-key-forte-qui

# Storage (produzione: usa S3)
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=https://s3.amazonaws.com  # o MinIO endpoint
S3_BUCKET=passaporto-energetico
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=eu-west-1

# Ambiente
ENV=prod
LOG_LEVEL=INFO
```

### Verifica DNS

Dopo aver configurato DNS, verifica con:

```bash
# Verifica A record
dig passaportoenergetico.it +short

# Verifica CNAME www
dig www.passaportoenergetico.it +short

# Verifica nameserver
dig NS passaportoenergetico.it +short
```

Dovresti vedere:
- A record → IP del VPS
- www CNAME → passaportoenergetico.it
- NS → nameserver corretti (Cloudflare o registrar)

### Perché il dominio può risultare “dnsHold” / “inactive”

Alcuni registrar applicano un *hold* finché:
- non imposti nameserver validi, oppure
- il dominio non supera verifiche/attivazione (es. documenti, pagamento, email di conferma).

**Come verificare se è in hold:**
```bash
whois passaportoenergetico.it | grep -i hold
```

**Soluzione step-by-step:**
1. **Imposta nameserver** (Cloudflare consigliato):
   - Vai nel pannello del registrar
   - Trova "Nameserver" o "DNS"
   - Imposta quelli forniti da Cloudflare (es. `ns1.cloudflare.com`, `ns2.cloudflare.com`)
   - Salva e attendi 5-60 minuti

2. **Completa attivazione nel registrar:**
   - Verifica email di conferma se richiesta
   - Completa documenti/pagamento se pendenti
   - Rimuovi eventuali "locks" nel pannello

3. **Verifica propagazione:**
   ```bash
   dig NS passaportoenergetico.it +short
   ```
   Se vedi i nameserver corretti, il hold è rimosso.

4. **Se persiste:**
   - Contatta supporto registrar
   - Chiedi esplicitamente di rimuovere "dnsHold" o "clientHold"
   - Attendi fino a 24h per propagazione completa

**Nota:** Se usi Cloudflare, il dominio deve puntare ai nameserver Cloudflare. Se usi DNS del registrar, imposta A record + CNAME direttamente.

