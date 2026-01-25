#!/bin/bash
################################################################################
# CADMA.py - Setup Script para Linux y macOS
# Verifica Python, crea venv e instala dependencias desde requirements.txt
################################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_CMD=""

# Funciones
print_header() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_conda() {
    if command -v conda >/dev/null 2>&1; then
        # Verificar si existe el entorno CADMA
        if conda env list | grep -q "^CADMA "; then
            print_info "Entorno Conda 'CADMA' detectado"
            return 0
        fi
    fi
    return 1
}

check_python_version() {
    local cmd=$1
    local version_output
    version_output=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
    
    if [[ -z "$version_output" ]]; then
        return 1
    fi
    
    # Convertir versión a número comparable (3.10 -> 310, 3.9 -> 39)
    local version_num=$(echo "$version_output" | tr -d '.')
    
    # Requiere Python 3.10 a 3.13 (3.14+ tiene problemas de compatibilidad con algunas librerías)
    if [[ $version_num -ge 310 ]] && [[ $version_num -le 313 ]]; then
        echo "$version_output"
        return 0
    fi
    return 1
}

select_python() {
    local candidates=()
    local uname_s
    uname_s="$(uname -s)"
    
    if [[ "$uname_s" == "Darwin" ]]; then
        # macOS: buscar Python 3.10, 3.11, 3.12 en orden
        candidates+=("/opt/homebrew/bin/python3.10" \
                     "/usr/local/bin/python3.10" \
                     "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3" \
                     "/opt/homebrew/bin/python3.11" \
                     "/usr/local/bin/python3.11" \
                     "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3" \
                     "/opt/homebrew/bin/python3.12" \
                     "/usr/local/bin/python3.12" \
                     "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3")
    fi
    
    # PATH: python3.10, python3.11, python3.12, python3.13, etc.
    if command -v python3.10 >/dev/null 2>&1; then
        candidates+=("$(command -v python3.10)")
    fi
    if command -v python3.11 >/dev/null 2>&1; then
        candidates+=("$(command -v python3.11)")
    fi
    if command -v python3.12 >/dev/null 2>&1; then
        candidates+=("$(command -v python3.12)")
    fi
    if command -v python3.13 >/dev/null 2>&1; then
        candidates+=("$(command -v python3.13)")
    fi
    
    # Intentar python3 genérico
    if command -v python3 >/dev/null 2>&1; then
        candidates+=("$(command -v python3)")
    fi
    
    # Intentar python genérico
    if command -v python >/dev/null 2>&1; then
        candidates+=("$(command -v python)")
    fi

    for cmd in "${candidates[@]}"; do
        if [[ -x "$cmd" ]] || command -v "$cmd" >/dev/null 2>&1; then
            local py_version
            py_version=$(check_python_version "$cmd")
            if [[ $? -eq 0 ]]; then
                PYTHON_CMD="$cmd"
                PYTHON_VERSION="$py_version"
                return 0
            fi
        fi
    done
    return 1
}

# 1. Verificar Python y Conda
print_header "Verificando Python"

# Opción 1: Usar Conda si está disponible
if check_conda; then
    print_success "Usando entorno Conda 'CADMA'"
    echo ""
    echo "Para activar el entorno y ejecutar:"
    echo "  conda activate CADMA"
    echo "  python CADMA.py"
    echo ""
    echo "O simplemente ejecuta:"
    echo "  bash run.sh"
    echo ""
    exit 0
fi

# Opción 2: Usar Python estándar con venv
print_info "Conda no detectado, configurando con Python estándar..."

if ! select_python; then
    print_error "No se encontró Python 3.10 a 3.13"
    echo ""
    echo "CADMA.py requiere Python 3.10 a 3.13."
    echo "(Python 3.14+ aún no es totalmente compatible con todas las dependencias)"
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ OPCIÓN 1: Usa Conda (RECOMENDADO - más fácil)   │"
    echo "└─────────────────────────────────────────────────┘"
    echo "  conda env create -f CADMA.yml"
    echo "  conda activate CADMA"
    echo "  python CADMA.py"
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ OPCIÓN 2: Instala Python 3.10 a 3.13            │"
    echo "└─────────────────────────────────────────────────┘"
    echo ""
    echo "macOS:"
    echo "  1. Instala Python desde python.org o Homebrew:"
    echo "     brew install python@3.10"
    echo "  2. Luego ejecuta este script de nuevo"
    echo ""
    echo "Linux (Ubuntu/Debian):"
    echo "  1. Instala Python:"
    echo "     sudo apt update"
    echo "     sudo apt install python3.10 python3.10-venv python3.10-tk"
    echo "  2. Luego ejecuta este script de nuevo"
    echo ""
    echo "Linux (Fedora/RHEL):"
    echo "  1. Instala Python:"
    echo "     sudo dnf install python3.10 python3.10-venv python3-tkinter"
    echo "  2. Luego ejecuta este script de nuevo"
    echo ""
    echo "Windows:"
    echo "  1. Descarga Python 3.10 desde python.org"
    echo "  2. Marca 'Add Python to PATH' durante la instalación"
    echo "  3. Reinicia la terminal y ejecuta: setup.bat"
    echo ""
    exit 1
fi

print_success "Python $PYTHON_VERSION encontrado: $PYTHON_CMD"

# 2. Verificar Tkinter en el Python del sistema (ANTES de crear venv)
print_header "Verificando Tkinter"

set +e  # Deshabilitar salida automática en error
"$PYTHON_CMD" -c "import tkinter" 2>/dev/null
tkinter_result=$?
set -e  # Rehabilitar salida automática en error

if [ $tkinter_result -ne 0 ]; then
    echo ""
    echo "✗ ¡ERROR! Tkinter no está disponible en $PYTHON_CMD"
    echo ""
    echo "Tkinter es requerido para la interfaz gráfica de CADMA."
    echo ""
    
    uname_s="$(uname -s)"
    
    if [[ "$uname_s" == "Darwin" ]]; then
        echo "SOLUCIÓN para macOS:"
        echo "  brew install python-tk@3.10"
        echo ""
        echo "Luego ejecuta de nuevo:"
        echo "  bash setup.sh"
    elif [[ "$uname_s" == "Linux" ]]; then
        echo "SOLUCIÓN para Linux:"
        echo ""
        echo "Ubuntu/Debian:"
        echo "  sudo apt install python3.10-tk"
        echo ""
        echo "Fedora/RHEL:"
        echo "  sudo dnf install python3.10-tkinter"
        echo ""
        echo "Luego ejecuta de nuevo:"
        echo "  bash setup.sh"
    fi
    echo ""
    echo "ALTERNATIVA: Usa Conda (incluye Tkinter automáticamente):"
    echo "  bash run.sh"
    echo ""
    exit 1
fi
print_success "Tkinter OK"

# 3. Crear venv
print_header "Creando entorno virtual"

if [ -d "$VENV_DIR" ]; then
    print_info "Entorno virtual ya existe, actualizando..."
else
    print_info "Creando venv en $VENV_DIR"
    "$PYTHON_CMD" -m venv "$VENV_DIR"
fi

print_success "Entorno virtual OK"

# 3. Activar venv
print_info "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"
print_success "Entorno activado"

# 4. Actualizar pip
print_header "Actualizando pip"
python -m pip install --upgrade pip > /dev/null 2>&1
print_success "pip actualizado"

# 5. Instalar dependencias
print_header "Instalando dependencias"

if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    print_error "requirements.txt no encontrado"
    exit 1
fi

python -m pip install -r "$SCRIPT_DIR/requirements.txt"
print_success "Dependencias instaladas"

# 6. Verificar módulos
print_header "Verificando módulos"

# Verificar módulos científicos
python -c "import pandas; import numpy; import rdkit; import matplotlib; import py3Dmol" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Problema al cargar módulos científicos"
    exit 1
fi
print_success "Módulos científicos OK"

print_header "✓ SETUP COMPLETADO"
echo ""
echo "Para ejecutar CADMA.py:"
echo ""
echo "  Opción 1 (automático):"
echo "    bash run.sh"
echo ""
echo "  Opción 2 (manual):"
echo "    source venv/bin/activate"
echo "    python CADMA.py"
echo ""
