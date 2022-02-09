from pathlib import Path
Path(__file__).resolve()
try:
    from Atributo import *
except ImportError:
    from read_log_gaussian.Atributo import *

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ChkPointFile(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Value :string =""

    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("%chk=" in line):
            return True
        return False
    
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = line.split("=")[1]
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "ChkPoint File : " + self._Value
        else:
            return ""
'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class MultipleFrecuenciaNegativa(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("imaginary frequencies" in line) and "1" not in line:
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value :int = int(self.Num_extract(line))
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Number of negative frequencies: "+str(self._Value)
        else:
            return ""

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class FrecuenciaNegativa(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self.Contiene :bool =False


    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        self.Contiene = "1 imaginary frequencies" in line or self.Contiene
        return (self.Contiene and not self._Found) and ("Frequencies --" in line)
       
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Imaginary frequency: "+ str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class Free_energy(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Sum of electronic and thermal Free Energies= " in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Sum of electronic and thermal Free Energies: " + str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class Zero_point_Energies(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Sum of electronic and zero-point Energies=" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Sum of electronic and zero-point Energies: "+ str(self._Value) 
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class Thermal_Enthalpies(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Sum of electronic and thermal Enthalpies=" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Sum of electronic and thermal Enthalpies : "+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class Temperature(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Temperature " in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active= False
        self._Found = True
    
    def __str__(self):
        if(self._Found):
            return "Temperature: "+str(self._Value ) + "K"
        else:
            return ""
    @property
    def incelsius(self):
        return self._Value-273.15

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class NormalTermination(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Found =True
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Normal termination of Gaussian" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value:bool = True
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Value):
            return ""
        else:
            return "Error termination"
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class Comando(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Value = ""
        self.__Actual ="PasoVerificado.No"
        self.__ValueTemp :string =""
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if self.__Actual  == "PasoVerificado.No"  and " ---------------" in line :
            self.__Actual = "PasoVerificado.Anterior"
            return False
        if(self.__Actual == "PasoVerificado.Anterior"  ):
            if("#p" in line ):
                self.__Actual = "PasoVerificado.Siguiente"
                return True
            else:
                self.__Actual = "PasoVerificado.No"
                return False
        if(self.__Actual == "PasoVerificado.Siguiente"):
            if(" ---------------" in line):
                self._Value = self.__ValueTemp
                self._Found=True
                self._Active=False
                return False
            else:
                self.__Actual = "PasoVerificado.No"
                self.__ValueTemp=""
                return False 
        return False

    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self.__ValueTemp = line
        
    
    def __str__(self):
        if(self._Found):
            return "comand: "+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class IsAnOptFreq(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("opt freq" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value:bool = True
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "OPT Freq ?: "+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class SCF(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("SCF Done: " in line):
            return True  
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        x= line.split(" ")[7]
        if(  x[len(x)-1].isdigit()): 
            self._Value = self.Numbers_extract(line=x)[0]
        self._Active=True
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "SCF Energy: "+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ISThermo(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Thermochemistry" in line):
            return False
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value:bool = True
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "IS Thermo: "+str(self._Value)
        else:
            return ""
            
'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ZeroPointCorrection(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Zero-point correction=" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):

            return "Zero-point correction="+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ThermalCorrectionToEnergy(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Thermal correction to Energy=" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Thermal correction to Energy="+str(self._Value)
        else:
            return ""
        
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ThermalcorrectiontoEnthalpy(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Thermal correction to Enthalpy=" in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Thermal correction to Enthalpy="+str(self._Value)
        else:
            return ""

'''
 --------
 CH3OOH_2
 --------
'''

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class JobTitle(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Value = ""
        self.__Actual ="PasoVerificado.No"
        self.__ValueTemp :string =""
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if self.__Actual  == "PasoVerificado.No"  and " --------\n" == line :
            self.__Actual = "PasoVerificado.Anterior"
            return False
        if(self.__Actual == "PasoVerificado.Anterior"  ):
            if(" " in line ):
                self.__Actual = "PasoVerificado.Siguiente"
                return True
            else:
                self.__Actual = "PasoVerificado.No"
                return False
        if(self.__Actual == "PasoVerificado.Siguiente"):
            if(' --------\n' == line):
                self._Value = self.__ValueTemp
                self._Found=True
                self._Active=False
                return False
            else:
                self.__Actual = "PasoVerificado.No"
                self.__ValueTemp=""
                return False 
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self.__ValueTemp = line
        
    
    def __str__(self):
        if(self._Found):
            return "Job Title: "+str(self._Value)
        else:
            return ""
'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ChargeMultiplicity(AtributoGeneric):
    class C_M(object):
        def __init__(self,C:float, M:float):
            self.Charge :float=C
            self.Multiplicity :float = M
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Value: self.C_M  
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Charge" in line and "Multiplicity "in line):
            return True
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value :self.C_M= self.C_M(self.Numbers_extract(line)[0],self.Numbers_extract(line)[1]) 
        self._Active=False
        self._Found =True
    @property
    def Multiplicity(self):
        return self._Value.Multiplicity
    @property 
    def Charge(self):
        self._Value.Charge
    def __str__(self):
        if(self._Found):
            return "Charge: "+self._Value.Charge+ " Multiplicity: "+self._Value.Multiplicity
        else:
            return ""

    
'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ThermalCorrectionToGibbs(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Thermal correction to Gibbs Free Energy=" in line):
            return False
        return False
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        self._Value = self.Num_extract(line=line)
        self._Active=False
        self._Found =True
    
    def __str__(self):
        if(self._Found):
            return "Thermal correction to Gibbs Free Energy: "+str(self._Value)
        else:
            return ""


class Orbitales(object):
    def __init__(self)->None:    
        self.A   : list[float]  = list()
        self.AL  : list[float]  = list()
        self.B   : list[float]  = list()
        self.BL  : list[float]  = list()
    

'''
    A class represent
    Attributes
    ----------
    getValue
        the value of the attribute
    
'''
class ListaOrbitales(AtributoGeneric):
    def __init__(self, PalabraABuscar: string = None, Separator: string = None):
        super().__init__(PalabraABuscar, Separator)
        self._Value :list[Orbitales] = list()
        self.Orbital_LineActual:string = "X"
        self.OrbitalActualUltimo :Orbitales = None

    def Revision_condition(self, line: string, Actual: object =None) -> bool:
        if("Population analysis using the SCF density" in line):
            self.OrbitalActualUltimo = Orbitales()
            self._Value :list[Orbitales] = list()
            self._Value.append(self.OrbitalActualUltimo)
            self._Active=True
            self._Found =True
            return False
        if(self._Found):
            if("Alpha  occ. eigenvalues --"in line):
                self.Orbital_LineActual = "A"
            elif("Alpha virt. eigenvalues --"in line):
                self.Orbital_LineActual = "AL"
            elif("Beta  occ. eigenvalues --"in line):
                self.Orbital_LineActual = "B"
            elif("Beta virt. eigenvalues --"in line):
                self.Orbital_LineActual = "BL"
            else:
                self.Orbital_LineActual = "X"
        if(self.Orbital_LineActual !="X"):
            return True
        return False   
    def Definir(self, line: string, multiline: bool = False, brakword: bool = False) -> None:
        Orbitales:list[float]
        if(self.Orbital_LineActual is "A") :
            Orbitales =self.OrbitalActualUltimo.A
        if(self.Orbital_LineActual is "AL"):
            Orbitales =self.OrbitalActualUltimo.AL
        if(self.Orbital_LineActual is "B") :
            Orbitales =self.OrbitalActualUltimo.B
        if(self.Orbital_LineActual is "BL"):
            Orbitales =self.OrbitalActualUltimo.BL
        Orbitales.extend(self.Numbers_extract(line))

    def __str__(self)->string:
        if(not self._Found):
            return ""
        salida =" "
        salida += "\n  Last set of orbitals out of a total of: "+str(len(self._Value))+"\n"
        i=0
        if(len(self.OrbitalActualUltimo.A)>0):
            salida += "***************** Alpha  occ. eigenvalues***************\n"
        for a in self.OrbitalActualUltimo.A :
            salida += str(a) 
            i+=1
            if(i%5 == 0):
                salida += "\n"
            else:
                salida += "\t"
                if(len(str(a))<8): salida+="\t"
        salida +="\n\n"
        i=0 
        
        if(len(self.OrbitalActualUltimo.AL)>0):
            salida += "*****************Alpha virt. eigenvalues *****************\n"
        for a in self.OrbitalActualUltimo.AL :
            salida += str(a) 
            i+=1
            if(i%5 == 0):
                salida += "\n"
            else:
                salida += "\t"
                if(len(str(a))<8): salida+="\t"
        salida +="\n\n"
        i=0

        if(len(self.OrbitalActualUltimo.B)>0):
            salida += "***************** Beta  occ. eigenvalue*****************\n"
        for a in self.OrbitalActualUltimo.B :
            salida += str(a) 
            i+=1
            if(i%5 == 0):
                salida += "\n"
            else:
                salida += "\t"
                if(len(str(a))<8): salida+="\t"
        salida +="\n\n"
        i=0

        if(len(self.OrbitalActualUltimo.BL)>0):
            salida += "*****************Beta virt. eigenvalues *****************\n"
        for a in self.OrbitalActualUltimo.BL :
            salida += str(a) 
            i+=1
            if(i%5 == 0):
                salida += "\n"
            else:
                salida += "\t"
                if(len(str(a))<8): salida+="\t"
        i=0

        return salida

