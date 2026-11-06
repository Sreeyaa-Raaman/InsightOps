# InsightOps Frontend Launch Script
$env:PATH = "$PSScriptRoot\.tools\node;" + $env:PATH
Set-Location "$PSScriptRoot\frontend"
Write-Host "Starting InsightOps React + Vite Frontend on http://localhost:5173..." -ForegroundColor Cyan
npm run dev
