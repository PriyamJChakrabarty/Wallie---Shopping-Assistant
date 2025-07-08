# Voice Assistant Setup Script for Windows
# Run this script in PowerShell to set up the voice assistant

Write-Host "Setting up Wallie Voice Assistant..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 1: Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`nStep 2: Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`nStep 3: Setting up database..." -ForegroundColor Yellow
npm run db:push

Write-Host "`nStep 4: Seeding database with products..." -ForegroundColor Yellow
node lib/seed.js

Write-Host "`nStep 5: Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path "config.py")) {
    Copy-Item "config_template.py" "config.py"
    Write-Host "Created config.py from template. Please update it with your settings." -ForegroundColor Cyan
} else {
    Write-Host "config.py already exists." -ForegroundColor Green
}

Write-Host "`nSetup complete! " -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update config.py with your Gemini API key and settings"
Write-Host "2. Start the Next.js development server: npm run dev"
Write-Host "3. In another terminal, run the voice assistant: python test.py"
Write-Host ""
