@echo off
cd /d "%~dp0"

REM Detectar si el venv tiene langchain_core instalado
.venv\Scripts\python.exe -c "import langchain_core" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] venv sin dependencias. Usando Python global.
    echo         Ejecuta setup.bat para entorno aislado.
    python main.py
) else (
    call .venv\Scripts\activate.bat
    echo Iniciando Agente IA Telegram + MCP en puerto 8001...
    python main.py
)
pause