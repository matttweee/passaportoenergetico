# Checklist Deploy Produzione - Passaporto Energetico

## Pre-Deploy (sul tuo PC)

- [ ] Repository completo e funzionante localmente
- [ ] `docker compose up --build` funziona
- [ ] Test manuali passati

---

## FASE 1: Setup VPS

- [ ] VPS Ubuntu 24.04 accessibile via SSH
- [ ] IP pubblico del VPS noto: `_________________`

### Installazione Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Rientra via SSH
docker --version
docker compose version
```

- [ ] Docker installato e funzionante

### Directory applicazione
```bash
sudo mkdir -p /opt/passaportoenergetico
sudo chown $USER:$USER /opt/passaportoenergetico
cd /opt/passaportoenergetico
```

- [ ] Directory creata

### Copia repository
```bash
# Opzione A: Git
git clone TUO_REPO_URL .

# Opzione B: SCP (dal PC)
# scp -r /path/to/repo/* user@VPS_IP:/opt/passaportoenergetico/
```

- [ ] Repository copiato

### Configurazione env
```bash
cp .env.production .env.production.local
nano .env.production.local
```

**Valori da cambiare:**
- `POSTGRES_PASSWORD` = `_________________`
- `ADMIN_PASSWORD` = `_________________`
- `SECRET_KEY` = `_________________` (genera con: `openssl rand -hex 32`)

- [ ] `.env.production.local` configurato

---

## FASE 2: DNS (PRIMA di SSL)

### Opzione A: Cloudflare (CONSIGLIATA)

- [ ] Account Cloudflare creato
- [ ] Sito `passaportoenergetico.it` aggiunto
- [ ] Nameserver Cloudflare ottenuti:
  - `ns1.cloudflare.com`
  - `ns2.cloudflare.com`

**Nel registrar (TopHost):**
- [ ] Nameserver sostituiti con quelli Cloudflare
- [ ] Atteso 5-60 minuti per propagazione

**In Cloudflare:**
- [ ] Record A: `@` → `INSERISCI_IP_VPS` (Proxied ON)
- [ ] Record CNAME: `www` → `@` (Proxied ON)

**Verifica:**
```bash
dig +short passaportoenergetico.it
# Atteso: IP VPS o IP Cloudflare
```

- [ ] DNS risolve correttamente

### Opzione B: DNS Diretto

**Nel registrar:**
- [ ] Record A: `@` → `INSERISCI_IP_VPS`
- [ ] Record CNAME: `www` → `@`
- [ ] Atteso 5-60 minuti per propagazione

**Verifica:**
```bash
dig +short passaportoenergetico.it
# Atteso: IP VPS
```

- [ ] DNS risolve correttamente

---

## FASE 3: SSL (Let's Encrypt)

### Installazione Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

- [ ] Certbot installato

### Directory challenge
```bash
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot
```

- [ ] Directory creata

### Ottieni certificato
```bash
# Usa script o manuale (vedi DEPLOY-PRODUCTION.md FASE 3.2)
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it \
  --email TUO_EMAIL@example.com \
  --agree-tos \
  --non-interactive
```

- [ ] Certificato ottenuto
- [ ] Verificato: `sudo ls /etc/letsencrypt/live/passaportoenergetico.it/`

### Rinnovo automatico
```bash
sudo certbot renew --dry-run
```

- [ ] Rinnovo automatico configurato

---

## FASE 4: Deploy Servizi

### Build
```bash
cd /opt/passaportoenergetico
docker compose -f docker-compose.production.yml build
```

- [ ] Build completata senza errori

### Avvio
```bash
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d
```

- [ ] Servizi avviati

### Verifica
```bash
docker compose -f docker-compose.production.yml ps
# Tutti i servizi devono essere "Up"
```

- [ ] Tutti i servizi up

---

## FASE 5: Verifica Finale

### DNS
```bash
dig +short passaportoenergetico.it
dig +short www.passaportoenergetico.it
```

- [ ] DNS risolve

### HTTPS
```bash
curl -I http://passaportoenergetico.it
# Atteso: 301 redirect

curl -I https://passaportoenergetico.it
# Atteso: 200 OK
```

- [ ] HTTP → HTTPS redirect funziona
- [ ] HTTPS funziona

### Health Check
```bash
curl https://passaportoenergetico.it/health
# Atteso: {"ok": true, "checks": {"database": "ok", "storage": "ok"}}
```

- [ ] Health check OK

### Frontend
- [ ] Browser: `https://passaportoenergetico.it` → Landing page visibile

### Upload
- [ ] Test upload 1-2 file → Funziona, nessun 413/415

### Admin
- [ ] `https://passaportoenergetico.it/admin` → Login funziona
- [ ] Admin submissions visibili

---

## Troubleshooting

### DNS non risolve
- [ ] Verifica nameserver: `dig NS passaportoenergetico.it +short`
- [ ] Attendi propagazione (5-60 min)
- [ ] Controlla registrar per "dnsHold"

### 502 Bad Gateway
```bash
docker compose -f docker-compose.production.yml logs backend
docker compose -f docker-compose.production.yml logs frontend
docker compose -f docker-compose.production.yml logs nginx
```

- [ ] Log verificati, problema risolto

### Upload 413
- [ ] Verificato `client_max_body_size 20m` in nginx config
- [ ] Se Cloudflare Proxied: disattivato o aumentato limite

### Certbot fallisce
- [ ] DNS configurato e risolve
- [ ] Atteso 5-60 minuti dopo DNS
- [ ] Riavviato certbot

---

## Comandi Utili

```bash
# Status
docker compose -f docker-compose.production.yml ps

# Logs
docker compose -f docker-compose.production.yml logs -f

# Restart
docker compose -f docker-compose.production.yml restart

# Rebuild
docker compose -f docker-compose.production.yml up -d --build

# Shell
docker compose -f docker-compose.production.yml exec backend bash
```

---

## ✅ DEPLOY COMPLETATO

Il sito è online su: `https://passaportoenergetico.it`
