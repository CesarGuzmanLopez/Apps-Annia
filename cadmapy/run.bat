@echo off
REM ============================================================================
REM run.bat - Ejecuta CADMA.py (detecta automáticamente Conda o venv)
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

set "VENV_DIR=%CD%\venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

REM Detectar si estamos usando Conda
where conda >nul 2>&1
if not errorlevel 1 (
    conda env list | findstr /C:"CADMA" >nul 2>&1
    if not errorlevel 1 (
        echo Activando entorno Conda 'CADMA'...
        call conda activate CADMA
        python CADMA.py
        pause
        exit /b 0
    )
)

REM Si no hay Conda, usar venv
if not exist "%PYTHON%" (
    echo Error: Entorno virtual no encontrado
    echo Por favor ejecuta primero: setup.bat
    pause
    exit /b 1
)

echo Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
python CADMA.py

pause
