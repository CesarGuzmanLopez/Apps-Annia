from pathlib import Path
Path(__file__).resolve()

try:
    from Estructura import *
except ImportError:
    from read_log_gaussian.Estructura import *

class read_log_gaussian(object):
    def __init__(self, filename:string="", AtributoExtra : AtributoString =None, AtrributosExtra:"list[AtributoString]"= None )->None:
        self.Estructuras :list[Estructura] =list()
        self.__filename :string= filename
        self.__AtributoExtra = AtributoExtra
        self.__AtrributosExtra = AtrributosExtra
        self.Analizar()
    
    def Analizar(self)->None:
        self.__Linea =0
        file = open(self.__filename)
        exe:Estructura = None
        for line in file:
            self.__Linea  += 1
            if "Initial command:" in line :
                exe = Estructura()
                exe.Add(self.__AtributoExtra,self.__AtrributosExtra)
                self.Estructuras.append(exe)
            if(exe is not None):
                for i, Atributo in enumerate(exe.Atributos) :
                     
                    if(Atributo.Active and Atributo.Revision_condition(line=line,Actual= exe)):
                        Atributo.Definir(line)
                        Atributo.setLinenum(self.__Linea)
        file.close()    
    
    def __str__(self)->string:
        Salida = ""
        for i, exe in enumerate(self.Estructuras):
            Salida += str(i)+ " "+ exe.__str__() +"\n--------------------\n"
        return Salida