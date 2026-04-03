# Start VitalBook Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VitalBook Frontend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting React development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure Django backend is running at:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

Set-Location frontend
npm run dev
