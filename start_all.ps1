# InsightOps Launch Both Backend & Frontend
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         INSIGHTOPS – AI DATA ANALYST AGENT               " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "1. Starting Backend at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "2. Starting Frontend at http://localhost:5173" -ForegroundColor Green
Write-Host "3. API Documentation at http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\run_backend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\run_frontend.ps1"

Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"
