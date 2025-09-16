Para poder desarrollar las apps que se tienen en python es necesario primero clonar el repositorio

$ git clone --recurse-submodules https://github.com/CesarGuzmanLopez/Apps-Annia
$ git submodule status --recursive

El archivo environment.yml tiene toda la información de los repositorios usados para crear el environment:
 
$ conda env create -f environment.yml

Abrir el entorno de trabajo:

$ conda activate apps-annia

Y ya se pueden ejecutar todas las apps que uno quiera:

$ python Marcus/main.py


