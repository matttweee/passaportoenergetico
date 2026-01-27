# Quick Deploy Checklist - Passaporto Energetico

## Setup VPS (una volta)

```bash
# 1. Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
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

# 5. Genera SECRET_KEY
openssl rand -hex 32
# Copia output in .env.production.local -> SECRET_KEY
```

## DNS (Cloudflare - CONSIGLIATO)

### Nel registrar (TopHost):
1. Vai a "DNS" / "Nameserver"
2. Sostituisci con nameserver Cloudflare:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```

### In Cloudflare:
1. Aggiungi sito `passaportoenergetico.it`
2. DNS → Records:
   - **A** `@` → `INSERISCI_IP_VPS` (Proxied ON)
   - **CNAME** `www` → `@` (Proxied ON)

### Verifica DNS:
```bash
dig +short passaportoenergetico.it
# Atteso: IP VPS (o IP Cloudflare se Proxied)
```

## SSL (Let's Encrypt)

```bash
# 1. Installa certbot
sudo apt install -y certbot python3-certbot-nginx

# 2. Crea directory challenge
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# 3. Ottieni certificato (SOLO DOPO DNS configurato)
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it \
  --email TUO_EMAIL@example.com \
  --agree-tos \
  --non-interactive
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

# Browser
# Apri: https://passaportoenergetico.it
```

## Troubleshooting

```bash
# Logs
docker compose -f docker-compose.production.yml logs -f

# Restart
docker compose -f docker-compose.production.yml restart

# Shell in container
docker compose -f docker-compose.production.yml exec backend bash
```
