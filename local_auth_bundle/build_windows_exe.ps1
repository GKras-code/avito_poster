$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

$pyInstallerArgs = @(
  '--noconfirm'
  '--onefile'
  '--name', 'AvitoLocalAuth'
  '--collect-all', 'playwright'
  'avito_local_auth.py'
)

python -m PyInstaller @pyInstallerArgs

Copy-Item -Force .\dist\AvitoLocalAuth.exe .\AvitoLocalAuth.exe
Write-Host "Built .\AvitoLocalAuth.exe"