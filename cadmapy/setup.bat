@echo off
REM ============================================================================
REM CADMA.py - Setup Script para Windows
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

set "VENV_DIR=%CD%\venv"

echo.
echo ===============================================================================
echo                    CADMA.py - Setup para Windows
echo ===============================================================================
echo.

REM 1. Verificar Conda primero
echo [*] Verificando Conda...

where conda >nul 2>&1
if not errorlevel 1 (
    REM Conda está disponible, verificar si existe el entorno CADMA
    conda env list | findstr /C:"CADMA" >nul 2>&1
    if not errorlevel 1 (
        echo [+] Entorno Conda 'CADMA' detectado
        echo.
        echo Para activar el entorno y ejecutar:
        echo   conda activate CADMA
        echo   python CADMA.py
        echo.
        echo O simplemente ejecuta:
        echo   run.bat
        echo.
        pause
        exit /b 0
    ) else (
        echo [i] Conda detectado pero sin entorno 'CADMA'
        echo [i] Puedes crear el entorno con: conda env create -f CADMA.yml
        echo [i] Continuando con instalación usando Python estándar...
        echo.
    )
) else (
    echo [i] Conda no detectado, usando Python estándar...
)

REM 2. Verificar Python
echo.
echo [*] Verificando Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Error: Python no encontrado o no está en el PATH
    echo.
    echo Instala Python 3.10 o superior desde:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marca "Add Python to PATH" durante la instalación
    echo.
    echo O usa Conda (recomendado para este proyecto):
    echo   conda env create -f CADMA.yml
    echo   conda activate CADMA
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [+] Python !PYTHON_VERSION! detectado

REM 2. Crear venv
echo.
echo [*] Creando entorno virtual...

if exist "%VENV_DIR%" (
    echo [+] Entorno virtual ya existe
) else (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [+] Entorno virtual creado
)

REM 3. Activar venv
echo.
echo [*] Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [+] Entorno activado

REM 4. Actualizar pip
echo.
echo [*] Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1
echo [+] pip actualizado

REM 5. Instalar dependencias
echo.
echo [*] Instalando dependencias...

if not exist "%CD%\requirements.txt" (
    echo Error: requirements.txt no encontrado
    pause
    exit /b 1
)

python -m pip install -r "%CD%\requirements.txt"
if errorlevel 1 (
    echo Error: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [+] Dependencias instaladas

REM 6. Verificar
echo.
echo [*] Verificando instalación...

python -c "import pandas; import numpy; import rdkit; import matplotlib; import py3Dmol" >nul 2>&1
if errorlevel 1 (
    echo Error: Problema al cargar módulos
    pause
    exit /b 1
)
echo [+] Todos los módulos cargados correctamente

echo.
echo ===============================================================================
echo                    SETUP COMPLETADO EXITOSAMENTE
echo ===============================================================================
echo.
echo Para ejecutar CADMA.py:
echo.
echo   Opción 1 (automático):
echo     run.bat
echo.
echo   Opción 2 (manual):
echo     venv\Scripts\activate.bat
echo     python CADMA.py
echo.

pause
