# Start Hospital Management System Server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Hospital Management System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
Write-Host "Starting Django development server..." -ForegroundColor Yellow
Write-Host ""
python manage.py runserver
