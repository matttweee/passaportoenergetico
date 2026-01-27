# Istruzioni DNS - Passaporto Energetico

## Opzione A: Cloudflare (CONSIGLIATA)

### Vantaggi
- CDN globale (velocità)
- Nasconde IP VPS
- DDoS protection base
- SSL automatico (opzionale, ma usiamo Let's Encrypt)

### Step 1: Aggiungi sito su Cloudflare
1. Vai su https://cloudflare.com
2. Crea account (gratis)
3. Clicca "Add a Site"
4. Inserisci: `passaportoenergetico.it`
5. Scegli piano "Free"
6. Cloudflare ti mostrerà 2 nameserver (es.):
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```

### Step 2: Configura nameserver nel registrar (TopHost o altro)

**Nel pannello del registrar:**
1. Vai a "DNS" / "Nameserver" / "Gestione DNS"
2. Cerca "Nameserver" o "DNS Server"
3. **Sostituisci** i nameserver attuali con quelli di Cloudflare:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
4. Salva
5. **Attendi 5-60 minuti** per propagazione

### Step 3: Aggiungi record DNS in Cloudflare

Nel pannello Cloudflare, vai a "DNS" → "Records" → "Add record":

**Record A (principale):**
- **Type:** `A`
- **Name:** `@` (oppure lascia vuoto, o `passaportoenergetico.it`)
- **IPv4 address:** `INSERISCI_IP_VPS_QUI` (es. `123.45.67.89`)
- **Proxy status:** 
  - **Proxied** (arancione) = CONSIGLIATO (CDN + protezione)
  - **DNS only** (grigio) = se upload fallisce con Proxied
- **TTL:** Auto
- Clicca "Save"

**Record CNAME (www):**
- **Type:** `CNAME`
- **Name:** `www`
- **Target:** `passaportoenergetico.it` (o `@`)
- **Proxy status:** Stesso di A record
- **TTL:** Auto
- Clicca "Save"

### Step 4: Verifica DNS Cloudflare

```bash
# Verifica A record
dig +short passaportoenergetico.it

# Se Proxied ON: vedrai IP Cloudflare (es. 104.x.x.x)
# Se Proxied OFF: vedrai IP VPS

# Verifica CNAME
dig +short www.passaportoenergetico.it

# Verifica nameserver
dig NS passaportoenergetico.it +short
# Atteso: ns1.cloudflare.com, ns2.cloudflare.com
```

### Nota su "Proxied" (arancione vs grigio)

**Proxied ON (arancione):**
- ✅ CDN globale (velocità)
- ✅ Nasconde IP VPS
- ✅ DDoS protection base
- ⚠️ Upload grandi (>15MB) possono fallire se Cloudflare non configurato
- **Fix upload:** Aumenta limite in Cloudflare (Plan → Workers) o disattiva Proxied

**Proxied OFF (grigio):**
- ✅ DNS diretto, nessun proxy
- ✅ Upload sempre funzionanti
- ❌ IP VPS esposto
- ❌ Nessun CDN

**Raccomandazione:** Inizia con **Proxied ON**. Se upload fallisce, passa a **Proxied OFF**.

---

## Opzione B: DNS Diretto (senza Cloudflare)

### Step 1: Configura record nel registrar

Nel pannello del registrar (TopHost, Aruba, Register.it, etc.):

**Vai a "DNS" / "Zone DNS" / "Gestione DNS"**

**Aggiungi Record A:**
- **Type:** `A`
- **Name:** `@` (oppure lascia vuoto, o `passaportoenergetico.it`)
- **Value/IP:** `INSERISCI_IP_VPS_QUI` (es. `123.45.67.89`)
- **TTL:** `3600` (o Auto)

**Aggiungi Record CNAME:**
- **Type:** `CNAME`
- **Name:** `www`
- **Value/Target:** `@` (oppure `passaportoenergetico.it`)
- **TTL:** `3600` (o Auto)

### Step 2: Verifica DNS Diretto

```bash
# Verifica A record
dig +short passaportoenergetico.it
# Atteso: IP VPS

# Verifica CNAME
dig +short www.passaportoenergetico.it
# Atteso: passaportoenergetico.it (o IP VPS se risolto)

# Verifica nameserver (dovrebbero essere quelli del registrar)
dig NS passaportoenergetico.it +short
```

---

## Risoluzione "dnsHold" / "inactive"

### Cosa significa
Il registrar applica un "hold" al dominio finché:
- Nameserver non sono configurati correttamente, OPPURE
- Verifiche/attivazione non sono complete (email, documenti, pagamento)

### Come verificare
```bash
whois passaportoenergetico.it | grep -i hold
```

Se vedi `dnsHold` o `clientHold`, il dominio è bloccato.

### Soluzione step-by-step

1. **Imposta nameserver corretti:**
   - Cloudflare: usa nameserver Cloudflare
   - Diretto: usa nameserver del registrar

2. **Completa attivazione nel registrar:**
   - Verifica email di conferma (se richiesta)
   - Completa documenti/pagamento (se pendenti)
   - Rimuovi "locks" nel pannello

3. **Verifica propagazione:**
   ```bash
   dig NS passaportoenergetico.it +short
   ```
   Se vedi nameserver corretti, il hold è rimosso.

4. **Se persiste:**
   - Contatta supporto registrar
   - Chiedi esplicitamente: "Rimuovi dnsHold/clientHold"
   - Attendi fino a 24h per propagazione completa

---

## Comandi Verifica DNS

```bash
# A record
dig +short passaportoenergetico.it

# CNAME
dig +short www.passaportoenergetico.it

# Nameserver
dig NS passaportoenergetico.it +short

# Tutto insieme
dig passaportoenergetico.it +noall +answer

# Con nslookup (alternativa)
nslookup passaportoenergetico.it
nslookup www.passaportoenergetico.it
```

---

## Timeline Attesa

- **Nameserver change:** 5-60 minuti (tipicamente 15-30 min)
- **DNS records:** 5-60 minuti (tipicamente 10-20 min)
- **dnsHold removal:** Fino a 24h (dipende da registrar)

**Suggerimento:** Dopo aver configurato DNS, attendi almeno 30 minuti prima di eseguire certbot.
