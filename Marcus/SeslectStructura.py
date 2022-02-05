from tkinter import *
import tkinter as tk
import tkinter
from tkinter import scrolledtext
from tkinter.scrolledtext import *
from tkinter.filedialog import *
from pygubu import TkApplication
from tkinter import *
import tkinter.simpledialog as sd
import platform

from read_log_gaussian import *

class SelectStructure(sd.Dialog):
    """An alert which will wait for a given time before user can interact.

    Args:
        parent: Takes the parent window instance.
        title (str): Main heading of the alert.
        message (str): Information to display.
        pause (int): Time till inactive. (in seconds)
        show_timer (boolean): Shows countdown."""

    def __init__(self, parent, Estructuras:"list[Estructura]" ):
        super().__init__(parent, title="Select a Structure")
