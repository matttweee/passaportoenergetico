# Test manuali per Passaporto Energetico (PowerShell)
# Esegui dopo: docker compose up

$BASE_URL = "http://localhost:8000"

Write-Host "=== 1) Health Check ===" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
$health | ConvertTo-Json -Depth 10

Write-Host "`n=== 2) Crea Submission ===" -ForegroundColor Cyan
$subBody = @{
    email = "test@example.com"
    phone = ""
    consent = $true
} | ConvertTo-Json

$subResp = Invoke-RestMethod -Uri "$BASE_URL/api/submissions" -Method Post -Body $subBody -ContentType "application/json"
$subResp | ConvertTo-Json -Depth 10
$subId = $subResp.id
Write-Host "Submission ID: $subId" -ForegroundColor Green

if (-not $subId) {
    Write-Host "ERRORE: Submission non creata" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 3) Upload File ===" -ForegroundColor Cyan
Write-Host "NOTA: Sostituisci il path del file" -ForegroundColor Yellow
# $filePath = ".\testdata\bolletta.pdf"
# $form = @{
#     file = Get-Item -Path $filePath
# }
# Invoke-RestMethod -Uri "$BASE_URL/api/submissions/$subId/files?kind=latest" -Method Post -Form $form

Write-Host "`n=== 4) Avvia Analisi ===" -ForegroundColor Cyan
$analyzeResp = Invoke-RestMethod -Uri "$BASE_URL/api/submissions/$subId/analyze" -Method Post
$analyzeResp | ConvertTo-Json -Depth 10

Write-Host "`n=== 5) Poll Stato (attendi 5s) ===" -ForegroundColor Cyan
Start-Sleep -Seconds 5
$statusResp = Invoke-RestMethod -Uri "$BASE_URL/api/submissions/$subId/status" -Method Get
$statusResp | ConvertTo-Json -Depth 10
$shareToken = $statusResp.share_token

if ($shareToken) {
    Write-Host "`n=== 6) Report Pubblico ===" -ForegroundColor Cyan
    $report = Invoke-RestMethod -Uri "$BASE_URL/api/report/$shareToken" -Method Get
    $report | ConvertTo-Json -Depth 10
} else {
    Write-Host "Analisi non ancora completata. Riprova più tardi." -ForegroundColor Yellow
}

Write-Host "`n=== Test completati ===" -ForegroundColor Green
