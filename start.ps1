# CASSERISSIMA 2.0 - Arranque Unificado (PowerShell)
# Ejecuta backend FastAPI y frontend Next.js en paralelo
# Uso: .\start.ps1

Write-Host ""
Write-Host "  ================================================" -ForegroundColor DarkYellow
Write-Host "         CASSERISSIMA 2.0 - Motor Predictivo      " -ForegroundColor DarkYellow  
Write-Host "          Pasteleria Venezolana - IA Engine       " -ForegroundColor DarkYellow
Write-Host "  ================================================" -ForegroundColor DarkYellow
Write-Host ""

$ROOT = $PSScriptRoot

# -- Backend ------------------------------------------------------------------
Write-Host "  [1/2] Iniciando Backend Python (FastAPI)..." -ForegroundColor Cyan

$backendDir = Join-Path $ROOT "src"

# Copiar .env si no existe
if (-not (Test-Path "$backendDir\.env")) {
    Copy-Item "$backendDir\.env.example" "$backendDir\.env"
    Write-Host "  [OK] .env creado desde .env.example" -ForegroundColor Green
}

# Crear carpeta de modelos ML
$modelsDir = Join-Path $ROOT "data\models"
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
    Write-Host "  [OK] Carpeta data/models creada" -ForegroundColor Green
}

# Detectar la versión correcta de Python
$pythonCmd = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    # Probar si py -3.12 está disponible
    $null = & py -3.12 -c "import sys" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "py -3.12"
        Write-Host "  [OK] Detectado Python 3.12 launcher (py -3.12)" -ForegroundColor Green
    }
}

$backendJob = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile", "-Command",
    "cd '$backendDir'; $pythonCmd -m uvicorn main:app --reload --port 8000 --host 0.0.0.0"
) -PassThru -WindowStyle Normal

Write-Host "  [OK] Backend arrancando en http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# -- Frontend ------------------------------------------------------------------
Write-Host "  [2/2] Iniciando Frontend Next.js..." -ForegroundColor Cyan

$frontendDir = Join-Path $ROOT "frontend"
$frontendJob = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile", "-Command",
    "cd '$frontendDir'; npm run dev"
) -PassThru -WindowStyle Normal

Write-Host "  [OK] Frontend arrancando en http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "  --------------------------------------------" -ForegroundColor DarkGray
Write-Host "    Dashboard -> http://localhost:3000       " -ForegroundColor White
Write-Host "    API Docs  -> http://localhost:8000/docs  " -ForegroundColor White
Write-Host "                                             " -ForegroundColor DarkGray
Write-Host "    Ctrl+C para detener ambos servicios      " -ForegroundColor DarkGray
Write-Host "  --------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Esperando... (cierra esta ventana para detener todo)" -ForegroundColor DarkGray

# Mantener el proceso padre vivo
try {
    Wait-Process -Id $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
} catch {
    # Si uno termina, terminar el otro
    if (!$backendJob.HasExited)  { Stop-Process -Id $backendJob.Id  -Force }
    if (!$frontendJob.HasExited) { Stop-Process -Id $frontendJob.Id -Force }
}
