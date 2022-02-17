import math
import os
from tkinter import filedialog, font, messagebox, ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter.filedialog import askopenfilename
from SeslectStructura import SelectStructure
from viewStructure import ViewStructure
from tkdialog import WaitAlert
from read_log_gaussian.read_log_gaussian import *
import threading
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle


class EntradaDato(ttk.Frame):
    def Activar(self, Etiqueta="Sin nombre", buttontext="Browse", dato=0.0, info="", command=None):
        self.__dato = dato
        self.Etiqueta = Etiqueta
        self.textoButton = buttontext
        self.labelEtiquetaNombre = ttk.Label(
            self, text=self.Etiqueta, width=17)
        self.datoentrada = tk.Entry(self, width=10)
        self.datoentrada.insert(0, str(self.__dato))
        self.datoentrada["state"] = "disabled"
        self.botonActivo = ttk.Button(
            self, text=self.textoButton, width=7, command=self.open)
        self.grid(pady=5)
        self.labelEtiquetaNombre.grid(row=0, column=1)
        self.datoentrada.grid(row=0, column=2)
        self.botonActivo.grid(row=0, column=3)
        self.Archlog: read_log_gaussian = None
        self.filname = ""
        self.esperar: int = 0
        self.botonverfile = ttk.Button(
            self, text="view", width=5, command=self.view)
        self.botonverfile.grid(row=0, column=4, padx=4)
        self.botonverfile['state'] = "disabled"
        self.labelEtiquetafilename = ttk.Label(self, text="")
        self.labelEtiquetafilename.grid(row=1, column=3, columnspan=2, padx=4)
        self.comando = command

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
        read = threading.Thread(target=self.readfile)
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
        self.SeleccionarEstructura()

    def readfile(self):
        self.Archlog = read_log_gaussian(self.filename)
        self.botonverfile['state'] = "normal"
        if(self.Archlog == None):
            self.Archlog = False

    @property
    def getDato(self) -> float:
        return self.__dato

    @property
    def getTextValue(self) -> float:
        return float(self.datoentrada.get())

    def setDato(self, UnDato: float = 0.0):
        self.__dato = UnDato
        self.datoentrada.config(state='normal')
        self.datoentrada.delete(0, END)
        self.datoentrada.insert(0, str(UnDato))
        self.datoentrada.config(state='disabled')

    def SeleccionarEstructura(self):
        if(len(self.Archlog.Estructuras) == 1):
            self.EstructuraSeleccionada = self.Archlog.Estructuras[0]
        else:
            self.a = SelectStructure(
                parent=self, Estructuras=self.Archlog.Estructuras)
            if(self.a == None):
                self.EstructuraSeleccionada = None
            else:
                self.EstructuraSeleccionada = self.a.result
        if(self.EstructuraSeleccionada != None):
            self.comando(self.EstructuraSeleccionada)
            self.labelEtiquetafilename.config(
                text=os.path.basename(self.filename))
        else:
            self.labelEtiquetafilename.config(text="")
            self.filename = ""


'''
    Guarda la informacion de una ejecucion
'''


class Ejecucion:
    def __init__(self,  title: string = "Title",
                 React_1: EntradaDato = None,
                 React_2: EntradaDato = None,
                 Transition_Rate: EntradaDato = None,
                 Product_1: EntradaDato = None,
                 Product_2: EntradaDato = None):
        self.Zreact: float = nan
        self.Zact: float = nan
        self.Zreact_round: float = nan
        self.Zact_round: float = nan
        self.Hreact: float = nan
        self.Hact: float = nan
        self.Hreact_round: float = nan
        self.Hact_round: float = nan
        self.CalcularTunel: float = nan
        self.pathway: float = nan
        self.Greact_round: float = nan
        self.Gact_round: float = nan
        self.rateCte_write: float = nan
        self.title = title
        self.React_1: EntradaDato = React_1 
        self.React_2: EntradaDato = React_2 
        self.Transition_Rate: EntradaDato = Transition_Rate
        self.Product_1: EntradaDato = Product_1 
        self.Product_2: EntradaDato = Product_2


class EasyRate:
    VISC = 8.91e-4
    K_BOLTZ = 1.38E-23

    def __init__(self, master=None):
        self.Ejecucion: list[Ejecucion] = list()
        self.master = tk.Tk() if master is None else tk.Toplevel(master)
        self.Principal = ttk.Frame(self.master)
        ttk.setup_master(self.master)
        style = ThemedStyle(self.master)
        self.Principal.pack_propagate(True)
        self.Principal.place(
            anchor='nw', bordermode='outside', x=str(0), y=str(0))
        self.master.title("Easy Rate 1.1")
        self.master.resizable(False, False)
        self.master.geometry("975x600")
        self.FramePrincipal = ttk.Frame(self.Principal)
        self.Principal.configure(width='960', height='605')
        self.menu()
        self.Seccion_Datos_2()
        self.SeccionDifusion()
        self.SeccionPantalla()
        self.SeccionLeerArchivos()
        style.set_theme('winxpblue')
        style.configure('.', background='#f0f0f0', font=('calibri', 9))

    def menu(self):
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.onSave)
        filemenu.add_command(label="Exit", command=self.Principal.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="help", menu=help)
        help.add_command(label="About", command=self.About)

        self.master.config(menu=menubar)

    def SeccionLeerArchivos(self, pos_x=10, pos_y=10):
        seccionLeerArchivos = ttk.Frame(self.Principal)
        seccionLeerArchivos.configure(width='360', height='290')

        labelData_entry = ttk.Label(
            self.Principal, text="Data entry", font=('calibri', 9, "bold"))
        labelData_entry.place(x=str(pos_x), y=str(pos_y))

        seccionLeerArchivos.place(
            anchor='nw', bordermode='outside', x=str(pos_x), y=str(pos_y+10))

        tabla = ttk.Frame(seccionLeerArchivos)
        tabla.place(anchor='nw', bordermode='outside', x='10', y='10')

        labelEtiquetaNombre = ttk.Label(tabla, text="Run title")
        labelEtiquetaNombre.grid(row=1, column=1)

        self.Title = tk.Entry(tabla)
        self.Title.insert(0, str("Title"))
        self.Title.grid(row=1, column=2)

        self.React_1 = EntradaDato(tabla)
        self.React_1       .grid(row=2, column=1, columnspan=3)
        self.React_1       .Activar(
            Etiqueta="React-1", command=self.defReact_1)

        self.React_2 = EntradaDato(tabla)
        self.React_2       .grid(row=3, column=1, columnspan=3)
        self.React_2       .Activar(
            Etiqueta="React-2", command=self.defReact_2)

        self.Transition_Rate = EntradaDato(tabla)
        self.Transition_Rate.grid(row=4, column=1, columnspan=3)
        self.Transition_Rate.Activar(
            Etiqueta="Transition state", command=self.defTransition_Rate)

        self.Product_1 = EntradaDato(tabla)
        self.Product_1.grid(row=5, column=1, columnspan=3)
        self.Product_1.Activar(Etiqueta="Product-1 ",
                               command=self.defProduct_1)

        self.Product_2 = EntradaDato(tabla)
        self.Product_2 .grid(row=6, column=1, columnspan=3)
        self.Product_2 .Activar(Etiqueta="Product-2",
                                command=self.defProduct_2)

    def defReact_1(self, Estruc: Estructura):
        self.Temperatura.delete(0, END)
        self.Temperatura.insert(0, str(Estruc.temp.getValue))
        self.Temperatura['state'] = "disabled"
        self.React_1.setDato(UnDato=Estruc.free_engergy.getValue)

    def defReact_2(self, Estruc: Estructura):
        self.React_2.setDato(UnDato=Estruc.free_engergy.getValue)

    def defTransition_Rate(self, Estruc: Estructura):
        self.Transition_Rate.setDato(UnDato=Estruc.free_engergy.getValue)

    def defProduct_1(self, Estruc: Estructura):
        self.Product_1.setDato(UnDato=Estruc.free_engergy.getValue)

    def defProduct_2(self, Estruc: Estructura):
        self.Product_2.setDato(UnDato=Estruc.scf.getValue)

    def Seccion_Datos_2(self, pos_x=30, pos_y=300):
        SeccionDatos2 = ttk.Frame(self.Principal)
        SeccionDatos2.configure(width='200', height='50')
        SeccionDatos2.place(x=str(pos_x), y=str(pos_y+15))
        labelEtiquetaTemperatura = ttk.Label(
            SeccionDatos2, text="Temperature(K)")
        labelEtiquetaTemperatura.grid(row=1, column=0)
        self.Temperatura = tk.Entry(SeccionDatos2)
        self.Temperatura.grid(row=1, column=1)
        self.Temperatura.insert(0, "298.15")
        ttk.Label(SeccionDatos2, text="Tunneling").grid(
            column=0, row=0, padx=1, pady=5)
        self.Tunneling = ttk.Entry(SeccionDatos2, width='10').grid(
            column=1, row=0, padx=1, pady=5)
        ttk.Label(SeccionDatos2, text="Reaction path degeneracy").grid(
            column=0, row=2, padx=1, pady=5)
        self.Reaction_path_degeneracy = ttk.Entry(
            SeccionDatos2, width='10').grid(column=1, row=2, padx=1, pady=5)

    def SeccionDifusion(self, pos_x=30, pos_y=440):
        seccionDifusion = ttk.Frame(self.Principal)
        seccionDifusion.configure(width='400', height='400')
        seccionDifusion.place(x=str(pos_x), y=str(pos_y))
        frame1 = ttk.Frame(seccionDifusion)
        frame1.place(x="1", y="10")
        self.difusion = IntVar()
        self.difusion.set(0)
        ttk.Label(frame1, text="Do you want to consider difusion?").grid(
            column=0, row=0)
        ttk.Label(frame1, text="yes").grid(column=1, row=0)
        ttk.Radiobutton(frame1, value=1, variable=self.difusion,
                        command=self.isDifusion).grid(column=2, row=0)
        ttk.Label(frame1, text="No").grid(column=4, row=0)
        ttk.Radiobutton(frame1, value=0, variable=self.difusion,
                        command=self.isDifusion).grid(column=5, row=0)
        frame2a = ttk.Frame(seccionDifusion)
        frame2a.place(x="0", y="30")
        frame2a.configure(width='200', height='200')
        ttk.Label(frame2a, text="Solvent").grid(row=0, column=0)
        self.combo = ttk.Combobox(frame2a)
        self.combo.configure(width="14")
        self.combo.grid(row=1, column=0)
        values = list(self.combo["values"])
        self.combo["values"] = values + [""] + ["Benzene"] + \
            ["Gas phase (Air)"] + ["Pentyl ethanoate"]+["Water"]
        frame2 = ttk.Frame(seccionDifusion)
        frame2.place(x="110", y="30")
        frame2.configure(width='200', height='200')
        ttk.Label(frame2, text="Radius (in Angstroms) for:").grid(
            row=0, column=0, columnspan=2)
        ttk.Label(frame2, text="Reactant-1").grid(row=1, column=0)
        self.radius_react_1 = tk.Entry(frame2, width=7, state='disabled')
        self.radius_react_1.grid(row=1, column=1)
        ttk.Label(frame2, text="Reactant-2").grid(row=2, column=0)
        self.radius_react_2 = tk.Entry(frame2, width=7, state='disabled')
        self.radius_react_2.grid(row=2, column=1)
        ttk.Label(frame2, text="Reaction distance\n  (in Angstroms)").grid(
            row=3, column=0)
        self.ReactionDistance = tk.Entry(frame2, width=7, state='disabled')
        self.ReactionDistance.grid(row=3, column=1)

    def isDifusion(self):
        if(self.difusion.get() == 1):
            self.ReactionDistance['state'] = 'normal'
            self.radius_react_1['state'] = 'normal'
            self.radius_react_2['state'] = 'normal'
        else:
            self.radius_react_1['state'] = 'disabled'
            self.radius_react_2['state'] = 'disabled'
            self.ReactionDistance['state'] = 'disabled'

    def SeccionPantalla(self, pos_x=370, pos_y=20):
        seccionPantalla = ttk.Frame(self.Principal)
        seccionPantalla.configure(width='600', height='700')
        seccionPantalla.place(x=str(pos_x), y=str(pos_y))
        self.Cage_efects = IntVar()
        self.Cage_efects.set(0)
        ttk.Label(seccionPantalla, text="Cage Effects?").place(
            anchor='nw', x='100', y='10')
        ttk.Label(seccionPantalla, text="yes").place(
            anchor='nw', x='170', y='10')
        ttk.Radiobutton(seccionPantalla, value=1, variable=self.Cage_efects).place(
            anchor='nw', x='190', y='10')
        ttk.Label(seccionPantalla, text="No").place(
            anchor='nw', x='210', y='10')
        ttk.Radiobutton(seccionPantalla, value=0, variable=self.Cage_efects).place(
            anchor='nw', x='230', y='10')
        self.PrintData = IntVar()
        self.PrintData.set(0)
        ttk.Label(seccionPantalla, text="Print data input?").place(
            anchor='nw', x='300', y='10')
        ttk.Label(seccionPantalla, text="yes").place(
            anchor='nw', x='370', y='10')
        ttk.Radiobutton(seccionPantalla, value=1, variable=self.PrintData).place(
            anchor='nw', x='390', y='10')
        ttk.Label(seccionPantalla, text="No").place(
            anchor='nw', x='410', y='10')
        ttk.Radiobutton(seccionPantalla, value=0, variable=self.PrintData).place(
            anchor='nw', x='430', y='10')

        boton = ttk.Button(
            seccionPantalla, text="Data ok, Run", command=self.run_calc)
        boton.place(x="250", y="40")
        self.ScrollePantalla(seccionPantalla)
        labelrate = ttk.Label(seccionPantalla)
        labelrate.configure(cursor='arrow', justify='left', relief='raised',
                            text='Rate constant units:\n-For bimolecular(M-1 s-1)\n -For unimolecular reactions(s-1)')
        labelrate.place(anchor='nw', x='0', y='500')

        labelphpadvertence = ttk.Label(seccionPantalla)
        labelphpadvertence.configure(
            cursor='based_arrow_down', justify='center', relief='groove', takefocus=False)
        labelphpadvertence.configure(
            text='Please note that pH is not\nconsidered here.\n\nCheck for updates in \nthis topic')
        labelphpadvertence.place(anchor='nw', x='300', y='500')

    def ScrollePantalla(self, seccionPantalla):
        FrameResultados = ttk.Frame(seccionPantalla)
        FrameResultados.place(x='0', y='70')
        self.salida = ScrolledText(
            FrameResultados, wrap="none", width=35, height=23)
        xsb = tk.Scrollbar(FrameResultados, orient="horizontal",
                           command=self.salida.xview)
        self.salida.grid(row=1, column=0, columnspan=1)
        self.salida.focus()
        self.salida.configure(xscrollcommand=xsb.set)
        self.salida.bind("<Key>", lambda e: "break")
        xsb.grid(row=2, column=0, columnspan=1, sticky=E+N+S+W)

        self.salida2 = ScrolledText(
            FrameResultados, wrap="none", width=32, height=23)
        xsb2 = tk.Scrollbar(
            FrameResultados, orient="horizontal", command=self.salida2.xview)
        self.salida2.grid(row=1, column=1, columnspan=1)
        self.salida2.focus()
        self.salida2.configure(xscrollcommand=xsb2.set)
        self.salida2.bind("<Key>", lambda e: "break")
        xsb2.grid(row=2, column=1, columnspan=1, sticky=E+N+S+W)

    def run_calc(self):
        if(not True):
            return

    def About(self):
        pass

    def onSave(self):
        file_path: string = None
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        try:
            # Write the Prolog rule editor contents to the file location
            with open(file_path, "w+") as file:
                file.write(
                    "Entry Values: \n\n"
                    "\t\tReact-1(adiab.): " + str(self.React_1       .getTextValue) + "\n" +
                    "\t\tReact-2(adiab.): " + str(self.React_2       .getTextValue) + "\n" +
                    "\t\tProduct-1(adiab.): "+str(self.Transition_Rate.getTextValue) + "\n" +
                    "\t\tProduct-2(adiab.): "+str(self.Product_1.getTextValue) + "\n" +
                    "\t\tProduct-1(vert.): " +
                    str(self.Product_2 .getTextValue) + "\n"
                )
                file.write(
                    self.salida.get("1.0", END)+"\n")
                file.close()

        except FileNotFoundError:
            messagebox.showerror(title="It is not possible to save",
                                 message="Please contact to administrator")
            return

    def run(self):
        self.Principal.mainloop()


if __name__ == '__main__':
    app = EasyRate()
    app.run()
