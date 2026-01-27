#!/bin/bash
# Script per ottenere certificato SSL (Let's Encrypt)
# Esegui DOPO aver configurato DNS

set -e

DOMAIN="passaportoenergetico.it"
EMAIL="${1}"

if [ -z "$EMAIL" ]; then
    echo "ERRORE: Fornisci email come argomento"
    echo "Uso: ./setup-ssl.sh tua@email.com"
    exit 1
fi

echo "=== Setup SSL per $DOMAIN ==="

# Verifica DNS
echo "Verificando DNS..."
IP=$(dig +short $DOMAIN)
if [ -z "$IP" ]; then
    echo "ERRORE: DNS non risolve. Configura DNS prima di continuare."
    exit 1
fi
echo "DNS OK: $DOMAIN -> $IP"

# Crea directory challenge
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# Avvia nginx temporaneo per challenge (se non già avviato)
if ! docker ps | grep -q nginx-temp; then
    echo "Avviando nginx temporaneo per challenge..."
    docker run -d --name nginx-temp \
      -p 80:80 \
      -v /var/www/certbot:/var/www/certbot:ro \
      nginx:alpine \
      sh -c "echo 'server { listen 80; location /.well-known/acme-challenge/ { root /var/www/certbot; } location / { return 200 \"OK\"; } }' > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
    sleep 2
fi

# Ottieni certificato
echo "Ottenendo certificato SSL..."
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d $DOMAIN \
  -d www.$DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --non-interactive

# Ferma nginx temporaneo
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

# Verifica certificato
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✓ Certificato ottenuto con successo!"
    echo "Percorso: /etc/letsencrypt/live/$DOMAIN/"
else
    echo "ERRORE: Certificato non trovato"
    exit 1
fi

echo "=== Setup SSL completato ==="
echo "Ora avvia i servizi con:"
echo "  docker compose -f docker-compose.production.yml --env-file .env.production.local up -d"
