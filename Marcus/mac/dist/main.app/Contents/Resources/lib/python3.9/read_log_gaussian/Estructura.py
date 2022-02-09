from pathlib import Path
Path(__file__).resolve()

try:
    from Atributes import *
except ImportError:
    from read_log_gaussian.Atributes import *

class Estructura(object):
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
        self.chkPointFil = ChkPointFile()
        self.Atributos.append(self.chkPointFil)
        self.comand = Comando()
        self.Atributos.append(self.comand)
        self.jobtitle = JobTitle()
        self.Atributos.append(self.jobtitle)
        self.frecNeg = FrecuenciaNegativa()
        self.Atributos.append(self.frecNeg)
        self.free_engergy = Free_energy()
        self.Atributos.append(self.free_engergy)
        self.zpe = Zero_point_Energies()
        self.Atributos.append(self.zpe)
        self.eH_ts = Thermal_Enthalpies()
        self.Atributos.append(self.eH_ts)
        self.temp = Temperature()
        self.Atributos.append(self.temp)
        self.isAnOptFreq = IsAnOptFreq()
        self.Atributos.append(self.isAnOptFreq)
        self.scf = SCF()
        self.Atributos.append(self.scf)
        self.zeroPointCorrection = ZeroPointCorrection()
        self.Atributos.append(self.zeroPointCorrection)
        self.thermalCorrectionToEnergy = ThermalCorrectionToEnergy()
        self.Atributos.append(self.thermalCorrectionToEnergy)
        self.thermalcorrectiontoEnthalpy = ThermalcorrectiontoEnthalpy()
        self.Atributos.append(self.thermalcorrectiontoEnthalpy)
        self.thermalCorrectionToGibbs = ThermalCorrectionToGibbs()
        self.Atributos.append(self.thermalCorrectionToGibbs)
        self.iSThermo = ISThermo()
        self.Atributos.append(self.iSThermo)
        self.listaOrbitales = ListaOrbitales()
        self.Atributos.append(self.listaOrbitales)
        self.normalTerm = NormalTermination()
        self.Atributos.append(self.normalTerm)
        self.multFreqs = MultipleFrecuenciaNegativa()
        self.Atributos.append(self.multFreqs)
        self.chargeMultiplicity = ChargeMultiplicity()
        self.Atributos.append(self.chargeMultiplicity)