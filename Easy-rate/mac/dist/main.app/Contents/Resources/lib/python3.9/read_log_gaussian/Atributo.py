import math
from pathlib import Path
from abc import abstractmethod
from cmath import nan
import string
from tkinter.ttk import Separator
from typing import Sequence
import re

class Atributo(object):
    '''
    A class 'abstract' to represnt to element of interest 
    of log chk
    Attributes
    ----------
    _Value : float 
        el valor obtenido del documento en crudo
    _Active: boolean  
        si se sigue buscando el valor
    _found: boolean 
        si se encontro el valor en el ducumento
    _LineNum:integer 
        numero de linea donde se encontro el valor
    
    Methods
    -----------
    Revision_condition(self,line :string,Actual: Ejecucion )->bool:
        regresa si se debe seguir buscando el numero
    Define_Revision(line:string, )
        define la linea de busqueda la palabra a buscar
    Number_extract( self, line:string )->float:
        extrae el primer numero del string seleccionado
    setLinenum( self, line:string )->float:
        extrae el primer numero del string seleccionado


    '''
    __regex_Get_Numbers = r"([-+]?[0-9]*\.?[0-9]*e?[0-9]*d?[0-9]+)"
    
    def __init__(self):
        self._Value   =nan
        self._Active  =True
        self._Found   =False
        self._LineNum =nan

    @abstractmethod
    def Revision_condition(self,line :string,Actual: object )->bool:
        pass
    
    @abstractmethod
    def Define_Revision(self,line :string ="",multiline:bool = False,brakword:bool = False)->None:
        pass
    
    def Num_extract( self, line:string )->float:
        x = re.compile(self.__regex_Get_Numbers)
        return float(x.findall(line)[0]) 
    
    def Numbers_extract( self, line:string )->Sequence[float]:
        x = re.compile(self.__regex_Get_Numbers)
        return x.findall(line)
    @property
    def Active(self):
        return self._Active
    def setLinenum(self, num:int):
        return self._LineNum

    def __str__(self)->string:
        return str(self.__value)


class AtributoGeneric(Atributo):
    '''
    A class represent am execute read of file 
    Attributes
    ----------
    __PalabraABuscar: String
        La palabra a buscar en el .log
    _Separador:string
        El caracter que separa la palabra con el palabrar
    '''
    def __init__(self,PalabraABuscar:string =None,Separator:string=None)->None:
        super().__init__() 
        self.__PalabraABuscar:string = PalabraABuscar
        self._Separator:string = Separator
        self.__Words =[]
    
    def Revision_condition(self,line :string,Actual: object )->bool:
        self.__Words.append(Actual)
        if(len(self.__Words) >= 10):
            self.__Words.pop
        if (self.__PalabraABuscar in line  and (self._Separator == None or self._Separator =="")) :
            return True
        return False
        
    def Definir(self, line :string):
        if(self.__PalabraABuscar ==None) :
            return
        if(self.__PalabraABuscar in line ):
            self._Value = self.Num_extract(line)
            self._Active = False
            self._Found = True
    def __str__(self)->string:
        if(self._Found):
            return  self.__PalabraABuscar + " = " + str(self._Value)
        return ""
    @property
    def getValue(self):
        return self._Value
    
    @property
    def no_nan_value(self)->float:
        """
        return of _Value if not nan else 0
        """
        if(math.isnan(self._Value)):
            return 0
        return self._Value




class AtributoString(object):
    def __init__(self,NombreAtributo:string,Separador:string):
        self.NombreAtributo = NombreAtributo
        self.Separador =Separador
    def __str__(self)->string:
            return  self.NombreAtributo + self.separator