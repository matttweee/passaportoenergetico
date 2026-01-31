#!/bin/bash
# Script di deploy automatico per Google Cloud VM
# Esegui questo script nella sessione SSH della VM

set -e

echo "=========================================="
echo "DEPLOY PASSAPORTO ENERGETICO - GCP VM"
echo "=========================================="

# Step 1: Clona repository
echo ""
echo "STEP 1: Clonando repository..."
cd ~
rm -rf passaportoenergetico
git clone https://github.com/matttweee/passaportoenergetico.git
cd passaportoenergetico
echo "✓ Repository clonato"

# Step 2: Crea file configurazione
echo ""
echo "STEP 2: Creando file configurazione..."
cp .env.production .env.production.local
echo "✓ File .env.production.local creato"

# Step 3: Genera SECRET_KEY e configura .env
echo ""
echo "STEP 3: Configurando variabili ambiente..."
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)

# Backup del file originale
cp .env.production.local .env.production.local.backup

# Sostituisce i valori (usa sed per compatibilità)
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env.production.local
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$POSTGRES_PASSWORD|g" .env.production.local
sed -i "s|ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$ADMIN_PASSWORD|g" .env.production.local
sed -i "s|BASE_URL=.*|BASE_URL=http://34.30.131.94|g" .env.production.local
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://34.30.131.94|g" .env.production.local

echo "✓ SECRET_KEY generata: ${SECRET_KEY:0:16}..."
echo "✓ POSTGRES_PASSWORD generata"
echo "✓ ADMIN_PASSWORD generata"
echo "✓ BASE_URL impostata a http://34.30.131.94"
echo "✓ CORS_ORIGINS impostata"

# Mostra le password generate (per riferimento)
echo ""
echo "⚠️  PASSWORD GENERATE (salva queste informazioni!):"
echo "   ADMIN_PASSWORD: $ADMIN_PASSWORD"
echo "   POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "   SECRET_KEY: $SECRET_KEY"
echo ""

# Step 4: Crea directory necessarie
echo ""
echo "STEP 4: Creando directory necessarie..."
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot 2>/dev/null || sudo chown -R $USER /var/www/certbot
echo "✓ Directory create"

# Step 5: Build e avvio servizi
echo ""
echo "STEP 5: Building e avviando servizi Docker..."
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d --build

echo ""
echo "Attendendo che i servizi si avviino..."
sleep 15

# Step 6: Verifica container
echo ""
echo "STEP 6: Verificando container..."
docker compose -f docker-compose.production.yml ps

# Step 7: Verifica health check
echo ""
echo "STEP 7: Verificando health check..."
sleep 10

# Prova health check su diverse porte
HEALTH_OK=false
for port in 8000 3000 80; do
    if curl -f -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✓ Health check OK su porta $port"
        HEALTH_OK=true
        break
    fi
done

if [ "$HEALTH_OK" = false ]; then
    echo "⚠️  Health check non risponde ancora, controlla i log:"
    echo "   docker compose -f docker-compose.production.yml logs"
else
    echo "✓ Health check funzionante"
fi

# Step 8: Verifica accesso esterno
echo ""
echo "STEP 8: Verificando accesso esterno..."
EXTERNAL_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip)
echo "IP pubblico rilevato: $EXTERNAL_IP"

if curl -f -s --max-time 5 http://34.30.131.94/health > /dev/null 2>&1; then
    echo "✓ Accesso esterno funzionante!"
else
    echo "⚠️  Accesso esterno non funzionante - verifica firewall GCP"
    echo ""
    echo "🔴 AZIONE MANUALE RICHIESTA:"
    echo "   1. Vai su https://console.cloud.google.com"
    echo "   2. Seleziona il progetto corretto"
    echo "   3. Vai a: VPC network > Firewall"
    echo "   4. Clicca 'Create Firewall Rule'"
    echo "   5. Nome: allow-http-https"
    echo "   6. Direction: Ingress"
    echo "   7. Targets: All instances in the network"
    echo "   8. Source IP ranges: 0.0.0.0/0"
    echo "   9. Protocols and ports:"
    echo "      - ☑ TCP: 80"
    echo "      - ☑ TCP: 443"
    echo "   10. Clicca 'Create'"
    echo ""
    echo "   Oppure, se esiste già una regola, verifica che permetta:"
    echo "   - Porta 80 (HTTP)"
    echo "   - Porta 443 (HTTPS)"
fi

echo ""
echo "=========================================="
echo "DEPLOY COMPLETATO"
echo "=========================================="
echo ""
echo "URL: http://34.30.131.94"
echo "Health: http://34.30.131.94/health"
echo ""
echo "Prossimi passi:"
echo "1. Configura DNS per passaportoenergetico.it"
echo "2. Ottieni certificato SSL (Let's Encrypt)"
echo "3. Aggiorna BASE_URL e CORS_ORIGINS in .env.production.local"
echo ""
echo "Per vedere i log:"
echo "  docker compose -f docker-compose.production.yml logs -f"
echo ""
echo "Per riavviare:"
echo "  docker compose -f docker-compose.production.yml restart"
echo ""
