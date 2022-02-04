from tkinter import filedialog
import tkinter as tk
import tkinter
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import numpy as np
from tkinter import *
import matplotlib.pyplot as plt 
class EntradaDato(tk.Frame) :

    def Activar(self,Etiqueta="Sin nombre",buttontext="Browse",dato=0.0,info=""):
        self.dato=dato
        self.Etiqueta =Etiqueta
        self.textoButton=buttontext
        self.labelEtiquetaNombre = tk.Label(self,text=self.Etiqueta,width=13,font = ('calibri', 10))
        self.datoentrada = tk.Entry(self,width=6)
        self.datoentrada.insert(0,str(self.dato))
        self.botonActivo =tk.Button(self,text=self.textoButton,width=7)
        self.grid(pady=5)
        self.labelEtiquetaNombre.grid(row = 0, column = 1,padx=4)
        self.datoentrada.grid(row = 0, column = 2,padx=4)
        self.botonActivo.grid(row = 0, column = 3,padx=4)
        

class MarcusApp:
    def __init__(self, master=None):
        self.Principal = tk.Tk() if master is None else tk.Toplevel(master)
        self.FramePrincipal = tk.Frame(self.Principal, container='false')
        self.Principal.title("Marcus 1.1")
        self.Principal.resizable(False, False)
        self.Principal.geometry("710x550")

        self.menu()
        
        self.SeccionLeerArchivos()
        self.SeecionTemperatura()
        self.SeccionDifusion()
        self.SeccionPantalla()
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
        seccionLeerArchivos.configure(width='230',height='270',highlightbackground='#000000', highlightcolor='#000000')

        labelData_entry = tk.Label(self.Principal,text="Data entry",font = ('calibri', 11, 'bold'))
        labelData_entry.place(x=str(pos_x), y=str(pos_y))
        
        seccionLeerArchivos.place(anchor='nw', bordermode='outside', x=str(pos_x), y=str(pos_y+10))

        tabla =tk.Frame(seccionLeerArchivos)
        tabla.place(anchor='nw', bordermode='outside', x='10', y='10')

        labelEtiquetaNombre = tk.Label(tabla,text="Run title")
        labelEtiquetaNombre.grid(row = 1, column = 1)

        self.Title = tk.Entry(tabla)
        self.Title.grid(row = 1, column = 2)
        self.React_1        = EntradaDato(tabla)
        self.React_1       .grid(row=2,column=1,columnspan = 3) 
        self.React_1       .Activar(Etiqueta="React-1(adiab.)") 
        self.React_2        = EntradaDato(tabla)
        self.React_2       .grid(row=3,column=1,columnspan = 3) 
        self.React_2       .Activar(Etiqueta="React-2(adiab.)")
        self.Prduct_1_adiab = EntradaDato(tabla)
        self.Prduct_1_adiab.grid(row=4,column=1,columnspan = 3) 
        self.Prduct_1_adiab.Activar(Etiqueta="Product-1(adiab.)")
        self.Prduct_2_adiab = EntradaDato(tabla)
        self.Prduct_2_adiab.grid(row=5,column=1,columnspan = 3) 
        self.Prduct_2_adiab.Activar(Etiqueta="Product-2(adiab.)")
        self.Prduct_1_vert  = EntradaDato(tabla)
        self.Prduct_1_vert .grid(row=6,column=1,columnspan = 3) 
        self.Prduct_1_vert .Activar(Etiqueta="Product-1(vert.)")
        self.Prduct_2_vert  = EntradaDato(tabla)
        self.Prduct_2_vert .grid(row=7,column=1,columnspan = 3) 
        self.Prduct_2_vert .Activar(Etiqueta="Product-2(vert.)")


    def SeecionTemperatura(self,pos_x=30,pos_y=330): 
        seccionTemperatura= tk.Frame(self.Principal)
        seccionTemperatura.configure(width='200',height='50',highlightbackground='#333333', highlightcolor='#000000')
        seccionTemperatura.place(x=str(pos_x),y=str(pos_y+15))
        labelEtiquetaTemperatura = tk.Label(seccionTemperatura,text="Temperature(K)",font = ('calibri', 10, 'bold'))
        labelEtiquetaTemperatura.grid(row = 1, column = 1)

        self.Temperatura = tk.Entry(seccionTemperatura)
        self.Temperatura.grid(row = 1, column = 2)
        self.Temperatura.insert(0,"298.15")

    def SeccionDifusion(self,pos_x=30,pos_y=370):
        seccionDifusion= tk.Frame(self.Principal)
        seccionDifusion.configure(width='290',height='400',highlightbackground='#333333', highlightcolor='#000000')
        seccionDifusion.place(x=str(pos_x),y=str(pos_y))
        frame1=tk.Frame(seccionDifusion)
        frame1.place(x="1",y="10")
        labelEtiquetaDifusion = tk.Label(frame1,text="Do you want to consider difusion?",font = ('calibri', 10, )).grid(column=0,row=0)
        labelEtiquetaDifusion = tk.Label(frame1,text="no",font = ('calibri', 9, "bold")).grid(column=1,row=0)
        self.difusion =tk.Radiobutton(frame1).grid(column=2,row=0)
        labelEtiquetaDifusion = tk.Label(frame1,text="yes",font = ('calibri', 9,"bold" )).grid(column=3,row=0)
        difusionfalse =tk.Radiobutton(frame1).grid(column=4,row=0)
        frame2=tk.Frame(seccionDifusion)
        frame2.place(x="30",y="30")
        frame2.configure(width='200',height='200')
        labelradius = tk.Label(frame2,text="Radius (in Angstroms) for:",font = ('calibri', 10 ))
        labelradius.place(x="15",y="15")
        labelreact1 = tk.Label(frame2,text="Reactant-1",font = ('calibri', 10 ))
        labelreact1.place(x="30",y="35")
        self.radius_react_1 = tk.Entry(frame2,width=15)
        self.radius_react_1.place(x="95",y="35")
    def SeccionPantalla(self,pos_x=360,pos_y=30):
        seccionPantalla= tk.Frame(self.Principal)
        seccionPantalla.configure(width='350',height='500',highlightbackground='#333333', highlightcolor='#000000')
        seccionPantalla.place(x=str(pos_x),y=str(pos_y))
       
        boton = tk.Button(seccionPantalla,text="Data ok,Run",font = ('calibri', 10 ))
        boton.place(x="75",y="15")

        frame10 = tk.Frame(seccionPantalla)
        frame10.place( x='0', y='45')


        salida = ScrolledText(frame10, wrap = "none", width = 35, height = 20)
        xsb = tk.Scrollbar(frame10,orient="horizontal", command=salida.xview)        
        
        salida.grid(row=1,column =0,columnspan=1)        
        salida.focus()
        salida.configure(xscrollcommand=xsb.set)
        xsb.grid(row=2, column=0, columnspan=1,sticky=E+N+S+W)
        
        labelrate = tk.Label(seccionPantalla)
        labelrate.configure(cursor='arrow', justify='left', relief='raised', text='Rate constant units:\n-For bimolecular(M-1 s-1)\n -For unimolecular reactions(s-1)')
        labelrate.place(anchor='nw', x='0', y='400')

        labelphpadvertence = tk.Label(seccionPantalla)
        labelphpadvertence.configure(cursor='based_arrow_down', justify='center', relief='groove', takefocus=False)
        labelphpadvertence.configure(text='Plese note that pH is not\nconsidered here.\n\nCheck for updates in \nthis topic')
        labelphpadvertence.place(anchor='nw', width='140', x='200', y='400')






    def About(self):
        pass
    def onSave(self):
        files = [('All Files', '*.*')]
    def run(self):
        self.Principal.mainloop()


if __name__ == '__main__':
    app = MarcusApp()
    app.run()