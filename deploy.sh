#!/bin/bash
# Script di deploy produzione - Passaporto Energetico
# Esegui su VPS Ubuntu 24.04

set -e

echo "=== Deploy Passaporto Energetico ==="

# Verifica che siamo nella directory corretta
if [ ! -f "docker-compose.production.yml" ]; then
    echo "ERRORE: Esegui questo script da /opt/passaportoenergetico"
    exit 1
fi

# Verifica .env.production.local
if [ ! -f ".env.production.local" ]; then
    echo "ERRORE: Crea .env.production.local da .env.production e configura i valori"
    exit 1
fi

# Build immagini
echo "Building images..."
docker compose -f docker-compose.production.yml build --no-cache

# Avvia servizi
echo "Starting services..."
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d

# Attendi che tutto parta
echo "Waiting for services to start..."
sleep 30

# Verifica health
echo "Checking health..."
docker compose -f docker-compose.production.yml exec backend curl -s http://localhost:8000/health || echo "Health check failed, check logs"

echo "=== Deploy completato ==="
echo "Verifica con: docker compose -f docker-compose.production.yml ps"
echo "Logs: docker compose -f docker-compose.production.yml logs -f"
