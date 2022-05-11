import tkinter as tk
from tkinter import INSERT, N,E,W,S, scrolledtext
from read_log_gaussian.Estructura import Estructura
class ViewStructure:
    def __init__(self, master=None, estructure =Estructura ):
        self.Principal = tk.Tk() if master is None else tk.Toplevel(master)
        self.Principal.title("View")
        self.Principal.resizable(False, False)
        self.Principal.geometry("400x400")
        salida = scrolledtext.ScrolledText(self.Principal,wrap = "none",width=40,height=20)
        xsb = tk.Scrollbar(self.Principal,orient="horizontal", command=salida.xview)        
        salida.grid(row=0,column =0,columnspan=1)        
        salida.focus()
        salida.configure(xscrollcommand=xsb.set)
        xsb.grid(row=2, column=0, columnspan=1,sticky=E+N+S+W)
        salida.insert(INSERT,str(estructure))
        xsb.grid(row=2, column=0, columnspan=1,sticky=E+N+S+W)