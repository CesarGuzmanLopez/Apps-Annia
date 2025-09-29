Para compilar en mac y crear el ejecutable:

pyinstaller main.py --name "EasyRate" --windowed --osx-bundle-identifier com.eggl.easyrate

Si tuvieras un logo:

pyinstaller main.py --name "EasyRate" --windowed --icon=icon.icns --osx-bundle-identifier com.eggl.easyrate
pyinstaller main.py --name "EasyRate" --windowed --icon=icon.ico --osx-bundle-identifier com.eggl.easyrate


Para poder desarrollar las apps que se tienen en python es necesario primero clonar el repositorio

$ git clone --recurse-submodules https://github.com/CesarGuzmanLopez/Apps-Annia
$ git submodule status --recursive

El archivo environment.yml tiene toda la información de los repositorios usados para crear el environment:
 
$ conda env create -f environment.yml

Abrir el entorno de trabajo:

$ conda activate apps-annia

Y ya se pueden ejecutar todas las apps que uno quiera:

$ python Marcus/main.py

Cuando se hayan hecho modificaciones, se puede verificar el status de esas modificaciones git status,
esto indicará que archivos estánd mdificados y deben actualizarse en el repositorio:

$ git status


Nota: Cuando se hace un commit se desincroniza del repositorio, para sincronizarlo haciendo push, si quieresmos saber si nuestra versión 
es más antiguao más actualizada que laprincipal del repositorio usamo git log, por ejemp: Aquí estáás actualizada mi versión local que la del repitorio
porque mi HEAD está más arra que el HEAD de origin (servidor)

"""
commit d354acc2915ece09c63c6637331adbdf60e963f8 (HEAD)
Author: Eduardo Guzman <edagulo@hotmail.com>
Date:   Fri Sep 26 19:21:29 2025 -0600

    Actualizar_python_mac_CK

commit b631bd2b8a1b530ed81258785cacbee30514b769 (origin/main, origin/HEAD, main)
Author: CesarGuzman <47696662+CesarGuzmanLopez@users.noreply.github.com>
Date:   Thu May 12 01:50:27 2022 -0500

    agregar
"""

Si mi versió es más actualizada que la del HE:main debo hacer git push al main:

$ git push origin HEAD:main

�Cómo sabmos si alguien más ya hizo cambios en elrepositorio y que estoy en la versión más actualiza?
Esto me actualizará lasversiones de los demás que estén edindo:

$git fetch		#Esto te dice si hay cambios en cualquier rama
$git pull 		#Esto te descarga los cambios más actualizados de larama en la que estás.


Si se hicieron modificaciones se pueden regresar al repositorio

git add . 
git commit -m "Actualizar_python"
git push




