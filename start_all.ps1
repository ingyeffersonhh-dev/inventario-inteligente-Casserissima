# CASSERISSIMA 2.0 - Arranque Unificado Integral (PowerShell)
# Ejecuta backend FastAPI, frontend Next.js y el Agente de Telegram IA en paralelo
# Uso: .\start_all.ps1

Write-Host ""
Write-Host "  ========================================================" -ForegroundColor DarkYellow
Write-Host "         CASSERISSIMA 2.0 - Ecosistema Integral           " -ForegroundColor DarkYellow  
Write-Host "     Backend Predictivo + Frontend + Agente de Telegram   " -ForegroundColor DarkYellow
Write-Host "  ========================================================" -ForegroundColor DarkYellow
Write-Host ""

$ROOT = $PSScriptRoot

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

# -- Backend ------------------------------------------------------------------
Write-Host "  [1/3] Iniciando Backend Python (FastAPI)..." -ForegroundColor Cyan

$backendDir = Join-Path $ROOT "backend"

# Copiar .env si no existe
if (-not (Test-Path "$backendDir\.env")) {
    if (Test-Path "$backendDir\.env.example") {
        Copy-Item "$backendDir\.env.example" "$backendDir\.env"
        Write-Host "  [OK] .env creado desde .env.example en backend" -ForegroundColor Green
    }
}

# Crear carpeta de modelos ML
$modelsDir = Join-Path $backendDir "data\models"
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
    Write-Host "  [OK] Carpeta data/models creada" -ForegroundColor Green
}

$backendJob = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile", "-Command",
    "cd '$backendDir'; $pythonCmd -m uvicorn main:app --reload --port 8000 --host 0.0.0.0"
) -PassThru -WindowStyle Normal

Write-Host "  [OK] Backend arrancando en http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# -- Frontend ------------------------------------------------------------------
Write-Host "  [2/3] Iniciando Frontend Next.js..." -ForegroundColor Cyan

$frontendDir = Join-Path $ROOT "frontend"
$frontendJob = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile", "-Command",
    "cd '$frontendDir'; npm run dev"
) -PassThru -WindowStyle Normal

Write-Host "  [OK] Frontend arrancando en http://localhost:3000" -ForegroundColor Green
Write-Host ""

# -- Agente IA -----------------------------------------------------------------
Write-Host "  [3/3] Iniciando Agente IA de Telegram y Servidor FastMCP..." -ForegroundColor Cyan

# Esperar unos segundos para asegurar que el backend levantó
Start-Sleep -Seconds 3

$agentDir = "C:\Users\Yefferson\Documents\project\agente de ia casserissima"

if (-not (Test-Path "$agentDir\.env")) {
    if (Test-Path "$agentDir\.env.example") {
        Copy-Item "$agentDir\.env.example" "$agentDir\.env"
        Write-Host "  [!] .env creado en el Agente. Recuerda colocar el TELEGRAM_TOKEN." -ForegroundColor Yellow
    }
}

$agentJob = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile", "-Command",
    "cd '$agentDir'; $pythonCmd main.py"
) -PassThru -WindowStyle Normal

Write-Host "  [OK] Servidor MCP del Agente arrancando en http://localhost:8001/sse" -ForegroundColor Green
Write-Host ""


Write-Host "  --------------------------------------------------" -ForegroundColor DarkGray
Write-Host "    Dashboard (Next.js) -> http://localhost:3000       " -ForegroundColor White
Write-Host "    API Docs (FastAPI)  -> http://localhost:8000/docs  " -ForegroundColor White
Write-Host "    Agente IA (FastMCP) -> http://localhost:8001/sse   " -ForegroundColor White
Write-Host "                                             " -ForegroundColor DarkGray
Write-Host "    Ctrl+C o cierra esta ventana para detener todo     " -ForegroundColor DarkGray
Write-Host "  --------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Esperando... " -ForegroundColor DarkGray

# Mantener el proceso padre vivo
try {
    Wait-Process -Id $backendJob.Id, $frontendJob.Id, $agentJob.Id -ErrorAction SilentlyContinue
} catch {
    # Si uno termina, terminar los demás
    if (!$backendJob.HasExited)  { Stop-Process -Id $backendJob.Id  -Force }
    if (!$frontendJob.HasExited) { Stop-Process -Id $frontendJob.Id -Force }
    if (!$agentJob.HasExited)    { Stop-Process -Id $agentJob.Id    -Force }
}
