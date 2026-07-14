$ErrorActionPreference = "Stop"

Write-Host "====================================="
Write-Host "      AEGON Setup Script"
Write-Host "====================================="

Write-Host "`n[1/2] Setting up Backend..."
Set-Location -Path "$PSScriptRoot\..\backend"
python -m venv venv
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "`n[2/2] Setting up Frontend..."
Set-Location -Path "$PSScriptRoot\..\frontend"
npm install

Write-Host "`n====================================="
Write-Host "Setup Complete! You can now run the pipeline."
Write-Host "====================================="
