@echo off
setlocal enabledelayedexpansion

echo.
echo   ========================================================
echo          CASSERISSIMA 2.0 - Instalador Portable
echo        Backend + Dashboard + Agente IA Telegram
echo   ========================================================
echo.

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

echo   Raiz detectada: %ROOT%
echo.

REM ── 1. Verificar Python ──────────────────────────────────────
echo   [1/5] Verificando Python (requiere 3.12+)...
where python >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python no encontrado.
    echo          Descarga Python 3.12+ desde: https://python.org
    echo          IMPORTANTE: marca "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
if errorlevel 1 (
    for /f "tokens=1,2" %%a in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)"') do set "PYVER=%%a.%%b"
    echo   [ERROR] Python !PYVER! detectado, necesita 3.12+.
    echo          Descarga: https://python.org/downloads/
    pause
    exit /b 1
)
python --version 2>&1 | findstr /r "[0-9]"
echo   [OK] Python 3.12+ detectado.
echo.

REM ── 2. Verificar Node ────────────────────────────────────────
echo   [2/5] Verificando Node.js (requiere 20+)...
where node >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Node.js no encontrado.
    echo          Descarga Node 20+ LTS desde: https://nodejs.org
    pause
    exit /b 1
)

REM Extraer version mayor de Node (ej: parseInt("v24.15.0".slice(1)) = 24)
for /f %%a in ('node -e "console.log(parseInt(process.version.slice(1)))"') do set "NODE_MAJOR=%%a"
if !NODE_MAJOR! LSS 20 (
    echo   [ERROR] Node v!NODE_MAJOR! detectado, necesita 20+.
    echo          Descarga LTS desde: https://nodejs.org
    pause
    exit /b 1
)
node --version 2>&1 | findstr /r "[0-9]"
echo   [OK] Node 20+ detectado.
echo.

REM ── 3. Backend: venv + pip install ──────────────────────────
echo   [3/5] Instalando Backend (FastAPI)...
set "BACKEND_DIR=%ROOT%\src"
if not exist "%BACKEND_DIR%\.venv" (
    python -m venv "%BACKEND_DIR%\.venv"
    echo   [OK] venv creado para backend.
) else (
    echo   [OK] venv ya existe, reutilizando.
)
echo   Instalando dependencias del backend (puede tardar 2-5 min)...
cd /d "%BACKEND_DIR%"
.venv\Scripts\pip.exe install -r requirements.txt -q
if errorlevel 1 (
    echo   [ERROR] Fallo pip install del backend.
    pause
    exit /b 1
)
echo   [OK] Backend instalado.
echo.

REM ── 4. Agente IA: venv + pip install ────────────────────────
echo   [4/5] Instalando Agente IA (Telegram + MCP)...
set "AGENT_DIR=%ROOT%\agente de ia casserissima"
if not exist "%AGENT_DIR%\.venv" (
    python -m venv "%AGENT_DIR%\.venv"
    echo   [OK] venv creado para agente.
) else (
    echo   [OK] venv ya existe, reutilizando.
)
echo   Instalando dependencias del agente (puede tardar 2-5 min)...
cd /d "%AGENT_DIR%"
.venv\Scripts\pip.exe install -r requirements.txt -q
if errorlevel 1 (
    echo   [ERROR] Fallo pip install del agente.
    pause
    exit /b 1
)
echo   [OK] Agente IA instalado.
echo.

REM ── 5. Frontend: npm install ───────────────────────────────
echo   [5/5] Instalando Dashboard (Next.js)...
set "FRONTEND_DIR=%ROOT%\frontend"
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   Instalando dependencias del frontend (puede tardar 2-5 min)...
    cd /d "%FRONTEND_DIR%"
    call npm install --silent
    if errorlevel 1 (
        echo   [ERROR] Fallo npm install del frontend.
        pause
        exit /b 1
    )
) else (
    echo   [OK] node_modules ya existe, reutilizando.
)
echo   [OK] Dashboard instalado.
echo.

REM ── 6. Crear .env del backend si no existe ─────────────────
if not exist "%BACKEND_DIR%\.env" (
    if exist "%BACKEND_DIR%\.env.example" (
        copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
        echo   [OK] .env del backend creado desde .env.example.
    )
)

REM ── 7. .env del agente ─────────────────────────────────────
if not exist "%AGENT_DIR%\.env" (
    if exist "%AGENT_DIR%\.env.example" (
        copy "%AGENT_DIR%\.env.example" "%AGENT_DIR%\.env" >nul
        echo   [OK] .env del agente creado desde .env.example.
        echo.
        echo   *** IMPORTANTE: Edita el .env del agente y agrega tu TOKEN de Telegram
        echo       y API Key de Gemini antes de iniciar el sistema.
        echo       Archivo: %AGENT_DIR%\.env
    )
) else (
    echo   [OK] .env del agente ya existe.
)

REM ── Verificar DB ───────────────────────────────────────────
if not exist "%BACKEND_DIR%\casserisissima.db" (
    echo.
    echo   *** ADVERTENCIA: No se encontro casserisissima.db en src\
    echo       Copia la base de datos al directorio src\ antes de iniciar.
) else (
    echo   [OK] Base de datos encontrada.
)

REM ── Verificar modelos ML ───────────────────────────────────
if not exist "%ROOT%\data\models" (
    echo   *** ADVERTENCIA: No se encontro la carpeta data\models\
    echo       Sin los modelos .joblib las predicciones no funcionaran.
) else (
    echo   [OK] Modelos ML encontrados.
)

echo.
echo   ========================================================
echo          Instalacion completada.
echo   ========================================================
echo.
echo   Para iniciar el sistema ejecuta:  start.bat
echo.
pause