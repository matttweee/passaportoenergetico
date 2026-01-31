# Deploy su Google Cloud VM - Istruzioni

## Situazione Attuale
- **VM IP**: 34.30.131.94
- **OS**: Ubuntu
- **Docker**: Già installato
- **Repository**: https://github.com/matttweee/passaportoenergetico

## Procedura Completa

### 1. Connettiti alla VM via SSH

**Opzione A: Da Google Cloud Console**
1. Vai su https://console.cloud.google.com
2. Compute Engine > VM instances
3. Trova la VM con IP 34.30.131.94
4. Clicca "SSH" (icona terminale)

**Opzione B: Da terminale locale**
```bash
gcloud compute ssh NOME_VM --zone=ZONA
# oppure
ssh utente@34.30.131.94
```

### 2. Esegui lo script di deploy

Una volta connesso via SSH, esegui:

```bash
# Scarica lo script (se non è già nel repo)
curl -O https://raw.githubusercontent.com/matttweee/passaportoenergetico/main/deploy-gcp.sh
# oppure, se il repo è già clonato:
cd ~/passaportoenergetico
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

**Oppure esegui manualmente questi comandi:**

```bash
# Step 1: Clona repository
cd ~
rm -rf passaportoenergetico
git clone https://github.com/matttweee/passaportoenergetico.git
cd passaportoenergetico

# Step 2: Crea configurazione
cp .env.production .env.production.local

# Step 3: Genera password e configura
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)

# Edita .env.production.local
nano .env.production.local
# Sostituisci:
#   SECRET_KEY=INSERISCI_SECRET_KEY_QUI → SECRET_KEY=$SECRET_KEY
#   POSTGRES_PASSWORD=INSERISCI_PASSWORD_QUI → POSTGRES_PASSWORD=$POSTGRES_PASSWORD
#   ADMIN_PASSWORD=INSERISCI_PASSWORD_QUI → ADMIN_PASSWORD=$ADMIN_PASSWORD
#   BASE_URL=https://passaportoenergetico.it → BASE_URL=http://34.30.131.94
#   CORS_ORIGINS=... → CORS_ORIGINS=http://34.30.131.94

# Step 4: Crea directory
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# Step 5: Avvia servizi
docker compose -f docker-compose.production.yml --env-file .env.production.local up -d --build

# Step 6: Verifica
docker compose -f docker-compose.production.yml ps
curl http://localhost:8000/health
```

### 3. Configura Firewall GCP (se accesso esterno non funziona)

Se `curl http://34.30.131.94/health` non funziona dall'esterno:

1. Vai su https://console.cloud.google.com
2. Seleziona il progetto corretto
3. Vai a: **VPC network** > **Firewall**
4. Clicca **"Create Firewall Rule"**
5. Compila:
   - **Name**: `allow-http-https`
   - **Direction**: `Ingress`
   - **Targets**: `All instances in the network`
   - **Source IP ranges**: `0.0.0.0/0`
   - **Protocols and ports**:
     - ☑ **TCP**: `80`
     - ☑ **TCP**: `443`
6. Clicca **"Create"**

**Oppure via gcloud CLI:**
```bash
gcloud compute firewall-rules create allow-http-https \
  --allow tcp:80,tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP and HTTPS"
```

### 4. Verifica Deploy

```bash
# Dalla VM
curl http://localhost:8000/health

# Dall'esterno (dal tuo PC)
curl http://34.30.131.94/health
```

**Atteso:** `{"ok": true, "checks": {"database": "ok", "storage": "ok"}}`

### 5. Accesso al sito

Apri browser: `http://34.30.131.94`

---

## Prossimi Passi (Dopo Deploy Base)

### 1. Configura DNS
- Aggiungi record A: `passaportoenergetico.it` → `34.30.131.94`
- Aggiungi CNAME: `www` → `passaportoenergetico.it`

### 2. Ottieni SSL (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone \
  -d passaportoenergetico.it \
  -d www.passaportoenergetico.it \
  --email tua@email.com
```

### 3. Aggiorna .env.production.local
```bash
nano .env.production.local
# Cambia:
#   BASE_URL=https://passaportoenergetico.it
#   CORS_ORIGINS=https://passaportoenergetico.it,https://www.passaportoenergetico.it
```

### 4. Riavvia servizi
```bash
docker compose -f docker-compose.production.yml restart
```

---

## Troubleshooting

### Container non partono
```bash
docker compose -f docker-compose.production.yml logs
```

### Porta già in uso
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
# Se necessario, ferma servizi esistenti
```

### Database non si connette
```bash
docker compose -f docker-compose.production.yml logs postgres
docker compose -f docker-compose.production.yml exec postgres psql -U pe -d passaporto_energetico -c "SELECT 1;"
```

### Frontend non risponde
```bash
docker compose -f docker-compose.production.yml logs frontend
```

---

## Comandi Utili

```bash
# Log in tempo reale
docker compose -f docker-compose.production.yml logs -f

# Restart tutto
docker compose -f docker-compose.production.yml restart

# Stop tutto
docker compose -f docker-compose.production.yml down

# Rebuild
docker compose -f docker-compose.production.yml up -d --build

# Shell in container
docker compose -f docker-compose.production.yml exec backend bash
```
