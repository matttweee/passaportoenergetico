# Deploy Produzione - Passaporto Energetico

## Prerequisiti
- VPS Ubuntu 24.04 con SSH access (root o sudo)
- IP pubblico del VPS (lo userai per DNS)
- Dominio `passaportoenergetico.it` registrato

---

## FASE 1: Setup Server (Ubuntu 24.04)

### 1.1 Installa Docker + Docker Compose Plugin

```bash
# Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# Installa dipendenze
sudo apt install -y ca-certificates curl gnupg lsb-release

# Aggiungi repository Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installa Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Aggiungi utente al gruppo docker (se non root)
sudo usermod -aG docker $USER

# Verifica installazione
docker --version
docker compose version
```

**Nota:** Se hai aggiunto l'utente a docker, esci e rientra via SSH per applicare i permessi.

### 1.2 Crea directory applicazione

```bash
sudo mkdir -p /opt/passaportoenergetico
sudo chown $USER:$USER /opt/passaportoenergetico
cd /opt/passaportoenergetico
```

### 1.3 Copia repository

**Opzione A: Git clone (se repo è su Git)**
```bash
git clone https://github.com/TUO_USERNAME/passaporto-energetico.git .
# oppure
git clone TUO_REPO_URL .
```

**Opzione B: Upload manuale**
```bash
# Dal tuo PC, usa scp o rsync:
# scp -r /path/to/passaporto\ energetico/* user@VPS_IP:/opt/passaportoenergetico/
```

### 1.4 Configura ambiente produzione

```bash
cd /opt/passaportoenergetico

# Copia template env
cp .env.production .env.production.local

# Edita e cambia i valori (usa nano o vim):
nano .env.production.local
```

**Valori da cambiare in `.env.production.local`:**
- `POSTGRES_PASSWORD` → password forte per DB
- `ADMIN_PASSWORD` → password forte per admin
- `SECRET_KEY` → stringa casuale lunga (min 32 caratteri)

**Genera SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 1.5 Crea directory SSL per certbot

```bash
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot
```

---

## FASE 2: Build e Avvio Servizi (prima di SSL)

### 2.1 Build immagini

```bash
cd /opt/passaportoenergetico
docker compose -f docker-compose.production.yml --env-file .env.production.local build
```

### 2.2 Avvia servizi (senza Nginx per ora, solo per test)

```bash
# Avvia solo postgres + backend + frontend (commenta nginx temporaneamente)
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d postgres backend frontend
```

### 2.3 Verifica health

```bash
# Attendi 30 secondi che tutto parta
sleep 30

# Verifica backend (dovrebbe rispondere su localhost:8000 internamente)
docker compose -f docker-compose.production.yml exec backend curl -s http://localhost:8000/health
```

**Atteso:** `{"ok": true, "checks": {"database": "ok", "storage": "ok"}}`

---

## FASE 3: Nginx + SSL (Let's Encrypt)

### 3.1 Installa Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 3.2 Ottieni certificato SSL

**IMPORTANTE:** Esegui questo solo dopo aver configurato DNS (FASE 4) e aver atteso 5-60 minuti.

**Opzione A: Usa script automatico**
```bash
cd /opt/passaportoenergetico
chmod +x setup-ssl.sh
./setup-ssl.sh TUO_EMAIL@example.com
```

**Opzione B: Manuale**
```bash
# Crea directory challenge
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# Avvia nginx temporaneo per challenge
docker run -d --name nginx-temp \
  -p 80:80 \
  -v /var/www/certbot:/var/www/certbot:ro \
  nginx:alpine \
  sh -c "echo 'server { listen 80; location /.well-known/acme-challenge/ { root /var/www/certbot; } location / { return 200 \"OK\"; } }' > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"

# Ottieni certificato
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it \
  --email TUO_EMAIL@example.com \
  --agree-tos \
  --non-interactive

# Ferma nginx temporaneo
docker stop nginx-temp && docker rm nginx-temp

# Verifica certificato
sudo ls -la /etc/letsencrypt/live/passaportoenergetico.it/
```

**Se certbot fallisce con "DNS not resolving":**
- Vai a FASE 4, configura DNS, attendi 5-60 minuti, poi riprova.

### 3.5 Configura rinnovo automatico

```bash
# Test rinnovo
sudo certbot renew --dry-run

# Aggiungi cron job (già presente di default, ma verifica)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 3.6 Avvia tutti i servizi con Nginx

```bash
cd /opt/passaportoenergetico

# Avvia tutto (incluso nginx)
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d

# Verifica che tutti i container siano up
docker compose -f docker-compose.production.yml ps
```

---

## FASE 4: Configurazione DNS

### Opzione A: Cloudflare (CONSIGLIATA)

#### Step 1: Aggiungi sito su Cloudflare
1. Vai su https://cloudflare.com e crea account (gratis)
2. Aggiungi sito: `passaportoenergetico.it`
3. Cloudflare ti darà 2 nameserver (es. `ns1.cloudflare.com`, `ns2.cloudflare.com`)

#### Step 2: Configura nameserver nel registrar (es. TopHost)
1. Accedi al pannello del tuo registrar (TopHost o altro)
2. Vai a "DNS" o "Nameserver"
3. **Sostituisci** i nameserver attuali con quelli di Cloudflare:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
4. Salva e attendi 5-60 minuti per propagazione

#### Step 3: Aggiungi record DNS in Cloudflare
Nel pannello Cloudflare, vai a "DNS" → "Records" e aggiungi:

**Record A:**
- Type: `A`
- Name: `@` (o `passaportoenergetico.it`)
- IPv4 address: `INSERISCI_IP_VPS_QUI` (es. `123.45.67.89`)
- Proxy status: **Proxied** (arancione) - OK per upload se Cloudflare è configurato correttamente
- TTL: Auto

**Record CNAME:**
- Type: `CNAME`
- Name: `www`
- Target: `passaportoenergetico.it` (o `@`)
- Proxy status: **Proxied** (arancione)
- TTL: Auto

**Nota su "Proxied":**
- **Proxied ON (arancione):** Cloudflare nasconde il tuo IP, aggiunge CDN, ma può causare problemi con upload grandi se non configurato. Per upload fino a 15MB, di solito OK.
- **Proxied OFF (grigio):** DNS diretto, nessun proxy. Più semplice, ma IP esposto.

**Se upload fallisce con Proxied ON:**
- Disattiva Proxied (grigio) per A e CNAME
- Oppure aumenta limite upload in Cloudflare (Plan → Page Rules o Workers)

#### Step 4: Verifica DNS
```bash
# Verifica A record
dig +short passaportoenergetico.it

# Verifica CNAME
dig +short www.passaportoenergetico.it

# Verifica nameserver
dig NS passaportoenergetico.it +short
```

**Atteso:**
- A record → IP del VPS (o IP Cloudflare se Proxied ON)
- www CNAME → passaportoenergetico.it
- NS → nameserver Cloudflare

---

### Opzione B: DNS Diretto (senza Cloudflare)

#### Step 1: Configura record nel registrar
Nel pannello del registrar (TopHost o altro), vai a "DNS" o "Zone DNS" e aggiungi:

**Record A:**
- Type: `A`
- Name: `@` (o lascia vuoto, o `passaportoenergetico.it`)
- Value/IP: `INSERISCI_IP_VPS_QUI`
- TTL: 3600 (o Auto)

**Record CNAME:**
- Type: `CNAME`
- Name: `www`
- Value/Target: `@` (o `passaportoenergetico.it`)
- TTL: 3600 (o Auto)

#### Step 2: Verifica DNS
```bash
dig +short passaportoenergetico.it
dig +short www.passaportoenergetico.it
```

**Atteso:** Entrambi devono risolvere all'IP del VPS.

---

### Risoluzione "dnsHold" / "inactive"

Se il dominio mostra "dnsHold" o "inactive":

1. **Verifica nameserver:**
   ```bash
   dig NS passaportoenergetico.it +short
   ```
   Se non vedi nameserver corretti, il registrar li sta ancora bloccando.

2. **Azioni nel registrar:**
   - Completa verifica email se richiesta
   - Completa documenti/pagamento se pendenti
   - Rimuovi eventuali "locks" nel pannello
   - Imposta nameserver corretti (Cloudflare o registrar)

3. **Verifica hold:**
   ```bash
   whois passaportoenergetico.it | grep -i hold
   ```

4. **Attendi propagazione:** 5-60 minuti (a volte fino a 24h)

5. **Se persiste:** Contatta supporto registrar e chiedi esplicitamente di rimuovere "dnsHold" o "clientHold"

---

## FASE 5: Verifica Finale

### 5.1 Verifica DNS
```bash
# A record
dig +short passaportoenergetico.it

# CNAME
dig +short www.passaportoenergetico.it

# Nameserver
dig NS passaportoenergetico.it +short
```

### 5.2 Verifica HTTPS
```bash
# HTTP redirect
curl -I http://passaportoenergetico.it

# HTTPS funziona
curl -I https://passaportoenergetico.it

# Health check backend
curl https://passaportoenergetico.it/health
```

**Atteso:**
- HTTP → 301 redirect a HTTPS
- HTTPS → 200 OK
- Health → `{"ok": true, "checks": {...}}`

### 5.3 Verifica frontend
Apri browser: `https://passaportoenergetico.it`

**Atteso:** Landing page visibile.

### 5.4 Verifica upload
1. Vai su `https://passaportoenergetico.it/start`
2. Carica 1-2 file (PDF/JPG/PNG)
3. **Atteso:** Upload funziona, nessun errore 413/415

### 5.5 Verifica admin
1. Vai su `https://passaportoenergetico.it/admin`
2. Login con password da `.env.production.local`
3. **Atteso:** Accesso admin funziona

---

## FASE 6: Troubleshooting

### DNS non risolve
```bash
# Verifica che DNS punti al VPS
dig +short passaportoenergetico.it

# Se non risolve:
# 1) Verifica nameserver nel registrar
# 2) Attendi propagazione (5-60 min)
# 3) Verifica con: nslookup passaportoenergetico.it
```

### 502 Bad Gateway da Nginx
```bash
# Verifica che backend e frontend siano up
docker compose -f docker-compose.production.yml ps

# Verifica log backend
docker compose -f docker-compose.production.yml logs backend

# Verifica log frontend
docker compose -f docker-compose.production.yml logs frontend

# Verifica log nginx
docker compose -f docker-compose.production.yml logs nginx

# Test connessione interna
docker compose -f docker-compose.production.yml exec nginx ping -c 2 backend
docker compose -f docker-compose.production.yml exec nginx ping -c 2 frontend
```

**Fix comuni:**
- Backend non parte: verifica `.env.production.local`, DATABASE_URL, password
- Frontend non parte: verifica NEXT_PUBLIC_BACKEND_URL
- Network: verifica che tutti i servizi siano su `app_network`

### Upload fallisce (413 Request Entity Too Large)
```bash
# Verifica nginx config
cat /opt/passaportoenergetico/nginx/production.conf | grep client_max_body_size

# Dovrebbe essere: client_max_body_size 20m;

# Se usi Cloudflare Proxied:
# - Aumenta limite in Cloudflare (Plan → Workers/Page Rules)
# - Oppure disattiva Proxied per A e CNAME
```

### Certbot fallisce (DNS not resolving)
```bash
# Verifica DNS prima
dig +short passaportoenergetico.it

# Se non risolve, configura DNS (FASE 4) e attendi 5-60 minuti

# Poi riprova certbot
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it
```

### Certificato scaduto / rinnovo fallisce
```bash
# Test rinnovo manuale
sudo certbot renew --dry-run

# Rinnovo forzato
sudo certbot renew --force-renewal

# Riavvia nginx per caricare nuovo certificato
docker compose -f docker-compose.production.yml restart nginx
```

### Log inspection
```bash
# Log backend
docker compose -f docker-compose.production.yml logs -f backend

# Log frontend
docker compose -f docker-compose.production.yml logs -f frontend

# Log nginx
docker compose -f docker-compose.production.yml logs -f nginx

# Log postgres
docker compose -f docker-compose.production.yml logs -f postgres

# Log sistema (se nginx non è in docker)
sudo journalctl -u nginx -f
```

### Restart servizi
```bash
cd /opt/passaportoenergetico

# Restart tutto
docker compose -f docker-compose.production.yml restart

# Restart singolo servizio
docker compose -f docker-compose.production.yml restart backend

# Rebuild e restart
docker compose -f docker-compose.production.yml up -d --build
```

### Backup database
```bash
# Backup
docker compose -f docker-compose.production.yml exec postgres pg_dump -U pe passaporto_energetico > backup_$(date +%Y%m%d).sql

# Restore
docker compose -f docker-compose.production.yml exec -T postgres psql -U pe passaporto_energetico < backup_YYYYMMDD.sql
```

---

## Comandi Rapidi (Reference)

```bash
# Avvia tutto
cd /opt/passaportoenergetico
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d

# Ferma tutto
docker compose -f docker-compose.production.yml down

# Restart tutto
docker compose -f docker-compose.production.yml restart

# Log in tempo reale
docker compose -f docker-compose.production.yml logs -f

# Status servizi
docker compose -f docker-compose.production.yml ps

# Shell in container
docker compose -f docker-compose.production.yml exec backend bash
docker compose -f docker-compose.production.yml exec frontend sh

# Migrazioni DB
docker compose -f docker-compose.production.yml exec backend alembic upgrade head
```

---

## Checklist Finale

- [ ] Docker + Compose installati
- [ ] Repository copiato in `/opt/passaportoenergetico`
- [ ] `.env.production.local` configurato con password forti
- [ ] Build immagini completata
- [ ] DNS configurato (Cloudflare o diretto)
- [ ] DNS risolve correttamente (dig/nslookup)
- [ ] Certificato SSL ottenuto (certbot)
- [ ] Tutti i servizi up (`docker compose ps`)
- [ ] HTTPS funziona (`curl -I https://passaportoenergetico.it`)
- [ ] Frontend accessibile (browser)
- [ ] Upload funziona (test con file)
- [ ] Admin login funziona
- [ ] Health check OK (`curl https://passaportoenergetico.it/health`)

---

## Note Produzione

1. **Backup:** Configura backup automatico del database (cron job + script)
2. **Monitoring:** Considera aggiungere monitoring (Prometheus/Grafana o servizi cloud)
3. **Updates:** Aggiorna regolarmente immagini Docker e sistema operativo
4. **Logs:** I log sono in JSON strutturato, considera centralizzazione (ELK, Loki, etc.)
5. **Rate limiting:** Attivo (1 req/sec, burst 10). Per traffico alto, considera Redis-based
6. **Storage:** Se usi S3, configura backup automatico del bucket
