# InsightOps Backend Launch Script
$env:PYTHONPATH = "$PSScriptRoot\backend"
Write-Host "Starting InsightOps FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
& "C:\Users\Sreeyaa\AppData\Local\Programs\Python\Python315\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
