from cmath import nan
from math import exp, log
from os import path
from threading import Thread as thTread
from time import sleep as tsleep
from tkinter import (END, Button, E, Entry, IntVar, Label, Menu, N, S,
                     Scrollbar, Tk, Toplevel, W, filedialog, ttk)
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
from CK.tst import tst
from read_log_gaussian.Estructura import Estructura
from read_log_gaussian.read_log_gaussian import read_log_gaussian
from SeslectStructura import SelectStructure
from tkdialog import WaitAlert
from ttkthemes import ThemedStyle
from viewStructure import ViewStructure

'''
    Python 3.7.9
    @author: Cesar Gerardo Guzman Lopez
    @Description:  Programa easy rate
'''
class EntradaDato(ttk.Frame):
    '''
    Analiza los datos que obtenidos del log gaussian
    '''
    def Activar(self, etiqueta="Sin nombre", buttontext="Browse", dato=0.0, info="", command=None):
        self.__dato = dato
        self.Etiqueta = etiqueta
        self.textoButton = buttontext
        self.Archlog = None
        self.labelEtiquetaNombre = ttk.Label(self, text=self.Etiqueta, width=17)
        self.datoentrada = Entry(self, width=10)
        self.datoentrada.insert(0, str(self.__dato))
        self.datoentrada["state"] = "disabled"
        self.botonActivo = ttk.Button(
            self, text=self.textoButton, width=7, command=self.open)
        self.grid(pady=5)
        self.labelEtiquetaNombre.grid(row=0, column=1)
        self.datoentrada.grid(row=0, column=2)
        self.botonActivo.grid(row=0, column=3)
        self.filname = ""
        self.esperar: int = 0
        self.botonverfile = ttk.Button(
            self, text="view", width=5, command=self.view)
        self.botonverfile.grid(row=0, column=4, padx=4)
        self.botonverfile['state'] = "disabled"

        self.botonclearfile = ttk.Button(
            self, text="clear", width=5, command=self.clear)
        self.botonclearfile.grid(row=0, column=5, padx=4)
        self.botonclearfile['state'] = "disabled"

        self.labelEtiquetafilename = ttk.Label(self, text="")
        self.labelEtiquetafilename.grid(row=1, column=3, columnspan=2, padx=4)
        self.comando = command
        self.EstructuraSeleccionada = None

    def clear(self):
        self.Archlog = None
        self.EstructuraSeleccionada = None
        self.botonverfile['state'] = "disabled"
        self.botonclearfile['state'] = "disabled"
        self.labelEtiquetafilename.config(text="")
        self.datoentrada.config(state='normal')
        self.datoentrada.delete(0, END)  # clear the entry
        self.datoentrada.insert(0, str("0.0"))
        self.datoentrada.config(state='disabled')

    def view(self):
        ViewStructure(master=self, estructure=self.EstructuraSeleccionada)

    def open(self):
        filetypes = [
            ("log Gaussian file",  "*.log"),
            ("txt format Gaussian", "*.txt"),
            ("out Gaussian file",  "*.out")
        ]
        self.mensajeEsperar: WaitAlert
        self.filename = askopenfilename(initialdir=".",
                                        filetypes=filetypes,
                                        title="Choose a file.")
        if(self.filename == ""):
            return
        read = thTread(target=self.readfile)
        read.start()
        while(self.Archlog == None):
            self.esperar = 1
            self.mensajeEsperar = WaitAlert(parent=self,
                                            title='Reading the file',
                                            message='Please wait',
                                            pause=self.esperar)  # show countdown.

        if(self.Archlog == False):
            self.Archlog = None
            self.botonverfile['state'] = "disabled"
            self.botonclearfile['state'] = "disabled"
        self.SeleccionarEstructura()
        self.Archlog = None

    def readfile(self):
        self.Archlog = None
        self.EstructuraSeleccionada = None
        self.Archlog = read_log_gaussian(self.filename)
        tsleep(0.5)
        self.botonverfile['state'] = "normal"
        self.botonclearfile['state'] = "normal"
        if(self.Archlog.Estructuras.__len__ == 0):
            self.Archlog = False

    @property
    def getDato(self) -> float:
        return self.__dato

    @property
    def getTextValue(self) -> float:
        return float(self.datoentrada.get())

    def get_Estructura_Seleccionada(self):
        return self.EstructuraSeleccionada

    def setDato(self, un_dato: float = 0.0):
        self.__dato = un_dato
        self.datoentrada.config(state='normal')
        self.datoentrada.delete(0, END)
        self.datoentrada.insert(0, str(un_dato))
        self.datoentrada.config(state='disabled')

    def SeleccionarEstructura(self):
        self.EstructuraSeleccionada = None
        if(len(self.Archlog.Estructuras) == 1):
            self.EstructuraSeleccionada = self.Archlog.Estructuras[0]
        else:
            self.a = SelectStructure(
                parent=self, estructuras=self.Archlog.Estructuras)
            if(self.a == None):
                self.EstructuraSeleccionada = None
            else:
                self.EstructuraSeleccionada = self.a.result
        if(self.EstructuraSeleccionada != None):
            self.comando(self.EstructuraSeleccionada)
            self.labelEtiquetafilename.config(
                text=path.basename(self.filename))
        else:
            self.labelEtiquetafilename.config(text="")
            self.filename = ""


class exception_tunnel(Exception):
    """
    Exception for tunneling errors
    """

    def __init__(self, message):
        super(exception_tunnel, self).__init__(message)
        self.message = message


class Ejecucion:
    '''
    Guarda la informacion de una ejecucion y se hacen los calculos
    '''

    def __init__(self,  title: str = "Title",#NOSONAR
                 react_1: Estructura = None,
                 react_2: Estructura = None,
                 trasition_rate: Estructura = None,
                 product_1: Estructura = None,
                 product_2: Estructura = None,
                 cage_efects: bool = False,
                 diffusion: bool = False,
                 solvent: str = "",
                 radius_1: float = nan,
                 radius_2: float = nan,
                 reaction_distance: float = nan,
                 degen: float = nan,
                 print_data = False):
        if ( transition_rate is None ):
            raise exception_tunnel("Please check your files are in the correct format,\n "
                "if the error persists please contact the administrator")
        if(react_1 is None):
            react_1 = Estructura()
        if(product_1 is None):
            product_1 = Estructura()
        if(react_2 is None):
            react_2 = Estructura()
        if(product_2 is None):
            product_2 = Estructura()
        self.pathway: str = title
        self.title = title
        self.React_1: Estructura = react_1
        self.React_2: Estructura = react_2
        self.trasition_rate: Estructura = trasition_rate
        self.Product_1: Estructura = product_1
        self.product_2: Estructura = product_2
        self.frequency_negative = self.trasition_rate.frecNeg.getValue
        self.temp = self.Product_1.temp.getValue
        self.cage_efects: bool = cage_efects
        self.diffusion: bool = diffusion
        self.solvent: str = solvent
        self.radius_1: float = radius_1
        self.radius_2: float = radius_2
        self.reaction_distance: float = reaction_distance
        self.degeneracy: float = degen
        self.Zreact: float = nan
        self.Zact: float = nan
        self.dH_react: float = nan
        self.dHact: float = nan
        self.Greact: float = nan
        self.Gact: float = nan
        self.rateCte: float = nan
        self.CalcularTunel: tst = tst()
        self.ejecutable: bool = False
        self.PrintData: bool = print_data

    def run(self) -> None:

        self.ejecutable = True
        """
            Reaction enthalpies (dh)
        """
        self.dH_react: float = 627.5095 * (self.Product_1.eH_ts.no_nan_value +
                                           self.product_2.eH_ts.no_nan_value - self.React_1.eH_ts.no_nan_value - self.React_2.eH_ts.no_nan_value)
        self.dHact: float = 627.5095 * (self.trasition_rate.eH_ts.getValue -
                                        self.React_1.eH_ts.no_nan_value - self.React_2.eH_ts.no_nan_value)
        """
            Reaction Zero_point_Energies (dh)
        """
        self.Zreact: float = 627.5095 * (self.product_2.zpe.no_nan_value + self.Product_1.zpe.no_nan_value
                                         - self.React_1.zpe.no_nan_value-self.React_2.zpe.no_nan_value)
        self.Zact: float = 627.5095 * (self.trasition_rate.zpe.getValue
                                       - self.React_1.zpe.no_nan_value - self.React_2.zpe.no_nan_value)
        """
           Calculate Tunnel G
        """
        self.CalcularTunel.calculate(BARRZPE=self.Zact,
                                     DELZPE=self.Zreact,
                                     FREQ=abs(self.trasition_rate.frecNeg.getValue),
                                     TEMP=self.temp)

        gibbsR1 = self.React_1.Thermal_Free_Enthalpies.no_nan_value    # NOSONAR
        gibbsR2 = self.React_2.Thermal_Free_Enthalpies.no_nan_value    # NOSONAR
        gibbsTS = self.trasition_rate.Thermal_Free_Enthalpies.getValue  # NOSONAR
        gibbsP1 = self.Product_1.Thermal_Free_Enthalpies.no_nan_value  # NOSONAR
        gibbsP2 = self.product_2.Thermal_Free_Enthalpies.no_nan_value  # NOSONAR

        molarV = 0.08206 * self.temp  # NOSONAR

        countR = 1 if gibbsR1 == 0.0 or gibbsR2 == 0.0 else 2  # NOSONAR
        countP = 1 if gibbsP1 == 0.0 or gibbsP2 == 0.0 else 2  # NOSONAR

        deltaNr = countP - countR  # NOSONAR
        deltaNt = 1 - countR  # NOSONAR
        corr1Mr = (1.987 / 1000) * self.temp * log(pow(molarV, deltaNr))  # NOSONAR
        corr1Mt = (1.987 / 1000) * self.temp * log(pow(molarV, deltaNt))  # NOSONAR

        # Calor de reacción
        self.Greact: float = corr1Mr + 627.5095 * (gibbsP2 + gibbsP1 - gibbsR1 - gibbsR2)
        # Energia de activación
        self.Gact: float = corr1Mt + 627.5095 * (gibbsTS - gibbsR1 - gibbsR2)

        """
            if use Cage Correction
        """
        if (self.cage_efects and deltaNt != 0):
            cageCorrAct = (1.987 / 1000) * self.temp * ((log(countR * # NOSONAR
                                            pow(10, 2 * countR - 2))) - (countR - 1))  
            self.Gact: float = self.Gact - cageCorrAct

        self.rateCte: float = self.degeneracy * self.CalcularTunel.G * (2.08e10 * self.temp * exp(-self.Gact * 1000 / (1.987 * self.temp)))

        if(self.diffusion):
            diffCoefA = (1.38E-23 * self.temp) / (6 * 3.14159 *  self.visc * self.radius_1)   # NOSONAR
            diffCoefB = (1.38E-23 * self.temp) / (6 * 3.14159 *   self.visc * self.radius_1)   # NOSONAR
            diffCoefAB = diffCoefA + diffCoefB  # NOSONAR
            kDiff = 1000 * 4 * 3.14159 * diffCoefAB * self.reaction_distance * 6.02e23  # NOSONAR
            self.rateCte: float = (kDiff * self.rateCte) /  (kDiff + self.rateCte)

    @property
    def visc(self) -> float:
        if(self.solvent == "Benzene"):
            return 0.000604
        elif(self.solvent == "Gas phase (Air)"):
            return 0.000018
        elif(self.solvent == "Pentyl ethanoate"):
            return 0.000862
        elif(self.solvent == "Water"):
            return 0.000891
        else:
            return nan


class EasyRate:

    def __init__(self, master=None):
        self.Ejecuciones: list[Ejecucion] = list()
        self.master = Tk() if master is None else Toplevel(master)
        self._principal = ttk.Frame(self.master)
        ttk.setup_master(self.master)
        self.style = ThemedStyle(self.master)
        self._principal.pack_propagate(True)
        self._principal.place(
            anchor='nw', bordermode='outside', x=str(0), y=str(0))
        self.master.title("Easy Rate 1.1")
        self.master.resizable(False, False)
        self.master.geometry("1100x600")
        self.frame_principal = ttk.Frame(self._principal)
        self._principal.configure(width='1200', height='605')
        self.menu()
        self.seccion_datos_2()
        self.seccion_diffusion()
        self.seccion_pantalla()
        self.seccion_leer_archivos()
        self.style.set_theme('winxpblue')
        self.style.configure('.', background='#f0f0f0', font=('calibri', 9))
        self.style.configure('TCombobox', fieldbackground='#f0f0f0')

    def menu(self):
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.on_save)
        filemenu.add_command(label="Exit", command=self._principal.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        ayuda = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="help", menu=ayuda)
        ayuda.add_command(label="About", command=self.about)
        self.master.config(menu=menubar)

    def seccion_leer_archivos(self, pos_x=10, pos_y=10):
        _seccion_leer_archivos = ttk.Frame(self._principal)
        _seccion_leer_archivos.configure(width='360', height='290')
        label_data_entry = ttk.Label(
            self._principal, text="Data entry", font=('calibri', 9, "bold"))
        label_data_entry.place(x=str(pos_x), y=str(pos_y))
        _seccion_leer_archivos.place(
            anchor='nw', bordermode='outside', x=str(pos_x), y=str(pos_y+10))
        tabla = ttk.Frame(_seccion_leer_archivos)
        tabla.place(anchor='nw', bordermode='outside', x='10', y='10')
        label_etiqueta_nombre = ttk.Label(tabla, text="Run title")
        label_etiqueta_nombre.grid(row=1, column=1)
        self.Title: Entry = Entry(tabla)
        self.Title.insert(0, str("Title"))
        self.Title.grid(row=1, column=2)
        self.React_1: EntradaDato = EntradaDato(tabla)
        self.React_1       .grid(row=2, column=1, columnspan=3)
        self.React_1       .Activar(etiqueta="React-1", command=self.def_react_1)
        self.React_2: EntradaDato = EntradaDato(tabla)
        self.React_2       .grid(row=3, column=1, columnspan=3)
        self.React_2       .Activar(etiqueta="React-2", command=self.def_react_2)
        self.trasition_rate: EntradaDato = EntradaDato(tabla)
        self.trasition_rate.grid(row=4, column=1, columnspan=3)
        self.trasition_rate.Activar(etiqueta="Transition state", command=self.deftrasition_rate)
        self.Product_1: EntradaDato = EntradaDato(tabla)
        self.Product_1.grid(row=5, column=1, columnspan=3)
        self.Product_1.Activar(etiqueta="Product-1 ",
                               command=self.def_product_1)
        self.product_2: EntradaDato = EntradaDato(tabla)
        self.product_2 .grid(row=6, column=1, columnspan=3)
        self.product_2 .Activar(etiqueta="Product-2",
                                command=self.defproduct_2)

    def def_react_1(self, estruct: Estructura):
        self.Temperatura.delete(0, END)
        self.Temperatura.insert(0, str(estruct.temp.getValue))
        self.Temperatura['state'] = "disabled"
        self.React_1.setDato(un_dato=estruct.Thermal_Free_Enthalpies.getValue)

    def def_react_2(self, estruct: Estructura):
        self.React_2.setDato(un_dato=estruct.Thermal_Free_Enthalpies.getValue)

    def deftrasition_rate(self, estruct: Estructura):
        self.trasition_rate.setDato(
            un_dato=estruct.Thermal_Free_Enthalpies.getValue)

    def def_product_1(self, estruct: Estructura):
        self.Product_1.setDato(
            un_dato=estruct.Thermal_Free_Enthalpies.getValue)

    def defproduct_2(self, estruct: Estructura):
        self.product_2.setDato(
            un_dato=estruct.Thermal_Free_Enthalpies.getValue)

    def seccion_datos_2(self, pos_x=30, pos_y=300):
        _seccion_datos_2 = ttk.Frame(self._principal)
        _seccion_datos_2.configure(width='200', height='50')
        _seccion_datos_2.place(x=str(pos_x), y=str(pos_y+15))
        label_etiqueta_temperatura = ttk.Label(
            _seccion_datos_2, text="Temperature(K)")
        label_etiqueta_temperatura.grid(row=1, column=0)
        self.Temperatura: Entry = Entry(_seccion_datos_2)
        self.Temperatura.grid(row=1, column=1)
        self.Temperatura.insert(0, "298.15")
        ttk.Label(_seccion_datos_2, text="Tunneling").grid(
            column=0, row=0, padx=1, pady=5)
        self.Tunneling: Entry = Entry(_seccion_datos_2, width='10')
        self.Tunneling.grid(column=1, row=0, padx=1, pady=5)
        ttk.Label(_seccion_datos_2, text="Reaction path degeneracy").grid(
            column=0, row=2, padx=1, pady=5)
        self.Reaction_path_degeneracy: Entry = Entry(
            _seccion_datos_2, width='10')
        self.Reaction_path_degeneracy.grid(column=1, row=2, padx=1, pady=5)
        self.Reaction_path_degeneracy.insert(0, "1")

    def seccion_diffusion(self, pos_x=30, pos_y=440):
        _seccion_diffusion = ttk.Frame(self._principal)
        _seccion_diffusion.configure(width='400', height='400')
        _seccion_diffusion.place(x=str(pos_x), y=str(pos_y))
        frame1 = ttk.Frame(_seccion_diffusion)
        frame1.place(x="1", y="10")
        self.diffusion = IntVar()
        self.diffusion.set(0)
        ttk.Label(frame1, text="Do you want to consider diffusion?").grid(
            column=0, row=0)
        ttk.Label(frame1, text="yes").grid(column=1, row=0)
        ttk.Radiobutton(frame1, value=1, variable=self.diffusion,
                        command=self.isdiffusion).grid(column=2, row=0)
        ttk.Label(frame1, text="No").grid(column=4, row=0)
        ttk.Radiobutton(frame1, value=0, variable=self.diffusion,
                        command=self.isdiffusion).grid(column=5, row=0)
        frame2a = ttk.Frame(_seccion_diffusion)
        frame2a.place(x="0", y="30")
        frame2a.configure(width='200', height='200')
        ttk.Label(frame2a, text="solvent").grid(row=0, column=0)
        self.solvent = ttk.Combobox(frame2a, state='disabled')
        self.solvent.configure(width="14")
        self.solvent.grid(row=1, column=0)
        values = list(self.solvent["values"])
        self.solvent["values"] = values + [""] + ["Benzene"] + \
            ["Gas phase (Air)"] + ["Pentyl ethanoate"]+["Water"]
        frame2 = ttk.Frame(_seccion_diffusion)
        frame2.place(x="110", y="30")
        frame2.configure(width='200', height='200')
        ttk.Label(frame2, text="Radius (in Angstroms) for:").grid(
            row=0, column=0, columnspan=2)
        ttk.Label(frame2, text="Reactant-1").grid(row=1, column=0)
        self.radius_react_1 = Entry(frame2, width=7, state='disabled')
        self.radius_react_1.grid(row=1, column=1)
        ttk.Label(frame2, text="Reactant-2").grid(row=2, column=0)
        self.radius_react_2 = Entry(frame2, width=7, state='disabled')
        self.radius_react_2.grid(row=2, column=1)
        ttk.Label(frame2, text="Reaction distance\n  (in Angstroms)").grid(
            row=3, column=0)
        self.reaction_distance = Entry(frame2, width=7, state='disabled')
        self.reaction_distance.grid(row=3, column=1)

    def isdiffusion(self):
        """

        """
        if(self.diffusion.get() == 1):
            self.reaction_distance['state'] = 'normal'
            self.radius_react_1['state'] = 'normal'
            self.radius_react_2['state'] = 'normal'
            self.solvent['state'] = 'normal'
            self.style.configure('TCombobox', fieldbackground='white')
        else:
            self.radius_react_1['state'] = 'disabled'
            self.radius_react_2['state'] = 'disabled'
            self.reaction_distance['state'] = 'disabled'
            self.solvent['state'] = 'disabled'
            self.style.configure('TCombobox', fieldbackground='#f0f0f0')

    def seccion_pantalla(self, pos_x=370, pos_y=20):
        _seccion_pantalla = ttk.Frame(self._principal)
        _seccion_pantalla.configure(width='1000', height='700')
        _seccion_pantalla.place(x=str(pos_x), y=str(pos_y))
        self.cage_efects = IntVar()
        self.cage_efects.set(0)
        ttk.Label(_seccion_pantalla, text="Cage Effects?").place(
            anchor='nw', x='80', y='10')
        ttk.Label(_seccion_pantalla, text="yes").place(
            anchor='nw', x='170', y='10')
        ttk.Radiobutton(_seccion_pantalla, value=1, variable=self.cage_efects).place(
            anchor='nw', x='190', y='10')
        ttk.Label(_seccion_pantalla, text="No").place(
            anchor='nw', x='210', y='10')
        ttk.Radiobutton(_seccion_pantalla, value=0, variable=self.cage_efects).place(
            anchor='nw', x='230', y='10')
        self.print_data = IntVar()
        self.print_data.set(0)
        ttk.Label(_seccion_pantalla, text="Print data input?").place(
            anchor='nw', x='270', y='10')
        ttk.Label(_seccion_pantalla, text="yes").place(
            anchor='nw', x='370', y='10')
        ttk.Radiobutton(_seccion_pantalla, value=1, variable=self.print_data).place(
            anchor='nw', x='390', y='10')
        ttk.Label(_seccion_pantalla, text="No").place(
            anchor='nw', x='410', y='10')

        ttk.Radiobutton(_seccion_pantalla, value=0, variable=self.print_data).place(
            anchor='nw', x='430', y='10')
        boton = ttk.Button(
            _seccion_pantalla, text="Data ok, Run", command=self.run_calc)
        boton.place(x="250", y="40")
        self._scrolle_pantalla(_seccion_pantalla)
        labelrate = ttk.Label(_seccion_pantalla)
        labelrate.configure(cursor='arrow', justify='left', relief='raised',
                            text='Rate constant units:\n-For bimolecular(M-1 s-1)\n -For unimolecular reactions(s-1)')
        labelrate.place(anchor='nw', x='0', y='500')
        labelphpadvertence = ttk.Label(_seccion_pantalla)
        labelphpadvertence.configure(
            cursor='based_arrow_down', justify='center', relief='groove', takefocus=False)
        labelphpadvertence.configure(
            text='Please note that pH is not\nconsidered here.\n\nCheck for updates in \nthis topic')
        labelphpadvertence.place(anchor='nw', x='300', y='500')

    def _scrolle_pantalla(self, _seccion_pantalla):
        frame_resultados = ttk.Frame(_seccion_pantalla)
        frame_resultados.place(x='0', y='70')
        self.salida = ScrolledText(
            frame_resultados, wrap="none", width=40, height=23)
        xsb = Scrollbar(frame_resultados, orient="horizontal",
                        command=self.salida.xview)
        self.salida.grid(row=1, column=0, columnspan=1)
        self.salida.focus()
        self.salida.configure(xscrollcommand=xsb.set)
        self.salida.bind("<Key>", lambda e: "break")
        xsb.grid(row=2, column=0, columnspan=1, sticky=E+N+S+W)
        self.salida2 = ScrolledText(
            frame_resultados, wrap="none", width=40, height=23)
        xsb2 = Scrollbar(
            frame_resultados, orient="horizontal", command=self.salida2.xview)
        self.salida2.grid(row=1, column=1, columnspan=1)
        self.salida2.focus()
        self.salida2.configure(xscrollcommand=xsb2.set)
        self.salida2.bind("<Key>", lambda e: "break")
        xsb2.grid(row=2, column=1, columnspan=1, sticky=E+N+S+W)

    def run_calc(self):
        if(not True):  # TODO #1 Verificar si los datos son correcotoss  Verificarlos
            return
        ejecucion_actual = Ejecucion(
            str(self.Title.get()),
            self.React_1.get_Estructura_Seleccionada(),
            self.React_2.get_Estructura_Seleccionada(),
            self.trasition_rate.get_Estructura_Seleccionada(),
            self.Product_1.get_Estructura_Seleccionada(),
            self.product_2.get_Estructura_Seleccionada(),
            self.cage_efects.get() == 1,
            self.diffusion.get() == 1,
            self.solvent.get(),
            float(self.radius_react_1.get()
                  if self.radius_react_1.get() != "" else "0"),
            float(self.radius_react_2.get()
                  if self.radius_react_2.get() != "" else "0"),
            float(self.reaction_distance.get()
                  if self.reaction_distance.get() != "" else "0"),
            float(self.Reaction_path_degeneracy.get()
                  if self.Reaction_path_degeneracy.get() != "" else "0"),
            self.print_data.get() == 1
           
        )
        ejecucion_actual.run()
        self.salida.insert(
            END, ("Pathway:  " + ejecucion_actual.pathway + "\n"))
        self.salida.insert(END, ("Gibbs Free Energy of \n\treaction (kcal/mol):   "
                                 + str(round(ejecucion_actual.Greact, 2)) + "\n\n"))
        self.salida.insert(END, ("Gibbs Free Energy of \n\tactivation "
                                 + ("with cage effects \n\t"if(ejecucion_actual.cage_efects)else "") +
                                 " (kcal/mol):   "
                                 + str(round(ejecucion_actual.Gact, 2)) + "\n\n"))
        self.salida.insert(END, ("Rate Constant "+("\n\twith cage effects "if(ejecucion_actual.cage_efects)else "") + ":    "
                                 + "{:.2e}".format(ejecucion_actual.rateCte) + "\n\n"))
        
        self.salida.insert(
            END, ("ALPH1:" + str(round(ejecucion_actual.CalcularTunel.ALPH1, 2)) + "\n"))
        self.salida.insert(
            END, ("ALPH2:" + str(round(ejecucion_actual.CalcularTunel.ALPH2, 2)) + "\n"))
        self.salida.insert(
            END, ("u:" + str(round(ejecucion_actual.CalcularTunel.U, 2)) + "\n"))
        self.salida.insert(
            END, ("G:" + str(round(ejecucion_actual.CalcularTunel.G, 2)) + "\n"))
        self.salida.insert(END, ("_____________________________\n"))
        self.salida2.insert(
            END, ("Pathway:  " + str(ejecucion_actual.pathway) + "\n"))
        self.salida2.insert(END, ("Imag. Freq. (cm-1):  \t\t\t"
                                  + str(round(ejecucion_actual.frequency_negative, 2)) + "\n\n"))
        self.salida2.insert(END, ("Reaction enthalpies (dH)" + "\n"))
        self.salida2.insert(END, ("\tdH reaction (kcal/mol):  \t"
                                  + str(round(ejecucion_actual.dH_react, 2)) + "\n"))
        self.salida2.insert(END, ("\tdH activation (kcal/mol):\t"
                                  + str(round(ejecucion_actual.dHact, 2)) + "\n\n"))
        self.salida2.insert(END, ("Reaction ZPE (dZPE)  " + "\n"))
        self.salida2.insert(END, ("\tdZPE reaction (kcal/mol):  \t"
                                  + str(round(ejecucion_actual.Zreact, 2)) + "\n"))
        self.salida2.insert(END, ("\tdZPE activation (kcal/mol):\t"
                                  + str(round(ejecucion_actual. Zact, 2)) + "\n\n"))
        self.salida2.insert(END, ("Temperature (K):  " + str(round(ejecucion_actual.temp, 2))
                            + ("\n\n"if(ejecucion_actual.cage_efects)else "") + "\n\n"))
        self.salida2.insert(END, ("______________________________________\n"))
        self.Ejecuciones.append(ejecucion_actual)
        self.Tunneling.insert(0, " ")

        self.Tunneling.delete(0, END)
        self.Tunneling.insert(
            0, str(round(ejecucion_actual.CalcularTunel.G, 2)))
        self.Tunneling['state'] = "disabled"

    def about(self):
        """
            show a windows with aabout information
            with data:
            autrhor
            licence
        """
        window = Toplevel()
        window.title("About")
        window.geometry("300x200")
        window.resizable(0, 0)
        label = Label(window, text="About", font=("Helvetica", 16))
        label.grid(row=0, column=0, columnspan=2)
        label = Label(window, text="Author:", font=("Helvetica", 12))
        label.grid(row=1, column=0)
        label = Label(window, text="Annia Galano", font=("Helvetica", 12))
        label.grid(row=1, column=1)

        def close():
            window.destroy()
        boton = Button(window, text="Close", command=close)
        boton.grid(row=3, column=0, columnspan=2)

    def on_save(self):
        file_path: str = None
        if file_path is None:
            file_path = filedialog.asksaveasfilename(filetypes 
                    = (("Text files", "*.txt"), ("All files", "*.*")))

        file = open(file_path, "w+")
        for ejecucion in self.Ejecuciones:
            
            file.write("Pathway: "+ ejecucion.pathway + "\n")
            if(ejecucion.PrintData):
                file.write("Data entry: " + "\n")
                file.write("\tReact 1:        :"+str(ejecucion.React_1.Thermal_Free_Enthalpies.no_nan_value   ) + "\n"    )
                file.write("\tReact 2:        :"+str(ejecucion.React_2.Thermal_Free_Enthalpies.no_nan_value   ) + "\n"    )
                file.write("\tTransition rate :"+str(ejecucion.trasition_rate.Thermal_Free_Enthalpies.getValue) + "\n"   )
                file.write("\tProd 1          :"+str(ejecucion.Product_1.Thermal_Free_Enthalpies.no_nan_value ) + "\n"    )
                file.write("\tProd 2          :"+str(ejecucion.product_2.Thermal_Free_Enthalpies.no_nan_value ) + "\n")
                file.write("\tDegeneracy      :"+str(ejecucion.degeneracy) + "\n")
            if(ejecucion.PrintData and ejecucion.diffusion):
                file.write("\tDiffusion considered: \n") 
                file.write("\t\tSolvent:        "+ ejecucion.solvent +  "\n")
                file.write("\t\tRadius React-1: "+str(ejecucion.radius_1) + "\n")
                file.write("\t\tRadius React-2: "+str(ejecucion.radius_2) + "\n")
                file.write("\t\tRadius Reaction distance: "+ str(ejecucion.reaction_distance) + "\n")
            if(ejecucion.PrintData):
                file.write("\n\n")
            file.write("Gibbs Free Energy of reaction (kcal/mol):\t\t"
                          + str(round(ejecucion.Greact, 2)) + "\n\n")
            
            file.write("Gibbs Free Energy of activation "
                            + ("with cage effects "if(ejecucion.cage_efects)else "") +
                            " (kcal/mol):\t"
                            + str(round(ejecucion.Gact, 2)) + "\n\n")
            
            file.write("Rate Constant "+("with cage effects "if(ejecucion.cage_efects)else "") + ":    "
                            + "{:.2e}".format(ejecucion.rateCte) + "\n\n")
            
            file.write("ALPH1:\t" + str(round(ejecucion.CalcularTunel.ALPH1, 2)) + "\n")  # ALPH1
            
            file.write("ALPH2:\t" + str(round(ejecucion.CalcularTunel.ALPH2, 2)) + "\n")  # ALPH2
            
            file.write("u:\t\t" + str(round(ejecucion.CalcularTunel.U, 2)) + "\n")  # u 
            
            file.write("Imag. Freq. (cm-1): \t"
                            + str(round(ejecucion.frequency_negative, 2)) + "\n\n") 
            
            file.write("Reaction enthalpies (dH)" + "\n")
            
            file.write("\tdH reaction (kcal/mol):  \t"
                            + str(round(ejecucion.dH_react, 2)) + "\n")
            
            file.write("\tdH activation (kcal/mol):\t"
                            + str(round(ejecucion.dHact, 2)) + "\n\n")
            
            file.write("Reaction ZPE (dZPE)  " + "\n") 
            
            file.write("\tdZPE reaction (kcal/mol):  \t" 
                            + str(round(ejecucion.Zreact, 2)) + "\n")   
            
            file.write("\tdZPE activation (kcal/mol):\t"
                            + str(round(ejecucion. Zact, 2)) + "\n\n")  
            
            file.write("Temperature (K):  " + str(round(ejecucion.temp, 2))
                            + ("\n\n") )
            
            file.write("______________________________________\n")

        file.close()

    def run(self):
        self._principal.mainloop()


if __name__ == '__main__':
    app = EasyRate()
    app.run()
