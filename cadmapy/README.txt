CADMA.py - Instalación y Uso

Autor: Eduardo Gabriel Guzmán López (eggl.quimica@gmail.com)


REQUISITOS PREVIOS

Debes tener instalado:
- Python 3.10, 3.11 o 3.12 (no versiones anteriores ni posteriores)


VERIFICAR SI TIENES PYTHON INSTALADO

Windows:
  1. Abre: Inicio > Buscar "cmd"
  2. En la ventana que se abre, escribe: python --version
  3. Si ves un número como "Python 3.10.x", ya tienes Python

macOS / Linux:
  1. Abre Terminal
  2. Escribe: python3 --version
  3. Si ves un número como "Python 3.10.x", ya tienes Python


DESCARGAR E INSTALAR PYTHON (si no lo tienes)

Windows:
  1. Ve a https://www.python.org/downloads/
  2. Descarga Python 3.10, 3.11 o 3.12
  3. Ejecuta el archivo descargado
  4. IMPORTANTE: Marca la casilla "Add Python to PATH" durante la instalación
  5. Completa la instalación
  6. Reinicia la computadora

macOS:
  1. Abre Terminal
  2. Copia y pega esto en Terminal:
     brew install python@3.10
  3. Espera a que termine

Linux (Ubuntu/Debian):
  1. Abre Terminal
  2. Copia y pega esto:
     sudo apt update
     sudo apt install python3.10
  3. Escribe tu contraseña cuando te lo pida

Linux (Fedora/RHEL):
  1. Abre Terminal
  2. Copia y pega esto:
     sudo dnf install python3.10
  3. Escribe tu contraseña cuando te lo pida


DESCOMPRIMIR EL ARCHIVO

Windows:
  1. Descargaste CADMA-py_v1.0.0.zip
  2. Haz clic derecho sobre el archivo
  3. Selecciona "Extraer todo..."
  4. Elige una carpeta (por ejemplo Descargas)
  5. Espera a que termine

macOS / Linux:
  El archivo debería descomprimirse automáticamente al descargarlo
  Si no, haz doble clic sobre el archivo ZIP


INSTALAR CADMA.PY
     Si llegán a ocurrir errores estos aparecerán escritos en la terminal; en la sección final de este documento se dan soluciones para errores típicos
     
Windows:
  1. Abre: Inicio > Buscar "cmd"
  2. En la ventana que se abre, cambia a la carpeta donde descomprimiste:
     cd Descargas
     cd CADMA-py_v1.0.0
  3. Ejecuta:
     setup.bat
  4. Espera a que termine (puede tardar 5-10 minutos)
  5. Verás un mensaje de éxito al final

macOS: 
  1. Abre Terminal
  2. Cambia a la carpeta donde descomprimiste:
     cd ~/Downloads
     cd CADMA-py_v1.0.0
  3. Ejecuta:
     bash setup.sh
  4. Espera a que termine
  5. Verás un mensaje de éxito al final

Linux:
  1. Abre Terminal
  2. Cambia a la carpeta donde descomprimiste:
     cd ~/Downloads
     cd CADMA-py_v1.0.0
  3. Ejecuta:
     bash setup.sh
  4. Espera a que termine (puede tardar 5-10 minutos)
  5. Verás un mensaje de éxito al final


EJECUTAR CADMA.PY

Windows:
  1. Abre: Inicio > Buscar "cmd"
  2. Cambia a la carpeta:
     cd Descargas
     cd CADMA-py_v1.0.0
  3. Ejecuta:
     run.bat
  4. La aplicación debería abrirse

macOS / Linux:
  1. Abre Terminal
  2. Cambia a la carpeta:
     cd ~/Downloads
     cd CADMA-py_v1.0.0
  3. Ejecuta:
     bash run.sh
  4. La aplicación debería abrirse


SI ALGO FALLA

Error: "Python no encontrado"
  - Reinstala Python desde https://www.python.org
  - En Windows: marca "Add Python to PATH" durante instalación
  - Reinicia la computadora después de instalar

Error: "Tkinter no está disponible" (macOS)
  - Abre Terminal y ejecuta:
    brew install python-tk@3.10
  - Luego intenta instalar de nuevo:
    cd (carpeta donde está CADMA)
    bash setup.sh

Error: "Tkinter no está disponible" (Linux Ubuntu/Debian)
  - Abre Terminal y ejecuta:
    sudo apt install python3.10-tk
  - Luego intenta instalar de nuevo:
    cd (carpeta donde está CADMA)
    bash setup.sh

Error: "Tkinter no está disponible" (Linux Fedora/RHEL)
  - Abre Terminal y ejecuta:
    sudo dnf install python3.10-tkinter
  - Luego intenta instalar de nuevo:
    cd (carpeta donde está CADMA)
    bash setup.sh

Si nada funciona:
  - Usa Conda (si la tienes instalada):
    conda env create -f CADMA.yml
    conda activate CADMA
    python CADMA.py
  - O contacta a: eggl.quimica@gmail.com


PRÓXIMAS VECES

Después de instalar, para ejecutar CADMA.py otra vez:

Windows:
  1. Abre cmd
  2. cd Descargas/CADMA-py_v1.0.0
  3. run.bat

macOS / Linux:
  1. Abre Terminal
  2. cd ~/Downloads/CADMA-py_v1.0.0
  3. bash run.sh

- INSTALL.md - Guía detallada de instalación
- QUICKSTART.md - Referencia rápida
- CADMApy.pdf - Manual completo
