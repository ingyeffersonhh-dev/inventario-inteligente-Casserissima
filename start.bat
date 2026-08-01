@echo off
setlocal

echo.
echo   ========================================================
echo          CASSERISSIMA 2.0 - Iniciar Sistema
echo        Backend + Dashboard + Agente IA Telegram
echo   ========================================================
echo.

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "BACKEND_DIR=%ROOT%\src"
set "AGENT_DIR=%ROOT%\agente de ia casserissima"
set "FRONTEND_DIR=%ROOT%\frontend"

REM -- Verificar DB (unico check realmente bloqueante) -----------
if not exist "%BACKEND_DIR%\casserisissima.db" (
    echo   [ERROR] No se encontro casserisissima.db en src\
    echo          Copia la base de datos a: %BACKEND_DIR%\
    pause
    exit /b 1
)

echo   Iniciando 3 servicios...
echo.

REM -- 1. Backend FastAPI (puerto 8000) ------------------------
echo   [1/3] Backend FastAPI  :  http://localhost:8000/docs
start "CASSERISSIMA - Backend" /d "%BACKEND_DIR%" run.bat

REM -- 2. Frontend Next.js (puerto 3000) -----------------------
echo   [2/3] Dashboard Next.js  :  http://localhost:3000
start "CASSERISSIMA - Dashboard" /d "%FRONTEND_DIR%" cmd /k npm run dev

REM -- Esperar a que el backend suba ---------------------------
timeout /t 5 /nobreak >nul

REM -- 3. Agente IA (Telegram + MCP puerto 8001) ---------------
echo   [3/3] Agente IA Telegram  :  puerto 8001 (MCP SSE)
start "CASSERISSIMA - Agente IA" /d "%AGENT_DIR%" run.bat

echo.
echo   ========================================================
echo          Sistema iniciado.
echo   ========================================================
echo.
echo   Dashboard  :  http://localhost:3000
echo   API Docs   :  http://localhost:8000/docs
echo   Agente IA  :  Escribir al bot de Telegram (escanear QR)
echo.
echo   Cierra las 3 ventanas abiertas para detener todo.
echo.
pause