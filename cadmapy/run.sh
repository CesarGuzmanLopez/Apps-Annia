#!/bin/bash
################################################################################
# run.sh - Ejecuta CADMA.py (detecta automáticamente Conda o venv)
################################################################################

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"

# Detectar si estamos usando Conda
if command -v conda >/dev/null 2>&1; then
    if conda env list | grep -q "^CADMA "; then
        echo "Activando entorno Conda 'CADMA'..."
        eval "$(conda shell.bash hook)"
        conda activate CADMA
        cd "$SCRIPT_DIR"
        python CADMA.py
        exit $?
    fi
fi

# Si no hay Conda, usar venv
PYTHON="$VENV_DIR/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "Error: Entorno virtual no encontrado"
    echo "Por favor ejecuta primero: bash setup.sh"
    exit 1
fi

echo "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"
cd "$SCRIPT_DIR"
python CADMA.py

deactivate 2>/dev/null || true
