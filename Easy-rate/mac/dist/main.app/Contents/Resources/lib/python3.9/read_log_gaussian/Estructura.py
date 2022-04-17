from pathlib import Path
Path(__file__).resolve()

try:
    from Atributes import *
except ImportError:
    from read_log_gaussian.Atributes import *

class Estructura(object):
    '''
    contain  an Structure execution gaussian
    Attributes
    ----------
    chkPointFil                     %chk=
    comand                       
    jobtitle                        -----#   %chk=p
    frecNeg                         Frequencies --
    free_engergy                    Sum of electronic and thermal Free Energies
    zpe                             Sum of electronic and thermal Free Energies=
    eH_ts                           Sum of electronic and thermal Enthalpies
    temp                            Temperature
    isAnOptFreq                     opt freq
    scf                             SCF Done:
    zeroPointCorrection             Zero-point correction=
    thermalCorrectionToEnergy       thermalCorrectionToEnergy
    thermalcorrectiontoEnthalpy     thermalcorrectiontoEnthalpy
    thermalCorrectionToGibbs        thermalCorrectionToGibbs
    iSThermo                        
    listaOrbitales                  
    normalTerm                      
    multFreqs                       "imaginary frequencies" in line  and "1" not in line:
    chargeMultiplicity              Multiplicity
    '''



    def Add(self,AtributoNuevo :AtributoString =None,AtributosNuevos :"list[AtributoString]" =None ):
        A = Estructura
        self.AtributosNuevos :list[AtributoGeneric]
        if(AtributosNuevos is not None):
            for atributoSTR in AtributosNuevos:
                atrib = AtributoGeneric(atributoSTR.NombreAtributo,atributoSTR.Separador)
                self.Atributos.append(atrib)
                self.AtributosNuevos.appen(atrib)

        if(AtributoNuevo is not None):
            self.Atributos.append(  AtributoGeneric( AtributoNuevo.NombreAtributo, AtributoNuevo.Separador))

    def __str__(self)->string:
        salida=""
        for AtributoActual  in self.Atributos:
            salida += str(AtributoActual) +"\n" if len(str(AtributoActual)) > 0 else ""
        
        return salida

    def __init__(self)->None:
        self.Atributos : list[AtributoGeneric] = list()
        self.chkPointFil = ChkPointFile()#   #p
        self.Atributos.append(self.chkPointFil)
        self.comand = Comando()#   -----
        self.Atributos.append(self.comand)
        self.jobtitle = JobTitle()#   Frequencies --
        self.Atributos.append(self.jobtitle)
        self.frecNeg = FrecuenciaNegativa()#   
        self.Atributos.append(self.frecNeg)
        self.zpe = Zero_point_Energies()#   
        self.Atributos.append(self.zpe)
        self.eH_ts = Thermal_Enthalpies()#   Sum of electronic and thermal Enthalpies
        self.Atributos.append(self.eH_ts)
        self.temp = Temperature()#   Temperature
        self.Atributos.append(self.temp)
        self.isAnOptFreq = IsAnOptFreq()#   opt freq
        self.Atributos.append(self.isAnOptFreq)
        self.scf = SCF()#   SCF Done:
        self.Atributos.append(self.scf)
        
        self.Thermal_Free_Enthalpies = Thermal_Free_Enthalpies()#   Sum of electronic and thermal Free Energies
        self.Atributos.append(self.Thermal_Free_Enthalpies)

        self.zeroPointCorrection = ZeroPointCorrection()#   Zero-point correction=
        self.Atributos.append(self.zeroPointCorrection)
        self.thermalCorrectionToEnergy = ThermalCorrectionToEnergy()#   thermalCorrectionToEnergy
        self.Atributos.append(self.thermalCorrectionToEnergy)
        self.thermalcorrectiontoEnthalpy = ThermalcorrectiontoEnthalpy()#   thermalcorrectiontoEnthalpy
        self.Atributos.append(self.thermalcorrectiontoEnthalpy)
        self.thermalCorrectionToGibbs = ThermalCorrectionToGibbs()#   thermalCorrectionToGibbs
        self.Atributos.append(self.thermalCorrectionToGibbs)
        self.iSThermo = ISThermo()#   
        self.Atributos.append(self.iSThermo)
        self.listaOrbitales = ListaOrbitales()#   
        self.Atributos.append(self.listaOrbitales)
        self.normalTerm = NormalTermination()#   
        self.Atributos.append(self.normalTerm)
        self.multFreqs = MultipleFrecuenciaNegativa()#   "imaginary frequencies" in line  and "1" not in li
        self.Atributos.append(self.multFreqs)
        self.chargeMultiplicity = ChargeMultiplicity()#   Multiplicity
        self.Atributos.append(self.chargeMultiplicity)