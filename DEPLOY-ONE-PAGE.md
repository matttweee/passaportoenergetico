# Deploy Produzione - Passaporto Energetico (One Page)

## Setup VPS

```bash
# 1. Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Rientra via SSH

# 2. Crea directory
sudo mkdir -p /opt/passaportoenergetico
sudo chown $USER:$USER /opt/passaportoenergetico
cd /opt/passaportoenergetico

# 3. Copia repo (sostituisci con tuo metodo)
# git clone TUO_REPO .
# oppure scp/rsync dal PC

# 4. Configura env
cp .env.production .env.production.local
nano .env.production.local
# Cambia: POSTGRES_PASSWORD, ADMIN_PASSWORD, SECRET_KEY
# Genera SECRET_KEY: openssl rand -hex 32

# 5. Directory SSL
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot
```

## DNS (Cloudflare - CONSIGLIATA)

### Nel registrar (TopHost):
1. DNS → Nameserver → Sostituisci con:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
2. Attendi 5-60 minuti

### In Cloudflare:
1. Aggiungi sito `passaportoenergetico.it`
2. DNS → Records:
   - **A** `@` → `INSERISCI_IP_VPS` (Proxied ON)
   - **CNAME** `www` → `@` (Proxied ON)

### Verifica DNS:
```bash
dig +short passaportoenergetico.it
# Atteso: IP VPS o IP Cloudflare
```

## SSL (Let's Encrypt)

```bash
# Installa certbot
sudo apt install -y certbot python3-certbot-nginx

# Ottieni certificato (SOLO DOPO DNS configurato)
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it \
  --email TUO_EMAIL@example.com \
  --agree-tos \
  --non-interactive

# Verifica
sudo ls /etc/letsencrypt/live/passaportoenergetico.it/
```

## Deploy

```bash
cd /opt/passaportoenergetico

# Build
docker compose -f docker-compose.production.yml build

# Avvia
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d

# Verifica
docker compose -f docker-compose.production.yml ps
curl https://passaportoenergetico.it/health
```

## Verifica Finale

```bash
# DNS
dig +short passaportoenergetico.it

# HTTPS
curl -I https://passaportoenergetico.it

# Health
curl https://passaportoenergetico.it/health
```

Apri browser: `https://passaportoenergetico.it`

---

## Troubleshooting

**502 Bad Gateway:**
```bash
docker compose -f docker-compose.production.yml logs backend
docker compose -f docker-compose.production.yml logs frontend
```

**Upload 413:**
- Verifica `client_max_body_size 20m` in nginx config
- Se Cloudflare Proxied: disattiva o aumenta limite

**Certbot fallisce:**
- Verifica DNS: `dig +short passaportoenergetico.it`
- Attendi 5-60 minuti dopo DNS config

**DNS non risolve:**
- Verifica nameserver: `dig NS passaportoenergetico.it +short`
- Controlla registrar per "dnsHold"

---

## File Chiave

- `docker-compose.production.yml` - Compose produzione
- `nginx/production.conf` - Config Nginx
- `.env.production.local` - Variabili ambiente (CAMBIA PASSWORD!)
- `DEPLOY-PRODUCTION.md` - Guida dettagliata
- `DNS-INSTRUCTIONS.md` - Istruzioni DNS complete
