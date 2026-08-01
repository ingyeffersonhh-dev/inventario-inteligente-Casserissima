@echo off
cd /d "%~dp0"

REM Detectar si el venv tiene fastapi instalado
.venv\Scripts\python.exe -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] venv sin dependencias. Usando Python global.
    echo         Ejecuta setup.bat para entorno aislado.
    python -m uvicorn main:app --port 8000 --host 0.0.0.0
) else (
    call .venv\Scripts\activate.bat
    echo Iniciando Backend FastAPI en puerto 8000...
    python -m uvicorn main:app --port 8000 --host 0.0.0.0
)
pause