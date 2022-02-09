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
class EntradaDato(ttk.Frame) :
    def Activar(self,Etiqueta="Sin nombre",buttontext="Browse",dato=0.0,info="",command =None):
        self.__dato=dato
        self.Etiqueta =Etiqueta
        self.textoButton=buttontext
        self.labelEtiquetaNombre = ttk.Label(self,text=self.Etiqueta,width=17)
        self.datoentrada = tk.Entry(self,width=10)
        self.datoentrada.insert(0,str(self.__dato))
        self.botonActivo =ttk.Button(self,text=self.textoButton,width=7,command=self.open)
        self.grid(pady=5)
        self.labelEtiquetaNombre.grid(row = 0, column = 1)
        self.datoentrada.grid(row = 0, column = 2)
        self.botonActivo.grid(row = 0, column = 3)
        self.Archlog:read_log_gaussian =None
        self.filname=""
        self.esperar:int =0
        self.botonverfile = ttk.Button(self,text="view",width=5,command=self.view)
        self.botonverfile.grid(row = 0, column = 4,padx=4)
        self.botonverfile['state'] ="disabled"
        self.labelEtiquetafilename = ttk.Label(self,text="")
        self.labelEtiquetafilename.grid(row = 1, column = 3,columnspan = 2,padx=4)
        self.mensajeEsperar:WaitAlert
        self.EstructuraSeleccionada:Estructura
        self.comando=command
    def view(self):
        ViewStructure(master=self, estructure =self.EstructuraSeleccionada)
    def open(self):
        filetypes = [ 
            ("log Gaussian file",  "*.log"), 
            ("txt format Gaussian","*.txt"),
            ("out Gaussian file",  "*.out")
            ]
        self.mensajeEsperar:WaitAlert
        self.filename = askopenfilename(initialdir=".",
                           filetypes =filetypes,
                           title = "Choose a file.")

        if(self.filename ==""):return
        read  = threading.Thread(target = self.readfile)
        read.start()
        while(self.Archlog == None):
            self.esperar =1
            self.mensajeEsperar =  WaitAlert(parent=self,
                title='Reading the file', 
                message='Please wait', 
                pause=self.esperar) # show countdown. 
        if(self.Archlog == False):
            self.Archlog =None
            self.botonverfile['state'] ="disabled"
        self.SeleccionarEstructura()
            
    def readfile(self):
        self.Archlog =read_log_gaussian(self.filename)
        self.botonverfile['state'] ="normal"
        if(self.Archlog ==None):
            self.Archlog =False
    @property
    def getDato(self)->float:
        return self.__dato
    @property
    def getTextValue(self)->float:
        return float(self.datoentrada.get())
    
    def setDato(self,UnDato:float=0.0):
        self.__dato=UnDato
        self.datoentrada.config(state='normal')
        self.datoentrada.delete(0,END)
        self.datoentrada.insert(0,str(UnDato))
        self.datoentrada.config(state='disabled')

    def SeleccionarEstructura(self):
        if(len(self.Archlog.Estructuras)==1):
            self.EstructuraSeleccionada =self.Archlog.Estructuras[0]
        else: 
            self.a = SelectStructure(parent=self,Estructuras=self.Archlog.Estructuras)
            if(self.a  == None):
                self.EstructuraSeleccionada =None
            else:
                self.EstructuraSeleccionada  =self.a.result
        if(self.EstructuraSeleccionada!=None):
            self.comando(self.EstructuraSeleccionada)
            self.labelEtiquetafilename.config(text  = os.path.basename(self.filename))
        else:
            self.labelEtiquetafilename.config(text  = "")
            self.filename=""

class EasyRate:
    def __init__(self, master=None):
        self.master = tk.Tk() if master is None else tk.Toplevel(master)
        self.Principal = ttk.Frame(self.master)
        ttk.setup_master(self.master)
        style = ThemedStyle(self.master )
        self.Principal.pack_propagate(True)
        self.Principal.place(anchor='nw', bordermode='outside', x=str(0), y=str(0))
       
        self.master.title("Marcus 1.1")
        self.master.resizable(False, False)
        self.master.geometry("975x600")

        self.FramePrincipal = ttk.Frame(self.Principal)
        self.Principal.configure(width='960',height='605')
        self.menu() 
        self.SeecionTemperatura()
        self.SeccionDifusion()
        self.SeccionPantalla() 
        self.SeccionLeerArchivos()
        self.visc = 8.91e-4 
        self.kBoltz = 1.38E-23
        ''' while(True):
          for i in style.get_themes():
            style.set_theme(i)
            style.configure('.', background= '#f0f0f0', font=('calibri', 9))
            input("inserta: "+ i)'''
        style.set_theme('winxpblue')
        style.configure('.', background= '#f0f0f0', font=('calibri', 9))
        
    def menu(self):
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save",command=self.onSave)
        filemenu.add_command(label="Exit",command=self.Principal.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="help", menu=help)
        help.add_command(label="About",command=self.About)
        
        self.master.config(menu=menubar)
    

    def SeccionLeerArchivos(self,pos_x=10,pos_y=10):
        seccionLeerArchivos = ttk.Frame(self.Principal)
        seccionLeerArchivos.configure(width='360',height='355')

        labelData_entry = ttk.Label(self.Principal,text="Data entry", font=('calibri', 9,"bold"))
        labelData_entry.place(x=str(pos_x), y=str(pos_y))
        
        seccionLeerArchivos.place(anchor='nw', bordermode='outside', x=str(pos_x), y=str(pos_y+10))

        tabla =ttk.Frame(seccionLeerArchivos)
        tabla.place(anchor='nw', bordermode='outside', x='10', y='10')

        labelEtiquetaNombre = ttk.Label(tabla,text="Run title")
        labelEtiquetaNombre.grid(row = 1, column = 1)

        self.Title = tk.Entry(tabla)
        self.Title.insert(0,str("Title"))
        self.Title.grid(row = 1, column = 2)
        
        self.React_1        = EntradaDato(tabla)
        self.React_1       .grid(row=2,column=1,columnspan = 3) 
        self.React_1       .Activar(Etiqueta="React-1(adiab.)"
                            ,command=self.defReact_1       )
        
        self.React_2        = EntradaDato(tabla)
        self.React_2       .grid(row=3,column=1,columnspan = 3) 
        self.React_2       .Activar(Etiqueta="React-2(adiab.)"
                            ,command=self.defReact_2       )
        
        self.Prduct_1_adiab = EntradaDato(tabla)
        self.Prduct_1_adiab.grid(row=4,column=1,columnspan = 3) 
        self.Prduct_1_adiab.Activar(Etiqueta="Product-1(adiab.)"
                            ,command=self.defPrduct_1_adiab)
        
        self.Prduct_2_adiab = EntradaDato(tabla)
        self.Prduct_2_adiab.grid(row=5,column=1,columnspan = 3) 
        self.Prduct_2_adiab.Activar(Etiqueta="Product-2(adiab.)"
                            ,command=self.defPrduct_2_adiab)
        
        self.Prduct_1_vert  = EntradaDato(tabla)
        self.Prduct_1_vert .grid(row=6,column=1,columnspan = 3) 
        self.Prduct_1_vert .Activar(Etiqueta="Product-1(vert.)"
                            ,command=self.defPrduct_1_vert )
        


    def defReact_1       (self,Estruc:Estructura):
        self.Temperatura.delete(0,END)
        self.Temperatura.insert(0,str(Estruc.temp.getValue))
        self.Temperatura['state'] ="disabled"
        self.React_1.setDato(UnDato=Estruc.free_engergy.getValue)
        
    def defReact_2       (self,Estruc:Estructura):
        self.React_2.setDato(UnDato=Estruc.free_engergy.getValue)
    def defPrduct_1_adiab(self,Estruc:Estructura):
        self.Prduct_1_adiab.setDato(UnDato=Estruc.free_engergy.getValue)
    def defPrduct_2_adiab(self,Estruc:Estructura):
        self.Prduct_2_adiab.setDato(UnDato=Estruc.free_engergy.getValue)
    def defPrduct_1_vert (self,Estruc:Estructura):
        self.Prduct_1_vert.setDato(UnDato=Estruc.scf.getValue)



    def SeecionTemperatura(self,pos_x=30,pos_y=400): 
        seccionTemperatura= ttk.Frame(self.Principal)
        seccionTemperatura.configure(width='200',height='50')
        seccionTemperatura.place(x=str(pos_x),y=str(pos_y+15))
        labelEtiquetaTemperatura = ttk.Label(seccionTemperatura,text="Temperature(K)" )
        labelEtiquetaTemperatura.grid(row = 1, column = 1)
        self.Temperatura = tk.Entry(seccionTemperatura)
        self.Temperatura.grid(row = 1, column = 2)
        self.Temperatura.insert(0,"298.15")

    def SeccionDifusion(self,pos_x=30,pos_y=440):
        seccionDifusion= ttk.Frame(self.Principal)
        seccionDifusion.configure(width='400',height='400')
        seccionDifusion.place(x=str(pos_x),y=str(pos_y))
        frame1=ttk.Frame(seccionDifusion)
        frame1.place(x="1",y="10")
        self.difusion=IntVar()
        self.difusion.set(0)
        ttk.Label(frame1,text="Do you want to consider difusion?").grid(column=0,row=0)
        ttk.Label(frame1,text="yes").grid(column=1,row=0)
        ttk.Radiobutton(frame1,value=1,variable=self.difusion, command=self.isDifusion).grid(column=2,row=0)
        ttk.Label(frame1,text="No").grid(column=4,row=0)
        ttk.Radiobutton(frame1,value=0,variable=self.difusion, command=self.isDifusion).grid(column=5,row=0)

        frame2=ttk.Frame(seccionDifusion)
        frame2.place(x="30",y="30")
        frame2.configure(width='900',height='200')
        labelradius = ttk.Label(frame2,text="Radius (in Angstroms) for:")
        labelradius.place(x="15",y="15")
        labelreact1 = ttk.Label(frame2,text="Reactant-1")
        labelreact1.place(x="30",y="35")
        self.radius_react_1 = tk.Entry(frame2,width=15,state='disabled')
        self.radius_react_1.place(x="95",y="35")
        labelreact1 = ttk.Label(frame2,text="Reactant-2")
        labelreact1.place(x="30",y="55")
        self.radius_react_2 = tk.Entry(frame2,width=15,state='disabled')
        self.radius_react_2.place(x="95",y="55")

        labelreact1 = ttk.Label(frame2,text="Reaction distance (in Angstroms)")
        labelreact1.place(x="30",y="75")
        self.ReactionDistance = tk.Entry(frame2,width=15,state='disabled')
        self.ReactionDistance.place(x="70",y="95")


    def isDifusion(self):
        if(self.difusion.get()==1):
            self.ReactionDistance['state'] = 'normal'
            self.radius_react_1  ['state'] = 'normal'
            self.radius_react_2  ['state'] = 'normal'
        else:
            self.radius_react_1['state'] = 'disabled'
            self.radius_react_2['state'] = 'disabled'
            self.ReactionDistance['state'] ='disabled'

    def SeccionPantalla(self,pos_x=370,pos_y=10):
        seccionPantalla= ttk.Frame(self.Principal)
        seccionPantalla.configure(width='600',height='700')
        seccionPantalla.place(x=str(pos_x),y=str(pos_y))
       
        boton = ttk.Button(seccionPantalla,text="Data ok, Run", command=self.run_calc)
        boton.place(x="250",y="10")
        
        self.ScrollePantalla(seccionPantalla)



        labelrate = ttk.Label(seccionPantalla)
        labelrate.configure(cursor='arrow', justify='left', relief='raised', text='Rate constant units:\n-For bimolecular(M-1 s-1)\n -For unimolecular reactions(s-1)')
        labelrate.place(anchor='nw', x='0', y='500')

        labelphpadvertence = ttk.Label(seccionPantalla)
        labelphpadvertence.configure(cursor='based_arrow_down', justify='center', relief='groove', takefocus=False)
        labelphpadvertence.configure(text='Please note that pH is not\nconsidered here.\n\nCheck for updates in \nthis topic')
        labelphpadvertence.place(anchor='nw', x='300', y='500')

    def ScrollePantalla(self, seccionPantalla):
        FrameResultados = ttk.Frame(seccionPantalla)
        FrameResultados.place( x='0', y='55')
        self.salida = ScrolledText(FrameResultados, wrap = "none", width = 35, height = 23)
        xsb = tk.Scrollbar(FrameResultados,orient="horizontal", command=self.salida.xview)        
        self.salida.grid(row=1,column =0,columnspan=1)       
        self.salida.focus()
        self.salida.configure(xscrollcommand=xsb.set)
        self.salida.bind("<Key>", lambda e: "break")
        xsb.grid(row=2, column=0, columnspan=1,sticky=E+N+S+W)

        self.salida2 = ScrolledText(FrameResultados, wrap = "none", width = 32, height = 23)
        xsb2 = tk.Scrollbar(FrameResultados,orient="horizontal", command=self.salida2.xview)        
        self.salida2.grid(row=1,column =1,columnspan=1)        
        self.salida2.focus()
        self.salida2.configure(xscrollcommand=xsb2.set)
        self.salida2.bind("<Key>", lambda e: "break")
        xsb2.grid(row=2, column=1, columnspan=1,sticky=E+N+S+W)
        
    def run_calc(self):
        c =self.radius_react_1.get()
        b =self.radius_react_2.get()
        a=self.ReactionDistance.get()
     
        react1_G =self.React_1       .getTextValue
        react2_G =self.React_2       .getTextValue
        prod1_G  =self.Prduct_1_adiab.getTextValue
        prod2_G  =self.Prduct_2_adiab.getTextValue
        prod1_Ev =self.Prduct_1_vert .getTextValue
        prod2_Ev =self.Prduct_2_vert .getTextValue
        react1_E =react1_G
        react2_E =react2_G
       
        
        if self.difusion.get() == 1 and (a =='' or b  =='' or  c ==''  ):
            messagebox.showerror(title="It is not possible to calculate", message="Please enter the missing value(s)")
            return
        
        aEnergy = 627.5095 * (prod1_G + prod2_G - react1_G - react2_G)
        aEnergy_round = round(aEnergy, 2)
        vEnergy = 627.5095 * (prod1_Ev + prod2_Ev - react1_E - react2_E)
        vEnergy_round = round(vEnergy, 2) 
        lam = (vEnergy - aEnergy)
        if lam == 0:
            messagebox.showerror(title="It is not possible to calculate", message="Please check Reacts and products values")
            return 

        lambda_round  = round(lam, 2)
        barrier:float = ((lam / 4) * (1 + (aEnergy / lam)) * (1 + (aEnergy / lam)))
        barrier_round = round(barrier, 2)
        temp          =  float(self.Temperatura.get())
        try:
            rateCte:float = 2.08e10 * temp * math.exp(-1.0*barrier * 1000 / (1.987 * temp))
        except:
            messagebox.showerror(   title  = "Math range error.",
                                    message= "Please check you data.")
            rateCte:float = nan                        
        
        if self.difusion.get() == 1:
            radMolA   :float  = float(self.radius_react_1.get())
            radMolB   :float  = float(self.radius_react_2.get())
            reactDist :float  = float(self.ReactionDistance.get())
            diffCoefA :float  = (self.kBoltz * temp) / (6 * 3.14159 * self.visc * radMolA)
            diffCoefB :float  = (self.kBoltz * temp) / (6 * 3.14159 * self.visc * radMolB)
            diffCoefAB:float  = diffCoefA + diffCoefB
            kDiff     :float  = 1000 * 4 * 3.14159 * diffCoefAB * reactDist * 6.02e23
            kCorrDiff :float  = (kDiff * rateCte) / (kDiff + rateCte)    
        title =self.Title.get()
        self.salida.delete('1.0', END)
        self.salida.insert(END,("Pathway:  " + title + "\n") )
        self.salida.insert(END,("Adiabatic energy (G) of reaction (kcal/mol):  " + str(round(aEnergy_round,2)) + "\n") )
        self.salida.insert(END,("Vertical energy (E) of reaction (kcal/mol):  " + str(round(vEnergy_round,2)) + "\n") )
        self.salida.insert(END,("Reorganization energy (kcal/mol):  " + str(round(lambda_round,2)) + "\n") )
        self.salida.insert(END,("Reaction barrier (kcal/mol):  " + str(round( barrier_round,2 ))+ "\n") )
        if self.difusion.get() == 0:
            self.salida.insert(END,("Rate Constant:  " + str(round(  rateCte,2)) ) )
        elif self.difusion.get() == 1:
            self.salida.insert(END,("Rate Constant:  " + str(round(kCorrDiff,2)) ))
        self.salida.insert(END, "\n\n-----------------------------------------------------\n\n\n")
    def About(self):
        pass
    
    def onSave(self):
        file_path:string=None
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                 filetypes=( ("Text files", "*.txt"),("All files", "*.*"))) 
        try:
            # Write the Prolog rule editor contents to the file location
            with open(file_path, "w+") as file: 
                file.write(
                    "Entry Values: \n\n"
                    "\t\tReact-1(adiab.): "  +str(self.React_1       .getTextValue) + "\n"+
                    "\t\tReact-2(adiab.): "  +str(self.React_2       .getTextValue) + "\n"+
                    "\t\tProduct-1(adiab.): "+str(self.Prduct_1_adiab.getTextValue) + "\n"+
                    "\t\tProduct-2(adiab.): "+str(self.Prduct_2_adiab.getTextValue) + "\n"+
                    "\t\tProduct-1(vert.): " +str(self.Prduct_1_vert .getTextValue) + "\n"+
                    "\t\tProduct-2(vert.): " +str(self.Prduct_2_vert .getTextValue) + "\n________________________\n\nOutput:\n"
                )
                file.write(
                    self.salida.get("1.0", END)+"\n")
                file.close()

        except FileNotFoundError:
            messagebox.showerror(   title  = "It is not possible to save",
                                    message= "Please contact to administrator")
            return
    def run(self):
        self.Principal.mainloop()

if __name__ == '__main__':
    app = EasyRate()
    app.run()