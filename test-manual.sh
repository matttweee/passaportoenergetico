#!/bin/bash
# Test manuali per Passaporto Energetico
# Esegui dopo: docker compose up

BASE_URL="http://localhost:8000"

echo "=== 1) Health Check ==="
curl -s "$BASE_URL/health" | jq .

echo -e "\n=== 2) Crea Submission ==="
SUB_RESP=$(curl -s -X POST "$BASE_URL/api/submissions" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","phone":"","consent":true}')
echo "$SUB_RESP" | jq .
SUB_ID=$(echo "$SUB_RESP" | jq -r '.id')
echo "Submission ID: $SUB_ID"

if [ "$SUB_ID" == "null" ] || [ -z "$SUB_ID" ]; then
  echo "ERRORE: Submission non creata"
  exit 1
fi

echo -e "\n=== 3) Upload File (sostituisci con path file reale) ==="
echo "NOTA: Sostituisci ./testdata/bolletta.pdf con un file reale"
# curl -s -X POST "$BASE_URL/api/submissions/$SUB_ID/files?kind=latest" \
#   -F "file=@./testdata/bolletta.pdf" | jq .

echo -e "\n=== 4) Avvia Analisi ==="
ANALYZE_RESP=$(curl -s -X POST "$BASE_URL/api/submissions/$SUB_ID/analyze")
echo "$ANALYZE_RESP" | jq .

echo -e "\n=== 5) Poll Stato (attendi 5s) ==="
sleep 5
STATUS_RESP=$(curl -s "$BASE_URL/api/submissions/$SUB_ID/status")
echo "$STATUS_RESP" | jq .
SHARE_TOKEN=$(echo "$STATUS_RESP" | jq -r '.share_token // empty')

if [ -n "$SHARE_TOKEN" ] && [ "$SHARE_TOKEN" != "null" ]; then
  echo -e "\n=== 6) Report Pubblico ==="
  curl -s "$BASE_URL/api/report/$SHARE_TOKEN" | jq .
else
  echo "Analisi non ancora completata. Riprova più tardi."
fi

echo -e "\n=== Test completati ==="
