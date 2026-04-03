# Hospital Management System - Activation Script
# Run this script to activate virtual environment and start server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Hospital Management System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:80000/" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Admin: admin / admin123" -ForegroundColor White
Write-Host "  Patient: john_doe / password123" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
