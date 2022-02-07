import math
import os
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename
from SeslectStructura import SelectStructure
from viewStructure import ViewStructure
from tkdialog import WaitAlert
from read_log_gaussian.read_log_gaussian import *
import threading

class EntradaDato(tk.Frame) :
    def Activar(self,Etiqueta="Sin nombre",buttontext="Browse",dato=0.0,info="",command =None):
        self.__dato=dato
        self.Etiqueta =Etiqueta
        self.textoButton=buttontext
        self.labelEtiquetaNombre = tk.Label(self,text=self.Etiqueta,width=13,font = ('calibri', 10))
        self.datoentrada = tk.Entry(self,width=6)
        self.datoentrada.insert(0,str(self.__dato))
        self.botonActivo =tk.Button(self,text=self.textoButton,width=7,command=self.open)
        self.grid(pady=5)
        self.labelEtiquetaNombre.grid(row = 0, column = 1,padx=4)
        self.datoentrada.grid(row = 0, column = 2,padx=4)
        self.botonActivo.grid(row = 0, column = 3,padx=4)
        #self.datoentrada.config(state='disabled')
        
        self.Archlog:read_log_gaussian =None
        self.filname=""
        self.esperar:int =0
        self.botonverfile = tk.Button(self,text="view",width=5,command=self.view)
        self.botonverfile.grid(row = 0, column = 4,padx=4)
        self.botonverfile['state'] ="disabled"
        self.labelEtiquetafilename = tk.Label(self,text="",width=13,font = ('calibri', 8), fg='#aaa')
        self.labelEtiquetafilename.grid(row = 1, column = 3,padx=4)
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

class MarcusApp:
    def __init__(self, master=None):
        self.Principal = tk.Tk() if master is None else tk.Toplevel(master)
        self.FramePrincipal = tk.Frame(self.Principal, container='false')
        self.Principal.title("Marcus 1.1")
        self.Principal.resizable(False, False)
        self.Principal.geometry("750x610")
        self.menu() 
        self.SeecionTemperatura()
        self.SeccionDifusion()
        self.SeccionPantalla() 
        self.SeccionLeerArchivos()
        self.visc = 8.91e-4 
        self.kBoltz = 1.38E-23

    def menu(self):
        menubar = tk.Menu(self.Principal)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save",command=self.onSave)
        filemenu.add_command(label="Exit",command=self.Principal.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="help", menu=help)
        help.add_command(label="About",command=self.About)
        
        self.Principal.config(menu=menubar)
    

    def SeccionLeerArchivos(self,pos_x=30,pos_y=40):
        seccionLeerArchivos = tk.Frame(self.Principal)
        seccionLeerArchivos.configure(width='310',height='355',highlightbackground='#000000', highlightcolor='#000000')

        labelData_entry = tk.Label(self.Principal,text="Data entry",font = ('calibri', 11, 'bold'))
        labelData_entry.place(x=str(pos_x), y=str(pos_y))
        
        seccionLeerArchivos.place(anchor='nw', bordermode='outside', x=str(pos_x), y=str(pos_y+10))

        tabla =tk.Frame(seccionLeerArchivos)
        tabla.place(anchor='nw', bordermode='outside', x='10', y='10')

        labelEtiquetaNombre = tk.Label(tabla,text="Run title")
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
        
        self.Prduct_2_vert  = EntradaDato(tabla)
        self.Prduct_2_vert .grid(row=7,column=1,columnspan = 3) 
        self.Prduct_2_vert .Activar(Etiqueta="Product-2(vert.)"
                            ,command=self.defPrduct_2_vert )


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
    def defPrduct_2_vert (self,Estruc:Estructura):
        self.Prduct_2_vert.setDato(UnDato=Estruc.scf.getValue)


    def SeecionTemperatura(self,pos_x=30,pos_y=400): 
        seccionTemperatura= tk.Frame(self.Principal)
        seccionTemperatura.configure(width='200',height='50',highlightbackground='#333333', highlightcolor='#000000')
        seccionTemperatura.place(x=str(pos_x),y=str(pos_y+15))
        labelEtiquetaTemperatura = tk.Label(seccionTemperatura,text="Temperature(K)",font = ('calibri', 10, 'bold'))
        labelEtiquetaTemperatura.grid(row = 1, column = 1)
        self.Temperatura = tk.Entry(seccionTemperatura)
        self.Temperatura.grid(row = 1, column = 2)
        self.Temperatura.insert(0,"298.15")

    def SeccionDifusion(self,pos_x=30,pos_y=440):
        seccionDifusion= tk.Frame(self.Principal)
        seccionDifusion.configure(width='290',height='400',highlightbackground='#333333', highlightcolor='#000000')
        seccionDifusion.place(x=str(pos_x),y=str(pos_y))
        frame1=tk.Frame(seccionDifusion)
        frame1.place(x="1",y="10")
        self.difusion=IntVar()
        self.difusion.set(0)
        tk.Label(frame1,text="Do you want to consider difusion?",font = ('calibri', 10, )).grid(column=0,row=0)
        tk.Label(frame1,text="yes",font = ('calibri', 9, "bold")).grid(column=1,row=0)
        tk.Radiobutton(frame1,value=1,variable=self.difusion, command=self.isDifusion).grid(column=2,row=0)
        tk.Label(frame1,text="No",font = ('calibri', 9,"bold" )).grid(column=4,row=0)
        tk.Radiobutton(frame1,value=0,variable=self.difusion, command=self.isDifusion).grid(column=5,row=0)

        frame2=tk.Frame(seccionDifusion)
        frame2.place(x="30",y="30")
        frame2.configure(width='900',height='200')
        labelradius = tk.Label(frame2,text="Radius (in Angstroms) for:",font = ('calibri', 10 ))
        labelradius.place(x="15",y="15")
        labelreact1 = tk.Label(frame2,text="Reactant-1",font = ('calibri', 10 ))
        labelreact1.place(x="30",y="35")
        self.radius_react_1 = tk.Entry(frame2,width=15,state='disabled')
        self.radius_react_1.place(x="95",y="35")
        labelreact1 = tk.Label(frame2,text="Reactant-2",font = ('calibri', 10 ))
        labelreact1.place(x="30",y="55")
        self.radius_react_2 = tk.Entry(frame2,width=15,state='disabled')
        self.radius_react_2.place(x="95",y="55")

        labelreact1 = tk.Label(frame2,text="Reaction distance (in Angstroms)",font = ('calibri', 10 ))
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

    def SeccionPantalla(self,pos_x=360,pos_y=30):
        seccionPantalla= tk.Frame(self.Principal)
        seccionPantalla.configure(width='550',height='500',highlightbackground='#333333', highlightcolor='#000000')
        seccionPantalla.place(x=str(pos_x),y=str(pos_y))
       
        boton = tk.Button(seccionPantalla,text="Data ok,Run",font = ('calibri', 10 ), command=self.run_calc)
        boton.place(x="120",y="10")
        frame10 = tk.Frame(seccionPantalla)
        frame10.place( x='0', y='55')
        self.salida = ScrolledText(frame10, wrap = "none", width = 51, height = 20,font=('bold', 10))
        xsb = tk.Scrollbar(frame10,orient="horizontal", command=self.salida.xview)        
        
        self.salida.grid(row=1,column =0,columnspan=1)        
        self.salida.focus()
        self.salida.configure(xscrollcommand=xsb.set)
        xsb.grid(row=2, column=0, columnspan=1,sticky=E+N+S+W)
        self.salida.bind("<Key>", lambda e: "break")
        labelrate = tk.Label(seccionPantalla)
        labelrate.configure(cursor='arrow', justify='left', relief='raised', text='Rate constant units:\n-For bimolecular(M-1 s-1)\n -For unimolecular reactions(s-1)')
        labelrate.place(anchor='nw', x='0', y='400')

        labelphpadvertence = tk.Label(seccionPantalla)
        labelphpadvertence.configure(cursor='based_arrow_down', justify='center', relief='groove', takefocus=False)
        labelphpadvertence.configure(text='Plese note that pH is not\nconsidered here.\n\nCheck for updates in \nthis topic')
        labelphpadvertence.place(anchor='nw', width='140', x='200', y='400')

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
        rateCte:float = 2.08e10 * temp * math.exp(-1.0*barrier * 1000 / (1.987 * temp))
        
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
    app = MarcusApp()
    app.run()