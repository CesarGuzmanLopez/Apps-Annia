import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import pandas as pd
from rdkit import Chem, rdBase
from rdkit.Chem import PandasTools, Descriptors, rdMolDescriptors, AllChem
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import webbrowser
from rdkit.Chem.AllChem import GetConformerRMS
import subprocess
import json
from documentation import open_notebook

import matplotlib as mpl
mpl.rcParams.update({
    "font.family": "serif",      # algo tipo LaTeX
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,          # apagamos grid global, lo controlamos a mano
    "text.usetex": False         # usamos mathtext, no LaTeX externo (más portable)
})


	
#-------------------------------------------------------------------------------------------------------------------------------------------
# CONTACT INFORMATION
#-------------------------------------------------------------------------------------------------------------------------------------------
'''
This code was developed by Eduardo Gabriel Guzmán López any comment or suggestion please contact by e-mail:
email: eggl.quimica@gmail.com

Universidad Autónoma Metropolitana
Universidad Nacional Autónoma de México

# Name                    Version                   Build  Channel
pandas                    2.1.4           py310hdba192b_0    conda-forge
python                    3.10.13         h00d2728_1_cpython    conda-forge
rdkit                     2023.09.4       py310hbbc110b_0    conda-forge
py3dmol-2.1.0              |     pyhd8ed1ab_0          12 KB  conda-forge

   ___ _____  _         _   _   _    __  __ ___ 
  / _ \_   _|/ \       | | | | / \  |  \/  |_ _|
 | | | || | / _ \ _____| | | |/ _ \ | |\/| || | 
 | |_| || |/ ___ \_____| |_| / ___ \| |  | || | 
  \__\_\|_/_/   \_\     \___/_/   \_\_|  |_|___|
                                                

Para empaquetar este software usar
 bash clean.sh
 bash package.sh

'''
#-------------------------------------------------------------------------------------------------------------------------------------------
# Variables globales
csv_processed = False
merged_data = None
# Desactivar el warning de RDKit sobre la versión
rdBase.DisableLog('rdApp.error')

#-------------------------------------------------------------------------------------------------------------------------------------------
# CONTACT INFO and DOCUMENTATION
#-------------------------------------------------------------------------------------------------------------------------------------------

# Ruta relativa para la documentación
def open_documentation():
    documentation_path = os.path.join(os.path.dirname(__file__), "CADMApy.pdf")
    print(documentation_path)  # Línea añadida para verificar la ruta
    if os.path.exists(documentation_path):
        try:
            if os.name == 'posix':  # macOS o Linux
                subprocess.call(('open', documentation_path))
            elif os.name == 'nt':  # Windows
                os.startfile(documentation_path)
            else:
                webbrowser.open_new(f"file://{documentation_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the documentation file: {e}")
    else:
        messagebox.showerror("Error", "The documentation file was not found.")

def shorten_path(path, levels=2):
    """
    Devuelve solo los últimos `levels` niveles de una ruta.
    Ejemplo: /a/b/c/d/e.txt → c/d/e.txt  (levels=2)
    """
    path = path.replace("\\", "/")
    parts = path.split("/")
    return "/".join(parts[-levels-1:])

def open_link(url):
    webbrowser.open_new(url)

# Función para mostrar la información de contacto con enlaces
def show_contact_info():
    contact_info_window = tk.Toplevel()
    contact_info_window.title("CONTACT & REFERENCES")
    contact_info_window.configure(bg="#FFFFFF")

    info_text = (
        "Developed by \n \tEduardo Gabriel Guzmán-López (1,2,3) \n \t Luis Felipe Hernández-Ayala (1,3) \n \t Adriana Perez-Gonzalez (1)  \n \t Miguel Reina (3) \n \t Annia Galano (1)\n"
        "\nemail: eggl.quimica@gmail.com\n"
        "\nTheoretical and Applied Chemistry Group of Dr. Annia Galano\n"
        " 1) Departamento de Química, UAM-Iztapalapa\n"
        " 2) Departamento de Sistemas Biológicos, UAM-Xochimilco\n"
        " 3) Facultad de Química - UNAM\n\n"

        "How to cite:"
    )
    info_label = tk.Label(contact_info_window, text=info_text, font=("Helvetica", 14), bg="#FFFFFF", justify="left")
    info_label.pack(pady=5, padx=10)

    link1 = tk.Label(contact_info_window, text="1. Guzman-Lopez, E.G.; Reina, M.; Perez-Gonzalez, A.; Francisco-Marquez, M.; Hernandez-Ayala, L.F.; Castañeda-Arriaga, R.; Galano, A. Int. J. Mol. Sci. 2022, 23, 13246.", font=("Helvetica", 12), bg="#FFFFFF", fg="blue", cursor="hand2", justify="left", wraplength=500)
    link1.pack(pady=5, padx=10)
    link1.bind("<Button-1>", lambda e: open_link("https://doi.org/10.3390/ijms232113246"))

    link2 = tk.Label(contact_info_window, text="2. Guzmán-López, E.G.; Reina, M.; Hernández-Ayala, L.F.; Galano, A. Antioxidants 2023, 12, 1256.", font=("Helvetica", 12), bg="#FFFFFF", fg="blue", cursor="hand2", justify="left", wraplength=500)
    link2.pack(pady=5, padx=10)
    link2.bind("<Button-1>", lambda e: open_link("https://doi.org/10.3390/antiox12061256"))

    close_button = tk.Button(contact_info_window, text="Close", command=contact_info_window.destroy, bg="#FFFFFF", fg="black")
    close_button.pack(pady=10)

    center_window(contact_info_window, 550, 350)


#-------------------------------------------------------------------------------------------------------------------------------------------
# Global information about property ranges, pandas options and the dictionary of values by each disease.
#-------------------------------------------------------------------------------------------------------------------------------------------

# Configura pandas para mostrar más filas y columnas
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def actualizar_rangos():
    global rangos, rangos_vars
    if 'rangos_vars' not in globals():
        return
    for prop, (min_var, max_var) in rangos_vars.items():
        rangos[prop] = (float(min_var.get()), float(max_var.get()))


# Definición de rangos  QTA-Lipinski
rangos = {
    'MW': (200, 400),
    'logP': (2, 3),
    'MR': (40, 130),
    'AtX': (20, 50),
    'HBLA': (0, 6),
    'HBLD': (0, 3),
    'RB': (0, 10),
    'PSA': (0, 70),
}

# Definir los diccionarios de valores para cada enfermedad
# ----------------------------------------------------------
# Carga y guardado persistente de enfermedades y archivos RefSet
# ----------------------------------------------------------

ENFERMEDADES_FILE = os.path.join(os.path.dirname(__file__), "valores_enfermedades.json")
DISEASE_FILES_FILE = os.path.join(os.path.dirname(__file__), "disease_files.json")

def load_valores_enfermedades():
    """Carga el diccionario de enfermedades desde JSON; si no existe, usa defaults."""
    default_valores = {
        'Neurodegenerativas 🧠': {
            'LD50_farmacos': 1131.37,
            'StdDevSet_LD50': 1588.67,
            'M_farmacos': 0.377,
            'StdDevSet_M': 0.274,
            'DT_farmacos': 0.743,
            'StdDevSet_DT': 0.168,
            'SA_farmacos': 74.07,
            'StdDevSet_SA': 14.318,
            'AverageRefSet_MW': 291.31,
            'StdDevSet_MW': 98.53,
            'AverageRefSet_logP': 2.55,
            'StdDevSet_logP': 1.63,
            'AverageRefSet_MR': 81.67,
            'StdDevSet_MR': 27.03,
            'AverageRefSet_AtX': 20.82,
            'StdDevSet_AtX': 6.83,
            'AverageRefSet_HBLA': 3.6,
            'StdDevSet_HBLA': 1.86,
            'AverageRefSet_HBLD': 1.42,
            'StdDevSet_HBLD': 1.27,
            'AverageRefSet_RB': 4.44,
            'StdDevSet_RB': 2.94,
            'AverageRefSet_PSA': 57.53,
            'StdDevSet_PSA': 36.44
        },
        'RETT 👧🏻': {
            'LD50_farmacos': 1751.04,
            'StdDevSet_LD50': 2750.10,
            'M_farmacos': 0.21,
            'StdDevSet_M': 0.21,
            'DT_farmacos': 0.74,
            'StdDevSet_DT': 0.19,
            'SA_farmacos': 76.98,
            'StdDevSet_SA': 12.83,
            'AverageRefSet_MW': 289.77,
            'StdDevSet_MW': 112.53,
            'AverageRefSet_logP': 2.22,
            'StdDevSet_logP': 2.33,
            'AverageRefSet_MR': 79.07,
            'StdDevSet_MR': 30.64,
            'AverageRefSet_AtX': 20.54,
            'StdDevSet_AtX': 7.95,
            'AverageRefSet_HBLA': 4.44,
            'StdDevSet_HBLA': 2.70,
            'AverageRefSet_HBLD': 2.31,
            'StdDevSet_HBLD': 2.34,
            'AverageRefSet_RB': 4.23,
            'StdDevSet_RB': 3.84,
            'AverageRefSet_PSA': 68.01,
            'StdDevSet_PSA': 45.51
        }
    }

    if os.path.exists(ENFERMEDADES_FILE):
        try:
            with open(ENFERMEDADES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {ENFERMEDADES_FILE}: {e}")
            return default_valores
    else:
        # Si no existe el archivo, guarda los defaults la primera vez
        try:
            with open(ENFERMEDADES_FILE, "w", encoding="utf-8") as f:
                json.dump(default_valores, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error writing default {ENFERMEDADES_FILE}: {e}")
        return default_valores

def save_valores_enfermedades():
    """Guarda el diccionario global valores_enfermedades a JSON."""
    try:
        with open(ENFERMEDADES_FILE, "w", encoding="utf-8") as f:
            json.dump(valores_enfermedades, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving {ENFERMEDADES_FILE}:\n{e}")

def load_disease_files():
    """Carga el mapeo enfermedad -> archivo RefSet, con defaults."""
    default_disease_files = {
        'Neurodegenerativas 🧠': os.path.join(os.path.dirname(__file__), "Neuro_RefSet.csv"),
        'RETT 👧🏻': os.path.join(os.path.dirname(__file__), "RETT_RefSet.csv"),
    }

    if os.path.exists(DISEASE_FILES_FILE):
        try:
            with open(DISEASE_FILES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Convertir a rutas absolutas si hiciera falta
            return data
        except Exception as e:
            print(f"Error loading {DISEASE_FILES_FILE}: {e}")
            return default_disease_files
    else:
        try:
            with open(DISEASE_FILES_FILE, "w", encoding="utf-8") as f:
                json.dump(default_disease_files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error writing default {DISEASE_FILES_FILE}: {e}")
        return default_disease_files



def calcular_suma_adme_enfermedad(enfermedad: str) -> int:
    csv_path = disease_files.get(enfermedad, None)
    if not csv_path or not os.path.exists(csv_path):
        print(f"[Aviso] No se encontró archivo RefSet para '{enfermedad}'. Usando len(rangos) como fallback.")
        return len(rangos)

    try:
        df_ref = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[Aviso] Error leyendo RefSet '{csv_path}' para '{enfermedad}': {e}")
        return len(rangos)

    suma = 0
    for prop, (min_val, max_val) in rangos.items():
        if prop not in df_ref.columns:
            continue

        serie = pd.to_numeric(df_ref[prop], errors="coerce").dropna()
        if serie.empty:
            continue

        avg = float(serie.mean())
        #Debug para ver que intervalos se están leyendo.

#        print(f"[DEBUG] {enfermedad} - {prop}: avg={avg:.2f}, rango=({min_val}, {max_val}) "
#              f"-> {'✔' if min_val <= avg <= max_val else '✘'}")

        if min_val <= avg <= max_val:
            suma += 1

    if suma == 0:
        print(f"[Aviso] Ninguna propiedad ADME pudo evaluarse para '{enfermedad}'. Usando len(rangos) como fallback.")
        return len(rangos)

    return suma


'''
def calcular_suma_adme_enfermedad(enfermedad: str) -> int:
    """
    Calcula cuántas propiedades ADME del RefSet de la enfermedad dada
    cumplen que el **promedio** del RefSet cae dentro del intervalo CADMA-Chem.
    """
    csv_path = disease_files.get(enfermedad, None)
    if not csv_path or not os.path.exists(csv_path):
        print(f"[Aviso] No se encontró archivo RefSet para '{enfermedad}'. Usando len(rangos) como fallback.")
        return len(rangos)

    try:
        df_ref = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[Aviso] Error leyendo RefSet '{csv_path}' para '{enfermedad}': {e}")
        return len(rangos)

    suma = 0
    for prop, (min_val, max_val) in rangos.items():
        if prop not in df_ref.columns:
            # Si el RefSet no tiene esa propiedad, la saltamos
            continue

        serie = pd.to_numeric(df_ref[prop], errors="coerce").dropna()
        if serie.empty:
            continue

        avg = float(serie.mean())

        #  Aquí el debug para que veas qué pasa
        print(f"[DEBUG] {enfermedad} - {prop}: avg={avg:.2f}, rango=({min_val}, {max_val}) "
              f"-> {'✔' if min_val <= avg <= max_val else '✘'}")

        if min_val <= avg <= max_val:
            suma += 1

    if suma == 0:
        print(f"[Aviso] Ninguna propiedad ADME pudo evaluarse para '{enfermedad}'. Usando len(rangos) como fallback.")
        return len(rangos)

    return suma'''


def save_disease_files():
    """Guarda el diccionario global disease_files a JSON."""
    try:
        with open(DISEASE_FILES_FILE, "w", encoding="utf-8") as f:
            json.dump(disease_files, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving {DISEASE_FILES_FILE}:\n{e}")


# Cargar al inicio
valores_enfermedades = load_valores_enfermedades()
disease_files = load_disease_files()


#-------------------------------------------------------------------------------------------------------------------------------------------
#Globally accesible features 
#-------------------------------------------------------------------------------------------------------------------------------------------

# Función para centrar la ventana en la pantalla
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Función para graficar cualquier columna del dataframe, solamente hay que pasar el argumento de qué columna se desea graficar, útil para graficar lo que sea.
def latex_label_for_score(score_col: str) -> str:
    """
    Convierte nombres de columnas tipo 'S_S', 'S_ADME', etc.
    en labels con formato LaTeX bonito.
    """
    mapping = {
        "S_S":      r"$S_{\mathrm{S}}$",
        "S_ADME":   r"$S_{\mathrm{ADME}}$",
        "S_ADMET":  r"$S_{\mathrm{ADMET}}$",
        "S_T":      r"$S_{\mathrm{T}}$",
        "S_SA":     r"$S_{\mathrm{SA}}$",
        "S_LD50":   r"$S_{\mathrm{LD50}}$",
        "S_M":      r"$S_{\mathrm{M}}$",
        "S_DT":     r"$S_{\mathrm{DT}}$"
    }
    return mapping.get(score_col, score_col)


def show_graph(score_col, title, xlabel, ylabel, compound_label=None,
               legend_loc='best', parent=None):
    """
    Dibuja un gráfico de barras de 'score_col' vs 'Compound' usando cleaned_data,
    embebido en una ventana Tkinter (parent = graph_window).
    """
    global cleaned_data, acronimo_var

    if parent is None:
        raise ValueError("show_graph requiere un 'parent' (ventana Tkinter) para dibujar.")

    if cleaned_data is None or score_col not in cleaned_data.columns:
        messagebox.showerror("Error", f"La columna '{score_col}' no está disponible en los datos.")
        return

    plt.close('all')  # evita figuras sueltas

    # Copia de trabajo
    df = cleaned_data.copy()

    # Eje X: nombres de compuestos
    if 'Compound' in df.columns:
        x_labels = df['Compound'].astype(str).tolist()
    else:
        x_labels = df.index.astype(str).tolist()

    y_values = df[score_col].values
    n = len(x_labels)

    # ==== FIGURA "PUBLICABLE" ====
    fig = Figure(figsize=(7, 4), dpi=150)
    ax = fig.add_subplot(111)

    # ---- Rango dinámico del eje Y (sin NaN ni ceros) ----
    y_valid = y_values[np.isfinite(y_values) & (y_values != 0)]
    if len(y_valid) > 0:
        y_min = float(y_valid.min())
        y_max = float(y_valid.max())

        if y_min == y_max:
            # Si todas las barras tienen el mismo valor, abrimos un margen pequeño
            delta = max(abs(y_min) * 0.05, 0.01)
            y_min -= delta
            y_max += delta
        else:
            # Margen del 5 % por arriba y por abajo
            margin = 0.05 * (y_max - y_min)
            y_min -= margin
            y_max += margin

        ax.set_ylim(y_min, y_max)

    # ------------------------------------------------------------------
    # Manejo dinámico de etiquetas del eje X según el zoom
    # ------------------------------------------------------------------
    max_labels = 35  # máximo de etiquetas visibles al mismo tiempo

    def update_xticks(event=None):
        try:
            if n == 0:
                return

            x_min, x_max = ax.get_xlim()

            # Índices visibles (intersección con [0, n-1])
            i_min = max(int(np.floor(x_min)), 0)
            i_max = min(int(np.ceil(x_max)), n - 1)
            if i_max < i_min:
                return

            visible_idx = np.arange(i_min, i_max + 1, dtype=int)
            n_visible = len(visible_idx)

            if n_visible <= max_labels:
                use_idx = visible_idx
            else:
                step = int(np.ceil(n_visible / max_labels))
                use_idx = visible_idx[::step]

            # Asegurar que están en rango
            use_idx = [i for i in use_idx if 0 <= i < n]
            if not use_idx:
                return

            ax.set_xticks(use_idx)
            ax.set_xticklabels([x_labels[i] for i in use_idx],
                               rotation=45, ha='right')
        except Exception as e:
            # Evita que errores del callback tumben toda la app
            print("Error en update_xticks:", repr(e))

    # Colores en escala de grises
    base_color = "0.7"   # gris claro
    edge_color = "0.1"   # borde casi negro
    highlight_color = "0.3"  # gris más oscuro para compuesto seleccionado

    # Índice del compuesto seleccionado, si existe
    sel_idx = None
    if compound_label is None and 'acronimo_var' in globals():
        compound_label = acronimo_var.get()

    if compound_label and 'Compound' in df.columns:
        matches = df.index[df['Compound'] == compound_label].tolist()
        if matches:
            # Convertir etiqueta de índice a posición entera
            try:
                sel_idx = df.index.get_loc(matches[0])
            except Exception:
                sel_idx = None

    # Dibujar barras
    x_pos = np.arange(n)
    bar_colors = [base_color] * n
    bar_hatch = [None] * n

    if sel_idx is not None and 0 <= sel_idx < n:
        bar_colors[sel_idx] = highlight_color
        bar_hatch[sel_idx] = '//'

    bars = ax.bar(x_pos, y_values,
                  color=bar_colors,
                  edgecolor=edge_color,
                  linewidth=0.6)

    # Aplicar hatch sólo a la barra seleccionada (opcional)
    if sel_idx is not None and 0 <= sel_idx < len(bars):
        bars[sel_idx].set_hatch(bar_hatch[sel_idx])

    # Título y ejes con estilo LaTeX-like
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel, fontsize=11)

    # Usamos el label LaTeX para el eje Y
    pretty_ylabel = latex_label_for_score(score_col)
    ax.set_ylabel(pretty_ylabel, fontsize=11)

    # Sólo grid horizontal y muy sutil
    ax.yaxis.grid(True, linestyle=':', linewidth=0.4, alpha=0.5)
    ax.xaxis.grid(False)

    # Bordes limpios
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # Llamada inicial de etiquetas (vista completa)
    update_xticks()
    
    # Línea horizontal en el score del compuesto seleccionado
    legend_labels = []

    if sel_idx is not None and 0 <= sel_idx < n:
        y_sel = float(y_values[sel_idx])
        ax.axhline(
            y=y_sel,
            color="green",
            linestyle="--",
            linewidth=0.8,
            #label=f"{compound_label}: {y_sel:.3f}"
        )

        ax.text(
            0.8, 0.8,                              # (x_frac, y_frac)
            f"{compound_label}: {y_sel:.3f}",
            transform=ax.transAxes,                # <<--- COORDENADAS DE EJE (0–1)
            fontsize=10,
            color="0.3",
            va="center",
            ha="left",
            fontfamily="monospace",
            #bbox=dict(facecolor="white", edgecolor="0.7", alpha=0.6),
            clip_on=False
        )
        legend_labels.append("ref")

    # Si estamos graficando S_S, dibujar también la línea S_S = 1
    if score_col == "S_S":
        ax.axhline(
            y=1.0,
            color="red",
            linestyle=":",
            linewidth=0.9,
            #label=r"$S_{\mathrm{S}} = 1$"
        )

        ax.text(
            0.8, 0.7,                         # (x_frac, y_frac)
            r"$S_{\mathrm{S}} = 1$",
            transform=ax.transAxes,             # <<--- COORDENADAS DE EJE (0–1)
            fontsize=10,
            color="0.4",
            va="center",
            ha="left",
            fontfamily="monospace",
            #bbox=dict(facecolor="white", edgecolor="0.7", alpha=0.6),
            clip_on=False
        )

        legend_labels.append("ss1")

    if legend_loc and legend_labels:
        ax.legend(loc=legend_loc, fontsize=9, frameon=False)

    fig.tight_layout()

    # ==== Embebido en Tkinter ====
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)

    # Conectar el callback al redibujado *en el canvas correcto*
    canvas.mpl_connect("draw_event", update_xticks)

    # Toolbar con botón de guardar
    toolbar_frame = ttk.Frame(parent)
    toolbar_frame.pack(fill='x')
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    return fig, canvas

# Función para cargar un archivo CSV y devolver su DataFrame
def load_file(label, file_type):
    filetypes = {
        "csv": [("CSV files", "*.csv")],
        "txt": [("Text files", "*.txt")],
        "smi": [("SMILES files", "*.smi")],
        "xlsx": [("Excel files", "*.xlsx")],
        "all": [("All files", "*.*")]
    }

    filetypes = filetypes.get(file_type, [("All files", "*.*")])
    
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        # Extrae solo el nombre del archivo de la ruta completa
        filename_only = os.path.basename(filename)
        # Actualiza el label con el nombre del archivo seleccionado
        label.config(text=filename_only)
    
    if filename:
        if file_type == "xlsx":
            return pd.read_excel(filename)
        else:
            return pd.read_csv(filename)
    else:
        return None

#Funciona para mandar la columna de smile al final del dataframe
def smiles_to_last(data_frame):
    cols = data_frame.columns.tolist()
    cols.append(cols.pop(cols.index('smile')))
    return data_frame[cols]

# Utilidades para manejo de SMILES
def validate_smiles(smiles):
    valid_smiles = []
    for smile in smiles:
        mol = Chem.MolFromSmiles(smile)
        if mol:
            valid_smiles.append(smile)
        else:
            print(f"Invalid SMILE: {smile}")
    return valid_smiles

#-------------------------------------------------------------------------------------------------------------------------------------------
# Section to create a new RefSet and their functions.
#-------------------------------------------------------------------------------------------------------------------------------------------

def load_smiles_with_names(path, label="SMILES"):
    """
    Lee un archivo de SMILES (smi/smiles/txt/csv) y devuelve 
    un DataFrame con columnas: ['name', 'smile'].

    Casos soportados:
    - .smi / .smiles / .txt:
        - Formato "SMILES  Name" (separado por espacios/tabs)
        - Formato "SMILES" solo → genera nombres Mol_001, Mol_002, ...
    - .csv:
        - Con columnas tipo ('name', 'smile'/'smiles')
        - Con solo una columna de SMILES → genera nombres Mol_001...
    """
    ext = os.path.splitext(path)[1].lower()

    # ------------------------------------------------------------------
    # 1) Archivos tipo línea-a-línea: .smi, .smiles, .txt
    # ------------------------------------------------------------------
    if ext in [".smi", ".smiles", ".txt"]:
        rows = []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                smi = parts[0]
                if len(parts) > 1:
                    name = " ".join(parts[1:])
                else:
                    name = f"Mol_{idx:03d}"

                rows.append({"name": name, "smile": smi})

        df = pd.DataFrame(rows)
        if df.empty:
            raise ValueError(f"El archivo de SMILES '{path}' está vacío o solo contiene comentarios.")
        return df

    # ------------------------------------------------------------------
    # 2) Archivos tipo tabla (CSV, TSV, etc.)
    # ------------------------------------------------------------------
    df = debug_read_csv(path, label)

    if df.empty:
        raise ValueError(f"El archivo de SMILES '{path}' está vacío.")

    # Normalizar nombres de columnas a minúsculas para detectar 'name' y 'smile(s)'
    lower_cols = {c.lower(): c for c in df.columns}

    name_col = None
    smi_col = None

    # Buscar columna de SMILES
    for key in ["smile", "smiles"]:
        if key in lower_cols:
            smi_col = lower_cols[key]
            break

    # Buscar columna de nombre
    for key in ["name", "compound", "id"]:
        if key in lower_cols:
            name_col = lower_cols[key]
            break

    # Caso: NO encontramos columna de SMILES
    if smi_col is None:
        # Si solo hay una columna, asumimos que son SMILES
        if df.shape[1] == 1:
            smi_col = df.columns[0]
        else:
            raise KeyError(
                f"No se encontró columna de SMILES ('smile' / 'smiles') en {path}. "
                f"Columnas disponibles: {list(df.columns)}"
            )

    smiles_series = df[smi_col].astype(str)

    # Caso: NO encontramos columna de nombre → generamos Mol_001, Mol_002, ...
    if name_col is None:
        names = [f"Mol_{i:03d}" for i in range(1, len(smiles_series) + 1)]
        out = pd.DataFrame({
            "name": names,
            "smile": smiles_series
        })
    else:
        out = df[[name_col, smi_col]].copy()
        out.columns = ["name", "smile"]

    # Limpiar espacios
    out["name"] = out["name"].astype(str).str.strip()
    out["smile"] = out["smile"].astype(str).str.strip()

    return out

def debug_read_csv(path, label):
    """
    Lee un archivo tipo CSV probando varios encodings y muestra en consola:
      - qué archivo está leyendo
      - qué encoding funcionó o falló
      - las primeras filas del DataFrame

    Limpia los nombres de las columnas (quita espacios, comillas y bytes raros).
    Devuelve un DataFrame listo para usar.
    """
    print(f"\n=== Intentando leer {label}: {shorten_path(path, levels=2)} ===")

    #print(f"\n=== Intentando leer {label}: {path} ===")

    encodings = ["utf-8", "utf-8-sig", "latin-1", "utf-16", "utf-16-le", "utf-16-be"]
    last_err = None

    for enc in encodings:
        try:
            # 👇 OJO: dejamos que pandas detecte el separador (sep=None)
            df = pd.read_csv(
                path,
                engine="python",
                encoding=enc,
                sep=None  # autodetección de separador
            )
            print(f"[OK] {label} leído con encoding: {enc}")
            print("Columnas originales de", label, ":", df.columns.tolist())

            # 🔧 Normalizar nombres de columnas:
            # - convertir a str
            # - quitar bytes nulos (\x00)
            # - quitar prefijo BOM extraño (ÿþ)
            # - quitar espacios alrededor
            # - quitar comillas dobles al inicio y final
            def _clean_col(c):
                s = str(c)
                s = s.replace("\x00", "")
                s = s.replace("ÿþ", "")
                s = s.strip().strip('"')
                return s

            df.columns = [_clean_col(c) for c in df.columns]
            #Quitar las comillas si existen
            df = df.map(lambda x: x.strip('"') if isinstance(x,str) else x)
        
            #Conver all columns to numeric values
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col],errors='ignore')
                except Exception:
                    pass


            print("Columnas normalizadas de", label, ":", df.columns.tolist())
            print(f"Primeras filas de {label}:")
            print(df.head())
            return df

        except UnicodeDecodeError as e:
            print(f"[Fallo] {label} con encoding {enc}: {e}")
            last_err = e
        except Exception as e:
            print(f"[Error] {label} con encoding {enc}: {e}")
            last_err = e

    # Si llegamos aquí, ningún encoding funcionó
    raise last_err

#Funciones para cargar los archivos de TEST
def load_dev_tox_file(path, label_suffix=""):
    """
    Lee archivo de Developmental Toxicity (TEST) y devuelve un DataFrame con la columna 'DT' (0–1).
    """
    label = f"Developmental_Toxicity{label_suffix}"
    df = debug_read_csv(path, label)

    if "Pred_Value" not in df.columns:
        raise KeyError(
            f"En {path} no se encontró la columna 'Pred_Value'. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    out = df[["Pred_Value"]].rename(columns={"Pred_Value": "DT"})
    out["DT"] = out["DT"].astype(float).clip(lower=0.0, upper=1.0)
    return out
def load_mutagenicity_file(path, label_suffix=""):
    """
    Lee archivo de Mutagenicity (TEST) y devuelve un DataFrame con la columna 'M' (0–1).
    """
    label = f"Mutagenicity{label_suffix}"
    df = debug_read_csv(path, label)

    if "Pred_Value" not in df.columns:
        raise KeyError(
            f"En {path} no se encontró la columna 'Pred_Value'. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    out = df[["Pred_Value"]].rename(columns={"Pred_Value": "M"})
    out["M"] = out["M"].astype(float).clip(lower=0.0, upper=1.0)
    return out
def load_ld50_file(path, label_suffix=""):
    """
    Lee archivo de Oral rat LD50 (TEST) y devuelve un DataFrame con la columna 'LD50' en mg/kg.
    Soporta encabezados:
      - Pred_Value:_mg/kg   (CONSENSUS original)
      - Pred_Value:mg/kg    (archivos fam1)
    """
    label = f"Oral_rat_LD50{label_suffix}"
    df = debug_read_csv(path, label)

    if "Pred_Value:_mg/kg" in df.columns:
        col_ld50 = "Pred_Value:_mg/kg"
    elif "Pred_Value:mg/kg" in df.columns:
        col_ld50 = "Pred_Value:mg/kg"
    else:
        raise KeyError(
            f"No se encontró la columna de LD50 ('Pred_Value:_mg/kg' o 'Pred_Value:mg/kg') en {path}. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    out = df[[col_ld50]].rename(columns={col_ld50: "LD50"})
    out["LD50"] = out["LD50"].astype(float)
    return out
def load_ambit_sa_file(path, label_suffix=""):
    """
    Lee archivo de Synthetic Accessibility (AMBIT-SA) y devuelve un DataFrame con la columna 'SA' como float.
    """
    label = f"Synthetic accessibility (AMBIT-SA){label_suffix}"
    df = debug_read_csv(path, label)

    if "SA" not in df.columns:
        raise KeyError(
            f"En {path} no se encontró la columna 'SA'. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    out = df[["SA"]].copy()
    out["SA"] = out["SA"].astype(float)
    return out

# Limpiar el archivo y propiedades ADME del RefSet
def load_and_process_smiles_for_RefSet(smiles_file):
    """
    Lee el archivo de SMILES del Reference Set (puede ser .smi/.smiles/.txt/.csv),
    normaliza a columnas ['name','smile'] y calcula las propiedades ADME:
    MW, logP, MR, AtX, HBLA, HBLD, RB, PSA.

    Devuelve un DataFrame con:
        ['name', 'smile', 'ROMol', 'MW', 'logP', 'MR',
         'AtX', 'HBLA', 'HBLD', 'RB', 'PSA']
    """
    if not smiles_file:
        raise ValueError("No se proporcionó archivo de SMILES para el Reference Set.")

    # 1) Leer SMILES con la función unificada
    smiles_df = load_smiles_with_names(smiles_file, label="SMILES (reference set)")

    # 2) Crear ROMol y filtrar inválidos
    smiles_df["ROMol"] = smiles_df["smile"].apply(Chem.MolFromSmiles)

    invalid_count = smiles_df["ROMol"].isna().sum()
    if invalid_count > 0:
        print(f"[Aviso] Se encontraron {invalid_count} SMILES inválidos en '{smiles_file}' y serán descartados.")

    smiles_df = smiles_df[smiles_df["ROMol"].notna()].copy()

    if smiles_df.empty:
        raise ValueError("Después de filtrar SMILES inválidos, no quedó ningún compuesto válido en el Reference Set.")

    # 3) Calcular descriptores ADME básicos
    smiles_df["MW"]   = smiles_df["ROMol"].apply(Descriptors.MolWt).round(2)
    smiles_df["logP"] = smiles_df["ROMol"].apply(Descriptors.MolLogP).round(2)
    smiles_df["MR"]   = smiles_df["ROMol"].apply(Descriptors.MolMR).round(2)
    smiles_df["AtX"]  = smiles_df["ROMol"].apply(Descriptors.HeavyAtomCount)
    smiles_df["HBLA"] = smiles_df["ROMol"].apply(rdMolDescriptors.CalcNumLipinskiHBA)
    smiles_df["HBLD"] = smiles_df["ROMol"].apply(rdMolDescriptors.CalcNumLipinskiHBD)
    smiles_df["RB"]   = smiles_df["ROMol"].apply(rdMolDescriptors.CalcNumRotatableBonds)
    smiles_df["PSA"]  = smiles_df["ROMol"].apply(rdMolDescriptors.CalcTPSA).round(2)

    return smiles_df

# Función para procesar los archivos de Toxiciad y de Síntesis
def reference_csv_data(name, prop_adme_file, results_text, dev_tox_file, mutagenicity_file, oral_rat_ld50_file, ambit_sa_file):
    global csv_processed
    global merged_data

    # Verifica si el campo "Original SMILE" está vacío
    if not name:
        messagebox.showerror("Error", "Disease name is a mandatory field")
        return  # Detiene la ejecución de la función si falta el nombre de la aplicación

    try:
        # Carga y procesamiento de los archivos CSV
        prop_ADME = load_and_process_smiles_for_RefSet(prop_adme_file)

        # Carga y procesamiento de los archivos CSV de toxicidad y SA usando helpers globales
        dev_tox = load_dev_tox_file(dev_tox_file, label_suffix=" (reference)")
        mutagenicity = load_mutagenicity_file(mutagenicity_file, label_suffix=" (reference)")
        oral_rat_ld50 = load_ld50_file(oral_rat_ld50_file, label_suffix=" (reference)")
        ambit_sa = load_ambit_sa_file(ambit_sa_file, label_suffix=" (reference)")

        # Seleccionar solo las columnas relevantes de prop_ADME
        prop_ADME = prop_ADME[['name','smile', 'MW', 'logP', 'MR', 'AtX', 'HBLA', 'HBLD', 'RB', 'PSA']]

        # Concatenar todos los DataFrames
        merged_data = pd.concat([prop_ADME, dev_tox, mutagenicity, oral_rat_ld50, ambit_sa], axis=1)

        # Identificar filas con valores faltantes
        rows_with_nan = merged_data[merged_data.isna().any(axis=1)]
        rows_with_nan = smiles_to_last(rows_with_nan)

        # DataFrame sin filas con valores faltantes
        cleaned_data = merged_data.dropna().copy()
        cleaned_data = smiles_to_last(cleaned_data)

        # Seleccionar solo las columnas numéricas para el cálculo de estadísticas
        numeric_cols = cleaned_data.select_dtypes(include=['float64', 'int64'])

        # Calcular estadísticos para cada columna
        mean_values = numeric_cols.mean().round(2)
        std_values = numeric_cols.std().round(2)
        min_values = numeric_cols.min().round(2)
        max_values = numeric_cols.max().round(2)
        median_values = numeric_cols.median().round(2)
        var_values = numeric_cols.var().round(2)
        skew_values = numeric_cols.skew().round(2)
        kurt_values = numeric_cols.kurt().round(2)


        # Combinar los resultados en un solo DataFrame
        summary_stats = pd.DataFrame({
            'Mean': mean_values,
            'StdDev': std_values,
            'Min': min_values,
            'Max': max_values,
            'Median': median_values,
            'Variance': var_values,
            'Skewness': skew_values, #Asimetria, Medida de la simetria de la distribucion de los datos
            'Kurtosis': kurt_values
        })

        # Compatibilidad con el código que usa la columna 'StdDev'
        if 'Standard Deviation' in summary_stats.columns:
            summary_stats.rename(columns={'Standard Deviation': 'StdDev'}, inplace=True)

        # Mostrar los resultados del DataFrame sin valores faltantes en la interfaz
        results_text.delete('1.0', tk.END)
        # Muestra los valores de summary_stats
        results_text.insert(tk.END, "\n\nSummary Statistics:\n")
        results_text.insert(tk.END, summary_stats.to_string())

        # Muestra la estadística de cada propiedad
        results_text.insert(tk.END, "Cleaned Data:\n")
        results_text.insert(tk.END, cleaned_data.to_string(index=False))
        
        # Mostrar el DataFrame las filas eliminadas
        results_text.insert(tk.END, "\n\nRows with at least one N/A:\n")
        results_text.insert(tk.END, rows_with_nan.to_string(index=False))

        # Obtener la ruta del archivo de smiles
        prop_csv_dir = os.path.dirname(prop_adme_file)

        # Guardar los archivos CSV con los resultados
        default_filename = f"{name}_RefSet.csv"
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 initialdir=prop_csv_dir,  # Utiliza el directorio donde esta el archivo de smiles
                                                 initialfile=default_filename,
                                                 filetypes=[("CSV files", "*.csv")])

        if save_path:
            cleaned_data.to_csv(save_path, index=False)
            summary_stats_path = os.path.join(os.path.dirname(save_path), f"{name}_SummaryStatistics.csv")
            summary_stats.to_csv(summary_stats_path, index=True)
            csv_processed = True  # Establece la variable como True después de procesar el archivo CSV

            # AQUI: crear/actualizar la enfermedad en valores_enfermedades

            try:
                # summary_stats tiene índices como 'MW', 'logP', 'MR', 'AtX', 'HBLA', 'HBLD', 'RB', 'PSA', 'LD50', 'M', 'DT', 'SA'
                mean = summary_stats['Mean']
                std = summary_stats['StdDev']

                nueva_enfermedad = {
                    'LD50_farmacos': float(mean['LD50']),
                    'StdDevSet_LD50': float(std['LD50']),
                    'M_farmacos': float(mean['M']),
                    'StdDevSet_M': float(std['M']),
                    'DT_farmacos': float(mean['DT']),
                    'StdDevSet_DT': float(std['DT']),
                    'SA_farmacos': float(mean['SA']),
                    'StdDevSet_SA': float(std['SA']),
                    'AverageRefSet_MW': float(mean['MW']),
                    'StdDevSet_MW': float(std['MW']),
                    'AverageRefSet_logP': float(mean['logP']),
                    'StdDevSet_logP': float(std['logP']),
                    'AverageRefSet_MR': float(mean['MR']),
                    'StdDevSet_MR': float(std['MR']),
                    'AverageRefSet_AtX': float(mean['AtX']),
                    'StdDevSet_AtX': float(std['AtX']),
                    'AverageRefSet_HBLA': float(mean['HBLA']),
                    'StdDevSet_HBLA': float(std['HBLA']),
                    'AverageRefSet_HBLD': float(mean['HBLD']),
                    'StdDevSet_HBLD': float(std['HBLD']),
                    'AverageRefSet_RB': float(mean['RB']),
                    'StdDevSet_RB': float(std['RB']),
                    'AverageRefSet_PSA': float(mean['PSA']),
                    'StdDevSet_PSA': float(std['PSA'])
                }

                # Añadir/actualizar en el diccionario global
                global valores_enfermedades, disease_files

                valores_enfermedades[name] = nueva_enfermedad
                save_valores_enfermedades()  # lo guarda en JSON

                # Guardar también el archivo RefSet asociado para la función "show_disease_info"
                disease_files[name] = save_path
                save_disease_files()

                messagebox.showinfo(
                    "Reference set created",
                    f"The disease '{name}' has been added to the disease list.\n"
                    f"It will now appear in 'Select Disease' inside 'SELECTION SCORES'."
                )

            except Exception as e_inner:
                messagebox.showerror("Error", f"Reference set created, but disease could not be registered:\n{e_inner}")
        

    except Exception as e:
        results_text.delete('1.0', tk.END)
        results_text.insert(tk.END, f"Error al procesar los datos: {e}")

# Interfaz create_reference_set
def create_reference_set_app():
    welcome_window.withdraw()  # Ocultar la ventana de bienvenida

    def on_close():
        reference_set.destroy()
        welcome_window.deiconify()  # Mostrar la ventana de bienvenida

    reference_set = tk.Toplevel()
    reference_set.title("Creating a new reference set")
    reference_set.protocol("WM_DELETE_WINDOW", on_close) 

    # Frames para las diferentes secciones
    frame_csv = ttk.Frame(reference_set)
    frame_results = ttk.Frame(reference_set)

    frame_csv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame_results.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Sección para cargar y procesar archivos SMILES
    name_var = tk.StringVar()
    tk.Label(frame_csv, text="Disease name").pack()
    tk.Entry(frame_csv, textvariable=name_var).pack(pady=(0, 20))

    # Sección para cargar archivos CSV
    csv_files = [tk.StringVar() for _ in range(5)]
    csv_labels = ["Smiles (Name, smile):", "Developmental_Toxicity:", "Mutagenicity:", "Oral_rat_LD50:", "Synthetic accessibility:"]

    def load_and_set_csv_var(var, check_label, path_label):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            # Guardar la ruta completa en var
            var.set(filename)
            #Mostrar solo un pedazo de la ruta en la interfaz
            path_label.config(text=shorten_path(filename, levels=2))
            # Muestra el símbolo "✔" si el archivo ha sido seleccionada
            check_label.config(text="✔")

    def load_and_set_smiles_file(var, check_label, path_label):
        # Acepta .smi, .smiles y .csv
        filename = filedialog.askopenfilename(
            filetypes=[
                ("SMILES files", "*.smi *.smiles"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            var.set(filename)
            path_label.config(text=shorten_path(filename, levels=2))
            check_label.config(text="✔")

    for i, label_text in enumerate(csv_labels):
        tk.Label(frame_csv, text=label_text).pack()
        csv_frame = ttk.Frame(frame_csv)
        csv_frame.pack(pady=(0, 15))

        check_label = tk.Label(csv_frame, text="", font=("Arial", 12))
        check_label.pack(side=tk.LEFT, padx=(0, 10))

        # Label que mostrará SOLO la ruta corta
        path_label = tk.Label(csv_frame, text="", anchor="w")
        # (lo empaquetamos después del botón, para que se vea a la derecha)

        # Para el primer archivo (índice 0) usamos la función especial de SMILES
        if i == 0:
            boton_cmd = lambda var=csv_files[i], c_label=check_label, p_label=path_label: \
                load_and_set_smiles_file(var, c_label, p_label)
            boton_texto = "Cargar SMILES"
        else:
            boton_cmd = lambda var=csv_files[i], c_label=check_label, p_label=path_label: \
                load_and_set_csv_var(var, c_label, p_label)
            boton_texto = "Cargar CSV"

        tk.Button(csv_frame, text=boton_texto, command=boton_cmd).pack(side=tk.LEFT)

        # Ahora mostramos SOLO la ruta acortada, NO el StringVar con la ruta completa
        path_label.pack(side=tk.LEFT, padx=(10, 0))


    # Sección de resultados
    results_text = scrolledtext.ScrolledText(frame_results, wrap='none', width=180, height=20)
    results_text.pack(fill=tk.BOTH, expand=True)

    # Agrega un espacio en blanco entre los botones CSV y el botón "Procesar Todos los Datos"
    tk.Label(frame_csv, text="").pack()

    # Botón para procesar todos los datos (debajo de los botones CSV)
    process_all_button = tk.Button(frame_csv, text="Process data ➡️",
                                   command=lambda: reference_csv_data(
                                       name_var.get(),
                                       csv_files[0].get(),
                                       results_text,
                                       csv_files[1].get(),
                                       csv_files[2].get(),
                                       csv_files[3].get(),
                                       csv_files[4].get()
                                   ))
    process_all_button.pack()

    center_window(reference_set, 1500, 500)

    reference_set.mainloop()

#-------------------------------------------------------------------------------------------------------------------------------------------
# Section to calculate SELECTION SCORES 
#-------------------------------------------------------------------------------------------------------------------------------------------

# Función para cargar y procesar SMILES de derivados
def load_and_process_smiles(filename, results_text, name, acronimo, smile_original):
    # Verifica si los campos "Name" y "Acronym" están vacíos
    if not name or not acronimo:
        messagebox.showerror("Error", "Name and Acronym are mandatory fields")
        return None

    if not filename:
        messagebox.showerror("Error", "No SMILES file selected")
        return None

    # 1) Reutilizar el lector robusto del refset
    df = load_and_process_smiles_for_RefSet(filename)
    if df is None:
        messagebox.showerror("Error", "Could not process SMILES file for selection scores.")
        return None

    # Asegurarnos de que exista la columna 'smile'
    if "smile" not in df.columns:
        messagebox.showerror("Error", "Processed SMILES file does not contain a 'smile' column.")
        return None

    # 2) Si por alguna razón aún queda algún ROMol = None, lo filtramos
    if "ROMol" in df.columns:
        df = df[df["ROMol"].notna()]

    if df.empty:
        messagebox.showerror("Error", "No valid molecules found in the SMILES file.")
        return None

    # 3) Generar etiquetas de compuesto: ACR, ACR-1, ACR-2, ...
    i = 0

    def get_etiqueta(smile):
        nonlocal i
        if smile_original and smile == smile_original:
            return f"{acronimo}"
        i += 1
        return f"{acronimo}-{i}"

    df["Compound"] = df["smile"].astype(str).apply(get_etiqueta)

    # 4) Asegurarnos de que tenemos las propiedades ADME necesarias.
    #    Si load_and_process_smiles_for_RefSet ya las calculó, solo las usamos.
    #    Si falta alguna y tenemos ROMol, la calculamos.
    required_props = ["MW", "logP", "MR", "AtX", "HBLA", "HBLD", "RB", "PSA"]

    if "ROMol" in df.columns:
        # Calcular las que falten
        for prop in required_props:
            if prop not in df.columns:
                if prop == "MW":
                    df["MW"] = df["ROMol"].apply(Descriptors.MolWt).round(2)
                elif prop == "logP":
                    df["logP"] = df["ROMol"].apply(Descriptors.MolLogP).round(2)
                elif prop == "MR":
                    df["MR"] = df["ROMol"].apply(Descriptors.MolMR).round(2)
                elif prop == "AtX":
                    df["AtX"] = df["ROMol"].apply(Descriptors.HeavyAtomCount)
                elif prop == "HBLA":
                    df["HBLA"] = df["ROMol"].apply(rdMolDescriptors.CalcNumLipinskiHBA)
                elif prop == "HBLD":
                    df["HBLD"] = df["ROMol"].apply(rdMolDescriptors.CalcNumLipinskiHBD)
                elif prop == "RB":
                    df["RB"] = df["ROMol"].apply(rdMolDescriptors.CalcNumRotatableBonds)
                elif prop == "PSA":
                    df["PSA"] = df["ROMol"].apply(rdMolDescriptors.CalcTPSA).round(2)

        # Si ya no quieres ver ROMol en la tabla final:
        df = df.drop(columns=["ROMol"], errors="ignore")

    # 5) Reordenar columnas para mostrar algo limpio
    ordered_cols = ["Compound", "smile"]
    for c in required_props:
        if c in df.columns:
            ordered_cols.append(c)

    # Añadir cualquier otra columna que haya quedado (por ejemplo 'name') al final
    other_cols = [c for c in df.columns if c not in ordered_cols]
    df = df[ordered_cols + other_cols]

    # 6) Mostrar en la ventana de resultados
    results_text.delete("1.0", tk.END)
    results_text.insert(tk.END, df.to_string(index=False))

    return df   

# Función para procesar los datos de los archivos CSV
def process_csv_data(name, acronimo, results_text, prop_adme_file, dev_tox_file, mutagenicity_file, oral_rat_ld50_file, ambit_sa_file, smile_original_var):
    global csv_processed
    global cleaned_data
    global valores_enfermedades
    global disease_var

    # Verifica si los campos "Name" y "Acronym" están vacíos
    if not name or not acronimo:
        messagebox.showerror("Error", "Name and Acronym are mandatory fields")
        return

    try:
        actualizar_rangos()
        enfermedad = disease_var.get()
        valores = valores_enfermedades[enfermedad]

        # Recalcular dinámicamente cuántas propiedades ADME cumple el RefSet con los rangos CADMA-Chem actuales
        suma_adme_calc = calcular_suma_adme_enfermedad(enfermedad)
        # Actualizar también la GUI para que el usuario vea el valor correcto
        suma_adme_disease_var.set(str(suma_adme_calc))

        # Evaluar los rangos de cada propiedad
        def en_rango(valor, propiedad):
            if propiedad in rangos:
                return 1 if rangos[propiedad][0] <= valor <= rangos[propiedad][1] else 0
            else:
                raise ValueError(f'La propiedad {propiedad} no tiene un rango definido.')

        # Carga y procesamiento de los archivos CSV
        prop_ADME = load_and_process_smiles(prop_adme_file, results_text, name, acronimo, smile_original_var.get() if smile_original_var else None)
        if prop_ADME is None or not all(col in prop_ADME.columns for col in rangos.keys()):
            raise ValueError('El archivo ADME no contiene todas las columnas necesarias.')

        # Developmental Toxicity, Mutagenicity, LD50 y SA usando los mismos helpers
        dev_tox = load_dev_tox_file(dev_tox_file, label_suffix=" (selection)")
        mutagenicity = load_mutagenicity_file(mutagenicity_file, label_suffix=" (selection)")
        oral_rat_ld50 = load_ld50_file(oral_rat_ld50_file, label_suffix=" (selection)")
        ambit_sa = load_ambit_sa_file(ambit_sa_file, label_suffix=" (selection)")

        # Concatenar todos los DataFrames
        merged_data = pd.concat([prop_ADME, dev_tox, mutagenicity, oral_rat_ld50, ambit_sa], axis=1)

        # Identificar filas con valores faltantes
        rows_with_nan = merged_data[merged_data.isna().any(axis=1)].copy()
        rows_with_nan = smiles_to_last(rows_with_nan)

        # DataFrame sin filas con valores faltantes
        print("Size before dropna")
        print("merged_data.shape =", merged_data.shape)
        print(merged_data.isna().sum())
        cleaned_data = merged_data.dropna().copy()
        print("Size after dropna")
        print("cleaned_data.shape =", cleaned_data.shape)
        print(cleaned_data.isna().sum())  

        # Seleccionar solo las columnas numéricas para el cálculo de estadísticas
        numeric_cols = cleaned_data.select_dtypes(include=['float64', 'int64'])

        # Calcular estadísticos para cada columna
        mean_values = numeric_cols.mean().round(2)
        std_values = numeric_cols.std().round(2)
        min_values = numeric_cols.min().round(2)
        max_values = numeric_cols.max().round(2)
        median_values = numeric_cols.median().round(2)
        var_values = numeric_cols.var().round(2)
        skew_values = numeric_cols.skew().round(2)
        kurt_values = numeric_cols.kurt().round(2)

        # Combinar los resultados en un solo DataFrame
        summary_stats = pd.DataFrame({
            'Mean': mean_values,
            'StdDev': std_values,
            'Min': min_values,
            'Max': max_values,
            'Median': median_values,
            'Variance': var_values,    #Valores altos indican mayor dispersión
            'Skewness': skew_values,  #Valores positivos indican asimetría hacia la derecha, valores negativos indican asimetría hacia la izquierda
            'Kurtosis': kurt_values    #Valores altos indican colas más pesadas, valores bajos indican colas más ligeras
        })

        # Aplicar la función 'en_rango' para cada propiedad y agregar nuevas columnas
        for propiedad in rangos.keys():
            cleaned_data[f'ADME_{propiedad}'] = cleaned_data.apply(lambda row: en_rango(row[propiedad], propiedad), axis=1)

        columnas_adme = [f'ADME_{propiedad}' for propiedad in rangos.keys()]

        # --------- PARÁMETROS DESDE LA GUI (PROMEDIOS / STDDEV) ---------
        farmacos_ld50_avg = float(ld50_farmacos_var.get())
        farmacos_ld50_std = float(stddev_ld50_var.get())

        farmacos_m_avg = float(m_farmacos_var.get())
        farmacos_m_std = float(stddev_m_var.get())

        farmacos_dt_avg = float(dt_farmacos_var.get())
        farmacos_dt_std = float(stddev_dt_var.get())

        farmacos_sa_avg = float(sa_farmacos_var.get())
        farmacos_sa_std = float(stddev_sa_var.get())

        farmacos_mw_avg    = float(avg_mw_var.get())
        farmacos_mw_std    = float(stddev_mw_var.get())
        farmacos_logp_avg  = float(avg_logp_var.get())
        farmacos_logp_std  = float(stddev_logp_var.get())
        farmacos_mr_avg    = float(avg_mr_var.get())
        farmacos_mr_std    = float(stddev_mr_var.get())
        farmacos_atx_avg   = float(avg_atx_var.get())
        farmacos_atx_std   = float(stddev_atx_var.get())
        farmacos_hbla_avg  = float(avg_hbla_var.get())
        farmacos_hbla_std  = float(stddev_hbla_var.get())
        farmacos_hbld_avg  = float(avg_hbld_var.get())
        farmacos_hbld_std  = float(stddev_hbld_var.get())
        farmacos_rb_avg    = float(avg_rb_var.get())
        farmacos_rb_std    = float(stddev_rb_var.get())
        farmacos_psa_avg   = float(avg_psa_var.get())
        farmacos_psa_std   = float(stddev_psa_var.get())

        suma_adme_ref = float(suma_adme_disease_var.get())
        # ---------------------------------------------------------------

        # Scores toxicológicos y de síntesis (usando GUI)
        cleaned_data['S_LD50'] = 1 + np.log10((1 + cleaned_data['LD50']) / (1 + farmacos_ld50_avg))
        cleaned_data['S_M']    = 1 - np.log10((1 + cleaned_data['M'])   / (1 + farmacos_m_avg))
        cleaned_data['S_DT']   = 1 - np.log10((1 + cleaned_data['DT'])  / (1 + farmacos_dt_avg))

        cleaned_data['S_T']  = (cleaned_data['S_LD50'] + cleaned_data['S_M'] + cleaned_data['S_DT']) / 3.0

        cleaned_data['S_SA'] = (cleaned_data['SA'] / farmacos_sa_avg)

        linea_acronimo = cleaned_data[cleaned_data['Compound'] == acronimo]

        print(linea_acronimo)

        cleaned_data['S_ADME'] = cleaned_data[columnas_adme].sum(axis=1) / float(suma_adme_calc)

        cleaned_data['S_ADMET'] = cleaned_data['S_ADME'] + cleaned_data['S_T']

        # Columnas necesarias para graficar el S^S por partes
        cleaned_data['S_ADMEPesada'] = cleaned_data['S_ADME'] * 0.4
        cleaned_data['S_TPesada']    = cleaned_data['S_T']    * 0.4
        cleaned_data['S_SAPesada']   = cleaned_data['S_SA']   * 0.2

        cleaned_data['S_LD50Pesada'] = (cleaned_data['S_LD50'] / 3.0) * 0.4
        cleaned_data['S_MPesada']    = (cleaned_data['S_M']    / 3.0) * 0.4
        cleaned_data['S_DTPesada']   = (cleaned_data['S_DT']   / 3.0) * 0.4

        # Propiedades fisicoquímicas: comparar contra intervalo CADMA + ventana µ ± 2σ
        '''cleaned_data['MW_violation'] = (
            (cleaned_data['MW'] < max(rangos['MW'][0],   farmacos_mw_avg   - 2 * farmacos_mw_std)) |
            (cleaned_data['MW'] > min(rangos['MW'][1],   farmacos_mw_avg   + 2 * farmacos_mw_std))
        ).astype(int)

        cleaned_data['logP_violation'] = (
            (cleaned_data['logP'] < max(rangos['logP'][0], farmacos_logp_avg - 2 * farmacos_logp_std)) |
            (cleaned_data['logP'] > min(rangos['logP'][1], farmacos_logp_avg + 2 * farmacos_logp_std))
        ).astype(int)

        cleaned_data['MR_violation'] = (
            (cleaned_data['MR'] < max(rangos['MR'][0],   farmacos_mr_avg   - 2 * farmacos_mr_std)) |
            (cleaned_data['MR'] > min(rangos['MR'][1],   farmacos_mr_avg   + 2 * farmacos_mr_std))
        ).astype(int)

        cleaned_data['AtX_violation'] = (
            (cleaned_data['AtX'] < max(rangos['AtX'][0], farmacos_atx_avg  - 2 * farmacos_atx_std)) |
            (cleaned_data['AtX'] > min(rangos['AtX'][1], farmacos_atx_avg  + 2 * farmacos_atx_std))
        ).astype(int)

        cleaned_data['HBLA_violation'] = (
            (cleaned_data['HBLA'] < max(rangos['HBLA'][0], farmacos_hbla_avg - 2 * farmacos_hbla_std)) |
            (cleaned_data['HBLA'] > min(rangos['HBLA'][1], farmacos_hbla_avg + 2 * farmacos_hbla_std))
        ).astype(int)

        cleaned_data['HBLD_violation'] = (
            (cleaned_data['HBLD'] < max(rangos['HBLD'][0], farmacos_hbld_avg - 2 * farmacos_hbld_std)) |
            (cleaned_data['HBLD'] > min(rangos['HBLD'][1], farmacos_hbld_avg + 2 * farmacos_hbld_std))
        ).astype(int)

        cleaned_data['RB_violation'] = (
            (cleaned_data['RB'] < max(rangos['RB'][0],   farmacos_rb_avg   - 2 * farmacos_rb_std)) |
            (cleaned_data['RB'] > min(rangos['RB'][1],   farmacos_rb_avg   + 2 * farmacos_rb_std))
        ).astype(int)

        cleaned_data['PSA_violation'] = (
            (cleaned_data['PSA'] < max(rangos['PSA'][0], farmacos_psa_avg  - 2 * farmacos_psa_std)) |
            (cleaned_data['PSA'] > min(rangos['PSA'][1], farmacos_psa_avg  + 2 * farmacos_psa_std))
        ).astype(int)

        # Toxicidad / síntesis: doble violación (GUI)
        cleaned_data['LD50_violation'] = np.where(
            cleaned_data['LD50'] < (farmacos_ld50_avg - farmacos_ld50_std), 2,
            np.where(cleaned_data['LD50'] < farmacos_ld50_avg, 1, 0)
        ).astype(int)

        cleaned_data['M_violation'] = np.where(
            cleaned_data['M'] > (farmacos_m_avg + farmacos_m_std), 2,
            np.where(cleaned_data['M'] > farmacos_m_avg, 1, 0)
        ).astype(int)

        cleaned_data['DT_violation'] = np.where(
            cleaned_data['DT'] > (farmacos_dt_avg + farmacos_dt_std), 2,
            np.where(cleaned_data['DT'] > farmacos_dt_avg, 1, 0)
        ).astype(int)

        cleaned_data['SA_violation'] = np.where(
            cleaned_data['SA'] < (farmacos_sa_avg - farmacos_sa_std), 2,
            np.where(cleaned_data['SA'] < farmacos_sa_avg, 1, 0)
        ).astype(int)

        # Número total de violaciones
        cleaned_data['Num_violations'] = cleaned_data[
            ['MW_violation', 'logP_violation', 'MR_violation', 'AtX_violation','HBLA_violation', 'HBLD_violation', 'RB_violation', 'PSA_violation','LD50_violation', 'M_violation', 'DT_violation', 'SA_violation']
            ].sum(axis=1)'''

        # Cálculo del score de selección completo
        cleaned_data['S_S'] = (cleaned_data['S_ADMEPesada'] + cleaned_data['S_TPesada'] + cleaned_data['S_SAPesada']).round(3)
        cleaned_data = cleaned_data.sort_values(by='S_S', ascending=False)
        cleaned_data = smiles_to_last(cleaned_data)

        # Mostrar los resultados en la interfaz de usuario
        results_text.delete('1.0', tk.END)

        # Muestra los valores de summary_stats
        results_text.insert(tk.END, "\nSummary Statistics:\n")
        results_text.insert(tk.END, summary_stats.to_string())

        # Muestra los valores de cleaned data
        results_text.insert(tk.END, "\n\nCleaned Data:\n")
        results_text.insert(tk.END, cleaned_data.to_string(index=False))

        # Mostrar el DataFrame las filas eliminadas
        results_text.insert(tk.END, "\n\nRows with at least one N/A:\n")
        results_text.insert(tk.END, rows_with_nan.to_string(index=False))

        # Obtener la ruta del archivo "name"_prop.csv
        prop_csv_dir = os.path.dirname(prop_adme_file)

        # Guardar el archivo "name"_SS.csv con los resultados
        default_filename = f"{name}_SS.csv"
        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 initialdir=prop_csv_dir,  # Utiliza el directorio de "name"_prop.csv
                                                 initialfile=default_filename,
                                                 filetypes=[("CSV files", "*.csv")])
        if save_path:
            cleaned_data.to_csv(save_path, index=False)
            summary_stats_path = os.path.join(os.path.dirname(save_path), f"{name}_SS_SummaryStatistics.csv")
            summary_stats.to_csv(summary_stats_path, index=True)
            csv_processed = True  # Establece la variable como True después de procesar el archivo CSV

    except Exception as e:
        results_text.delete('1.0', tk.END)
        results_text.insert(tk.END, f"Error al procesar los datos: {e}")

# Interfaz start_main
def start_main_app():
    global disease_var
    welcome_window.withdraw()

    def on_close():
        root.destroy()
        welcome_window.deiconify()

    root = tk.Toplevel()
    root.title("Data Analysis Tool")
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Frames para las diferentes secciones
    frame_smiles = ttk.Frame(root)
    frame_csv = ttk.Frame(root)
    frame_results = ttk.Frame(root)
    frame_smiles.grid(row=0, column=0, sticky='nsew')
    frame_csv.grid(row=0, column=1, sticky='nsew')
    frame_results.grid(row=0, column=2, sticky='nsew')

    # Configurar la expansión de las columnas
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)
    root.grid_columnconfigure(2, weight=2)
    root.grid_rowconfigure(0, weight=1)

    # Sección para cargar y procesar archivos SMILES
    name_var = tk.StringVar()
    global acronimo_var  # Añadido
    acronimo_var = tk.StringVar()  # Añadido
    smile_original_var = tk.StringVar()
    tk.Label(frame_smiles, text="Name of the project molecule").pack()
    tk.Entry(frame_smiles, textvariable=name_var).pack()
    tk.Label(frame_smiles, text="Acronym to make derivatives").pack()
    tk.Entry(frame_smiles, textvariable=acronimo_var).pack()
    tk.Label(frame_smiles, text="SMILES to make comparisons").pack()
    tk.Entry(frame_smiles, textvariable=smile_original_var).pack()

    global ld50_farmacos_var, m_farmacos_var, dt_farmacos_var, sa_farmacos_var, suma_adme_disease_var, stddev_ld50_var, stddev_m_var, stddev_dt_var
    global stddev_sa_var, avg_mw_var, stddev_mw_var, avg_logp_var, stddev_logp_var, avg_mr_var, stddev_mr_var, avg_atx_var, stddev_atx_var, avg_hbla_var
    global stddev_hbla_var, avg_hbld_var, stddev_hbld_var, avg_rb_var, stddev_rb_var, avg_psa_var, stddev_psa_var
    ld50_farmacos_var = tk.StringVar()
    stddev_ld50_var = tk.StringVar()
    m_farmacos_var = tk.StringVar()
    stddev_m_var = tk.StringVar()
    dt_farmacos_var = tk.StringVar()
    stddev_dt_var = tk.StringVar()
    sa_farmacos_var = tk.StringVar()
    stddev_sa_var = tk.StringVar()
    avg_mw_var = tk.StringVar()
    stddev_mw_var = tk.StringVar()
    avg_logp_var = tk.StringVar()
    stddev_logp_var = tk.StringVar()
    avg_mr_var = tk.StringVar()
    stddev_mr_var = tk.StringVar()
    avg_atx_var = tk.StringVar()
    stddev_atx_var = tk.StringVar()
    avg_hbla_var = tk.StringVar()
    stddev_hbla_var = tk.StringVar()
    avg_hbld_var = tk.StringVar()
    stddev_hbld_var = tk.StringVar()
    avg_rb_var = tk.StringVar()
    stddev_rb_var = tk.StringVar()
    avg_psa_var = tk.StringVar()
    stddev_psa_var = tk.StringVar()
    suma_adme_disease_var = tk.StringVar()

    # Función para actualizar los campos según la enfermedad seleccionada
    def actualizar_campos(*args):
        enfermedad = disease_var.get()
        valores = valores_enfermedades[enfermedad]
        ld50_farmacos_var.set(valores['LD50_farmacos'])
        stddev_ld50_var.set(valores['StdDevSet_LD50'])
        m_farmacos_var.set(valores['M_farmacos'])
        stddev_m_var.set(valores['StdDevSet_M'])
        dt_farmacos_var.set(valores['DT_farmacos'])
        stddev_dt_var.set(valores['StdDevSet_DT'])
        sa_farmacos_var.set(valores['SA_farmacos'])
        stddev_sa_var.set(valores['StdDevSet_SA'])
        avg_mw_var.set(valores['AverageRefSet_MW'])
        stddev_mw_var.set(valores['StdDevSet_MW'])
        avg_logp_var.set(valores['AverageRefSet_logP'])
        stddev_logp_var.set(valores['StdDevSet_logP'])
        avg_mr_var.set(valores['AverageRefSet_MR'])
        stddev_mr_var.set(valores['StdDevSet_MR'])
        avg_atx_var.set(valores['AverageRefSet_AtX'])
        stddev_atx_var.set(valores['StdDevSet_AtX'])
        avg_hbla_var.set(valores['AverageRefSet_HBLA'])
        stddev_hbla_var.set(valores['StdDevSet_HBLA'])
        avg_hbld_var.set(valores['AverageRefSet_HBLD'])
        stddev_hbld_var.set(valores['StdDevSet_HBLD'])
        avg_rb_var.set(valores['AverageRefSet_RB'])
        stddev_rb_var.set(valores['StdDevSet_RB'])
        avg_psa_var.set(valores['AverageRefSet_PSA'])
        stddev_psa_var.set(valores['StdDevSet_PSA'])

        try:
            # Asegurarnos de que los rangos estén actualizados desde la GUI
            actualizar_rangos()
        except Exception as e:
            print(f"Error al actualizar rangos desde GUI en actualizar_campos: {e}")

        suma_adme_calc = calcular_suma_adme_enfermedad(enfermedad)
        suma_adme_disease_var.set(str(suma_adme_calc))


    # Function to display disease information in a new window
    def show_disease_info():
        enfermedad = disease_var.get()
        csv_file = disease_files.get(enfermedad, None)

        if csv_file is None:
            messagebox.showerror("Error", "No CSV file found for the selected disease.")
            return

        try:
            data_frame = pd.read_csv(csv_file)

            # Calculate statistics for numeric columns
            numeric_cols = data_frame.select_dtypes(include=['float64', 'int64'])

            mean_values = numeric_cols.mean().round(2)
            std_values = numeric_cols.std().round(2)
            min_values = numeric_cols.min().round()
            max_values = numeric_cols.max().round()
            median_values = numeric_cols.median().round(2)
            var_values = numeric_cols.var().round(2)
            skew_values = numeric_cols.skew().round(2)
            kurt_values = numeric_cols.kurt().round(2)

            # Get the number of compounds
            number_compounds = len(data_frame)

            summary_stats = pd.DataFrame({
                'Mean': mean_values,
                'StdDev': std_values,
                'Min': min_values,
                'Max': max_values,
                'Median': median_values,
                'Var': var_values,
                'Skewness': skew_values,
                'Kurtosis': kurt_values
            })

            # Sort the DataFrame by the "Name" column
            if 'Name' in data_frame.columns:
                data_frame = data_frame.sort_values(by='Name')
            elif 'name' in data_frame.columns:
                data_frame = data_frame.sort_values(by='name')
            elif 'NAME' in data_frame.columns:
                data_frame = data_frame.sort_values(by='NAME')

            # Create a new window to display the information
            info_window = tk.Toplevel(root)
            info_window.title(f"Information for {enfermedad}")

            # Create a frame to hold the stats and logo
            stats_frame = tk.Frame(info_window)
            stats_frame.grid(row=0, column=0, sticky='nsew')
            
            # Create a scrollable text widget to display the statistics
            stats_area = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD, width=90, height=21)
            stats_area.grid(row=0, column=0, sticky='nsew')
            stats_area.insert(tk.END, "\n\nSummary Statistics:\n\n")
            stats_area.insert(tk.END, summary_stats.to_string(index=True))
            stats_area.insert(tk.END, f"\n\nNumber of compounds in the reference set: {number_compounds}")

            # Create a text widget to display the ASCII logo
            logo_area = tk.Text(stats_frame, wrap=tk.WORD, width=90, height=21)
            logo_area.grid(row=0, column=1, sticky='nsew')
            logo_area.insert(tk.END, """
                             ..,co88oc.oo8888cc,..
  o8o.               ..,o8889689ooo888o"88888888oooc..
.88888             .o888896888".88888888o'?888888888889ooo....
a888P          ..c6888969""..,"o888888888o.?8888888888"".ooo8888oo.
088P        ..atc88889"".,oo8o.86888888888o 88988889",o888888888888.
888t  ...coo688889"'.ooo88o88b.'86988988889 8688888'o8888896989^888o
 888888888888"..ooo888968888888  "9o688888' "888988 8888868888'o88888
  ""G8889""'ooo888888888888889 .d8o9889""'   "8688o."88888988"o888888o .
           o8888''''''''""""''   o8688             """"88868. 888888.68988888"o8o.
          '88888o.            "8888ooo.           8888. 88888.8898888o"888o.
           "888888'              ""888888'          '""8o 8888.8869888oo8888o .
    "". :.:::::::::::.: .     . :.::::::::.: .   . : ::.:."8888 "888888888888o
                                                        :..8888,. "88888888888.
   ___ _____  _         _   _   _    __  __ ___        .:o888.o8o.  "866o9888o
  / _ \_   _|/ \       | | | | / \  |  \/  |_ _|        :888.o8888.  "88."89".
 | | | || | / _ \ _____| | | |/ _ \ | |\/| || |        . 89  888888    "88":.
 | |_| || |/ ___ \_____| |_| / ___ \| |  | || |        :.     '8888o
  \__\_\|_/_/   \_\     \___/_/   \_\_|  |_|___|        .       "8888..
                                                                   "888889,
                                                            . : :.:::::::.: :.'""")

            logo_area.configure(state='disabled')  # Make the text read-only

            # Create a scrollable text widget to display the DataFrame
            text_area = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, width=180, height=40)
            text_area.grid(row=1, column=0, sticky='nsew')
            text_area.insert(tk.END, "Detailed Data:\n")
            text_area.insert(tk.END, data_frame.to_string(index=False))

            # Configure row and column weights for resizing behavior
            info_window.grid_rowconfigure(0, weight=0)  # Fixed height for stats_area
            info_window.grid_rowconfigure(1, weight=1)  # Expand text_area
            info_window.grid_columnconfigure(0, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading the CSV file: {e}")

    # Crear la variable tk.StringVar para el menú desplegable y agregar el menú
    disease_var = tk.StringVar(value='Neurodegenerativas 🧠')  # Valor por defecto
    disease_var.trace_add('write', actualizar_campos)  # Llamar a la función cuando el valor cambie

    tk.Label(frame_smiles, text="Select Disease", font=("Arial", 16)).pack(pady=(20, 0))

    # Crear un Frame para el botón y el OptionMenu
    select_disease_frame = ttk.Frame(frame_smiles)
    select_disease_frame.pack()

    # Agregar el botón al Frame
    tk.Button(select_disease_frame, text="👁️📝", command=show_disease_info).pack(side=tk.LEFT, padx=5)

    # Agregar el OptionMenu al Frame
    tk.OptionMenu(select_disease_frame, disease_var, *valores_enfermedades.keys()).pack(side=tk.LEFT)

    # Frame para todos los campos
    all_fields_frame = ttk.Frame(frame_smiles)
    all_fields_frame.pack(fill=tk.X, padx=5, pady=5, anchor='center')

    tk.Label(all_fields_frame, text="The following values will be used for the exclusion counter:", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, sticky='w')
    
    # Configurar encabezado de la tabla
    tk.Label(all_fields_frame, text="Property", font=("Arial", 14, "bold")).grid(row=1, column=0, sticky='w', padx=(10, 10))
    tk.Label(all_fields_frame, text="Average", font=("Arial", 14, "bold")).grid(row=1, column=1, sticky='w', padx=(10, 10))
    tk.Label(all_fields_frame, text="StdDev", font=("Arial", 14, "bold")).grid(row=1, column=2, sticky='w', padx=(10, 10))

    # LD50_farmacos
    tk.Label(all_fields_frame, text="LD50", font=("Arial", 12)).grid(row=2, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=ld50_farmacos_var, width=8).grid(row=2, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_ld50_var, width=8).grid(row=2, column=2, padx=(10, 10))

    # M_farmacos
    tk.Label(all_fields_frame, text="M", font=("Arial", 12)).grid(row=3, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=m_farmacos_var, width=8).grid(row=3, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_m_var, width=8).grid(row=3, column=2, padx=(10, 10))

    # DT_farmacos
    tk.Label(all_fields_frame, text="DT", font=("Arial", 12)).grid(row=4, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=dt_farmacos_var, width=8).grid(row=4, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_dt_var, width=8).grid(row=4, column=2, padx=(10, 10))

    # SA_farmacos
    tk.Label(all_fields_frame, text="SA", font=("Arial", 12)).grid(row=5, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=sa_farmacos_var, width=8).grid(row=5, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_sa_var, width=8).grid(row=5, column=2, padx=(10, 10))


    # Separador
    ttk.Separator(all_fields_frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky='ew', pady=(10, 10))

    # Average MW y StdDev MW
    tk.Label(all_fields_frame, text="MW", font=("Arial", 12)).grid(row=7, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_mw_var, width=8).grid(row=7, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_mw_var, width=8).grid(row=7, column=2, padx=(10, 10))

    # Average logP y StdDev logP
    tk.Label(all_fields_frame, text="logP", font=("Arial", 12)).grid(row=8, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_logp_var, width=8).grid(row=8, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_logp_var, width=8).grid(row=8, column=2, padx=(10, 10))

    # Average MR y StdDev MR
    tk.Label(all_fields_frame, text="MR", font=("Arial", 12)).grid(row=9, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_mr_var, width=8).grid(row=9, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_mr_var, width=8).grid(row=9, column=2, padx=(10, 10))

    # Average AtX y StdDev AtX
    tk.Label(all_fields_frame, text="AtX", font=("Arial", 12)).grid(row=10, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_atx_var, width=8).grid(row=10, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_atx_var, width=8).grid(row=10, column=2, padx=(10, 10))

    # Average HBLA y StdDev HBLA
    tk.Label(all_fields_frame, text="HBLA", font=("Arial", 12)).grid(row=11, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_hbla_var, width=8).grid(row=11, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_hbla_var, width=8).grid(row=11, column=2, padx=(10, 10))

    # Average HBLD y StdDev HBLD
    tk.Label(all_fields_frame, text="HBLD", font=("Arial", 12)).grid(row=12, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_hbld_var, width=8).grid(row=12, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_hbld_var, width=8).grid(row=12, column=2, padx=(10, 10))

    # Average RB y StdDev RB
    tk.Label(all_fields_frame, text="RB", font=("Arial", 12)).grid(row=13, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_rb_var, width=8).grid(row=13, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_rb_var, width=8).grid(row=13, column=2, padx=(10, 10))

    # Average PSA y StdDev PSA
    tk.Label(all_fields_frame, text="PSA", font=("Arial", 12)).grid(row=14, column=0, sticky='w', padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=avg_psa_var, width=8).grid(row=14, column=1, padx=(10, 10))
    tk.Entry(all_fields_frame, textvariable=stddev_psa_var, width=8).grid(row=14, column=2, padx=(10, 10))

    # Separador
    ttk.Separator(all_fields_frame, orient='horizontal').grid(row=15, column=0, columnspan=3, sticky='ew', pady=(10, 10))

    # suma_adme_enfermedad
    tk.Label(all_fields_frame, text="# ADME props met by RefSet ✅: ").grid(row=16, column=0,columnspan=2, sticky='w')
    tk.Entry(all_fields_frame, textvariable=suma_adme_disease_var, width=3).grid(row=16, column=2, sticky='w')

    # Separador
    ttk.Separator(all_fields_frame, orient='horizontal').grid(row=17, column=0, columnspan=3, sticky='ew', pady=(10, 10))

    # Inicializar los campos con los valores por defecto
    actualizar_campos()

    # Sección para cargar archivos CSV
    csv_files = [tk.StringVar() for _ in range(5)]
    csv_labels = ["Smiles file:", "Desarrollo de Toxicidad:", "Mutagenicidad:", "Dosis Letal en Ratas LD50:", "AMBIT-SA:"]
    extensions = ["smi", "csv", "csv", "csv", "csv"]

    def load_and_set_file(var, check_label, file_type):
        filetypes = {
            "csv": [("csv files", "*.csv")],
            "txt": [("txt files", "*.txt")],
            "smi": [("smi files", "*.smi")],
            "xlsx": [("xlsx files", "*.xlsx")],
            "all": [("All files", "*.*")]
        }

        filetypes = filetypes.get(file_type, [("All files", "*.*")])

        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)
            check_label.config(text="✔")

    for i, label_text in enumerate(csv_labels):
        tk.Label(frame_csv, text=label_text).pack()
        csv_frame = ttk.Frame(frame_csv)
        csv_frame.pack()
        check_label = tk.Label(csv_frame, text="", font=("Arial", 12))
        check_label.pack(side=tk.LEFT)
        load_button_text = f"Load '.{extensions[i]}' file"
        tk.Button(csv_frame, text=load_button_text, command=lambda var=csv_files[i], label=check_label, ext=extensions[i]: load_and_set_file(var, label, ext)).pack(side=tk.LEFT)
        tk.Label(csv_frame, textvariable=csv_labels[i]).pack(side=tk.LEFT)
        check_label.pack(side=tk.LEFT)

    # Sección de resultados
    results_text = scrolledtext.ScrolledText(frame_results, wrap='none', width=130, height=40)
    results_text.pack(fill=tk.BOTH, expand=True)

    process_all_button = tk.Button(frame_csv, text="CALCULATE SCORES ➡️",
                                   command=lambda: process_csv_data(
                                       name_var.get(),
                                       acronimo_var.get(),
                                       results_text,
                                       csv_files[0].get(),
                                       csv_files[1].get(),
                                       csv_files[2].get(),
                                       csv_files[3].get(),
                                       csv_files[4].get(),
                                       smile_original_var
                                   ))
    process_all_button.pack(pady=20)


    # Frame para mostrar todos los rangos:
    all_fields_intervals_frame = ttk.Frame(frame_csv)
    all_fields_intervals_frame.pack(fill=tk.X, padx=5, pady=10)

    tk.Label(all_fields_intervals_frame, text="CADME-Chem intervals: ").grid(row=0, column=0, columnspan=3, sticky='w')
    tk.Label(all_fields_intervals_frame, text="Property   ").grid(row=1, column=0, sticky='w')
    tk.Label(all_fields_intervals_frame, text="Min        ").grid(row=1, column=1, sticky='w')
    tk.Label(all_fields_intervals_frame, text="Max        ").grid(row=1, column=2, sticky='w')

    # Variables para los rangos (hacerlas globales)
    global rangos_vars
    rangos_vars = {prop: (tk.StringVar(value=str(min_val)), tk.StringVar(value=str(max_val))) for prop, (min_val, max_val) in rangos.items()}

    # Añadir los campos de rango a la interfaz
    row = 2
    for prop, (min_var, max_var) in rangos_vars.items():
        tk.Label(all_fields_intervals_frame, text=prop).grid(row=row, column=0, sticky='w')
        tk.Entry(all_fields_intervals_frame, textvariable=min_var, width=5).grid(row=row, column=1)
        tk.Entry(all_fields_intervals_frame, textvariable=max_var, width=5).grid(row=row, column=2)
        row += 1


    # Función para graficar datos
    def open_graph_window():
        """
        Handler del botón 'PLOT RESULTS'.
        Asegura que cleaned_data esté cargado y luego abre un diálogo para seleccionar la variable (columna Y).
        """
        global cleaned_data

        def asegurar_cleaned_data():
            global cleaned_data

            if cleaned_data is not None:
                return True

            filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if not filename:
                return False

            try:
                cleaned_data = pd.read_csv(filename)

                if 'Compound' not in cleaned_data.columns:
                    messagebox.showerror(
                        "Error",
                        "El archivo CSV no contiene la columna necesaria 'Compound'."
                    )
                    cleaned_data = None
                    return False

                return True
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar y procesar el archivo: {e}")
                cleaned_data = None
                return False

        def seleccionar_variable_y():
            """
            Open a Toplevel to choose the column to plot.
            """
            df = cleaned_data

            # Available numeric columns
            numeric_cols = [
                col for col in df.columns
                if col != 'Compound' and pd.api.types.is_numeric_dtype(df[col])
            ]

            if not numeric_cols:
                messagebox.showerror(
                    "Error",
                    "There are no any numeric columns to plot"
                )
                return

            selector = tk.Toplevel(root)
            selector.title("Select independent variable")

            tk.Label(
                selector,
                text="Choose a variable to plot:",
                font=("Arial", 11)
            ).pack(padx=10, pady=(10, 5))

            seleccion_var = tk.StringVar()

            # Si existe S_S, la ponemos como default
            if "S_S" in numeric_cols:
                seleccion_var.set("S_S")
            else:
                seleccion_var.set(numeric_cols[0])

            combo = ttk.Combobox(
                selector,
                textvariable=seleccion_var,
                values=numeric_cols,
                state="readonly",
                width=30
            )
            combo.pack(padx=10, pady=5)

            btn_frame = tk.Frame(selector)
            btn_frame.pack(pady=(10, 10))

            def on_aceptar():
                score_col = seleccion_var.get()
                if not score_col:
                    messagebox.showerror("Error", "You need to choose a variable.")
                    return

                selector.destroy()

                # Crear ventana de gráfica y llamar show_graph
                graph_window = tk.Toplevel(root)
                graph_window.title(f"{score_col} vs Compound")

                try:
                    show_graph(
                        score_col=score_col,
                        title=f"{score_col} vs Compound",
                        xlabel='Compound',
                        ylabel=score_col,
                        compound_label=acronimo_var.get(),
                        legend_loc='best',
                        parent=graph_window
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Plotting error: {e}")
                    graph_window.destroy()

            def on_cancelar():
                selector.destroy()

            tk.Button(btn_frame, text="Accept", command=on_aceptar).pack(
                side="left", padx=5
            )
            tk.Button(btn_frame, text="Cancel", command=on_cancelar).pack(
                side="left", padx=5
            )

            # Centrar un poco la ventana sobre root (opcional, si quieres)
            selector.transient(root)
            selector.grab_set()
            selector.focus_set()

        # Flujo principal del handler
        if not asegurar_cleaned_data():
            return

        seleccionar_variable_y()

    # Botón para abrir la ventana de gráficos
    show_graph_button = tk.Button(frame_csv, text="PLOT RESULTS  📊",
                                  font=("Arial", 14),
                                  command=open_graph_window)
    show_graph_button.pack(pady=20)

    center_window(root, 1600, 700)

    root.mainloop()

#-------------------------------------------------------------------------------------------------------------------------------------------
# Section to make the molecular representations and 3D conformers from SMILES
#-------------------------------------------------------------------------------------------------------------------------------------------

def show_processing_message(window):
    processing_window = tk.Toplevel(window)
    processing_window.title("Processing")
    tk.Label(
        processing_window,
        text="Processing... Please wait.",
        font=("Arial", 14)
    ).pack(pady=20, padx=20)
    center_window(processing_window, 320, 110)
    return processing_window

def update_progress(progress_bar, current, total):
    if total <= 0:
        return
    progress = int((current / total) * 100)
    progress_bar['value'] = progress
    progress_bar.update_idletasks()

def heuristic_num_confs(mol):
    """
    Decide cuántos conformeros generar en función del número de enlaces rotables (RB).
    Pensado para moléculas tipo fármaco.
    """
    rb = rdMolDescriptors.CalcNumRotatableBonds(mol)

    if rb <= 2:
        return 10       # moléculas muy rígidas
    elif rb <= 5:
        return 20       # flexibilidad moderada
    elif rb <= 8:
        return 30
    elif rb <= 12:
        return 50
    else:
        return 75       # muy flexibles; podrías subir a 100 si quieres

def generate_3d_conformations(data_frame, num_confs=None, progress_bar=None):
    """
    Genera conformaciones 3D usando ETKDGv3 + UFF.
    Si num_confs es None, decide cuántos conformeros generar por molécula
    usando una heurística basada en el número de enlaces rotables (RB).

    Estrategia:
      1) Intento "estricto" con ETKDGv3 por defecto.
      2) Si no se generan conformeros, intento "relajado"
         (useBasicKnowledge=False, enforceChirality=False, useRandomCoords=True).
    """
    # Parámetros estrictos (por defecto)
    ps_strict = AllChem.ETKDGv3()
    ps_strict.clearConfs = False

    total = len(data_frame)

    mol_3d_list = []
    best_etkdg_conf_list = []

    for idx, (_, row) in enumerate(data_frame.iterrows(), start=1):
        smi = row['smile']

        try:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                mol_3d_list.append(None)
                best_etkdg_conf_list.append(None)
                if progress_bar:
                    update_progress(progress_bar, idx, total)
                continue

            # Heurística para número de conformeros si el usuario no especifica
            n_confs = num_confs if num_confs is not None else heuristic_num_confs(mol)

            mol_3D = AllChem.AddHs(mol)

            # 1) Intento estricto
            cid_list = AllChem.EmbedMultipleConfs(
                mol_3D,
                numConfs=n_confs,
                params=ps_strict
            )

            # 2) Si falla, intento relajado
            if not cid_list:
                ps_relaxed = AllChem.ETKDGv3()
                ps_relaxed.clearConfs = False
                ps_relaxed.useBasicKnowledge = False
                ps_relaxed.enforceChirality = False
                ps_relaxed.useRandomCoords = True

                cid_list = AllChem.EmbedMultipleConfs(
                    mol_3D,
                    numConfs=n_confs,
                    params=ps_relaxed
                )

            # Si aún así no hay conformadores, marcamos como None
            if not cid_list:
                mol_3d_list.append(None)
                best_etkdg_conf_list.append(None)
                if progress_bar:
                    update_progress(progress_bar, idx, total)
                continue

            # Optimización UFF sobre todos los confórmeros
            etkdg_energies = AllChem.UFFOptimizeMoleculeConfs(mol_3D, numThreads=0)
            etkdg_energies_sorted = sorted(etkdg_energies, key=lambda x: x[1])
            min_etkdg_energy_conf = etkdg_energies_sorted[0][0]

            mol_3d_list.append(mol_3D)
            best_etkdg_conf_list.append(min_etkdg_energy_conf)

        except Exception:
            # Cualquier problema con esta molécula → la marcamos como None y seguimos
            mol_3d_list.append(None)
            best_etkdg_conf_list.append(None)

        if progress_bar:
            update_progress(progress_bar, idx, total)

    data_frame['mol_3D'] = mol_3d_list
    data_frame['best_etkdg_conf'] = best_etkdg_conf_list


'''def generate_3d_conformations(data_frame, num_confs=None, progress_bar=None):
    """
    Genera conformaciones 3D usando ETKDGv3 + UFF.
    Si num_confs es None, decide cuántos conformeros generar por molécula
    usando una heurística basada en el número de enlaces rotables (RB).
    """
    ps = AllChem.ETKDGv3()
    ps.clearConfs = False

    mol_3d_list = []
    best_etkdg_conf_list = []

    total = len(data_frame)

    for idx, (_, row) in enumerate(data_frame.iterrows(), start=1):
        smi = row['smile']

        try:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                # SMILES inválido → marcamos como None
                mol_3d_list.append(None)
                best_etkdg_conf_list.append(None)
                if progress_bar:
                    update_progress(progress_bar, idx, total)
                continue

            # Si el usuario no especifica num_confs, usamos la heurística
            n_confs = num_confs if num_confs is not None else heuristic_num_confs(mol)

            mol_3D = AllChem.AddHs(mol)
            cid_list = AllChem.EmbedMultipleConfs(mol_3D, numConfs=n_confs, params=ps)

            if not cid_list:
                mol_3d_list.append(None)
                best_etkdg_conf_list.append(None)
                if progress_bar:
                    update_progress(progress_bar, idx, total)
                continue

            # Optimización UFF sobre todos los confórmeros
            etkdg_energies = AllChem.UFFOptimizeMoleculeConfs(mol_3D, numThreads=0)
            etkdg_energies_sorted = sorted(etkdg_energies, key=lambda x: x[1])
            min_etkdg_energy_conf = etkdg_energies_sorted[0][0]

            mol_3d_list.append(mol_3D)
            best_etkdg_conf_list.append(min_etkdg_energy_conf)

        except Exception:
            # Si cualquier cosa truena para esta molécula, la marcamos como None y seguimos
            mol_3d_list.append(None)
            best_etkdg_conf_list.append(None)

        if progress_bar:
            update_progress(progress_bar, idx, total)

    data_frame['mol_3D'] = mol_3d_list
    data_frame['best_etkdg_conf'] = best_etkdg_conf_list'''

def save_sdf_file(data_frame, initial_dir, progress_bar=None):
    """
    Pide una ruta para guardar el .sdf, genera los conformeros 3D
    y escribe solo el conformero de menor energía por molécula.
    Si alguna molécula falla, se salta y se reporta el número de línea (si existe).
    """
    save_path = filedialog.asksaveasfilename(
        defaultextension=".sdf",
        initialdir=initial_dir,
        initialfile="smiles_3D.sdf",
        filetypes=[("SDF files", "*.sdf")]
    )
    if not save_path:
        return None  # usuario canceló

    # Generar conformaciones 3D
    generate_3d_conformations(data_frame, progress_bar=progress_bar)

    sdf_writer = Chem.SDWriter(save_path)
    failed_lines = []

    for _, row in data_frame.iterrows():
        mol_3D = row.get('mol_3D', None)
        conf_id = row.get('best_etkdg_conf', None)

        # número de línea original (solo está para el panel derecho)
        line_number = row.get('line_number', None)

        if mol_3D is None or conf_id is None:
            if line_number is not None:
                failed_lines.append(line_number)
            continue

        try:
            sdf_writer.write(mol_3D, confId=int(conf_id))
        except Exception:
            if line_number is not None:
                failed_lines.append(line_number)
            continue

    sdf_writer.close()

    # Avisar si hubo fallos
    if failed_lines:
        failed_lines = sorted(set(failed_lines))
        msg = (
            "Some SMILES could not be processed and were skipped.\n\n"
            "Problematic entries (line numbers in the pasted list):\n"
            + ", ".join(str(n) for n in failed_lines)
        )
        messagebox.showwarning("Warning", msg)

    return os.path.dirname(save_path)


'''def save_sdf_file(data_frame, initial_dir, progress_bar=None):
    """
    Pide una ruta para guardar el .sdf, genera los conformeros 3D
    y escribe solo el conformero de menor energía por molécula.
    """
    save_path = filedialog.asksaveasfilename(
        defaultextension=".sdf",
        initialdir=initial_dir,
        initialfile="smiles_3D.sdf",
        filetypes=[("SDF files", "*.sdf")]
    )
    if not save_path:
        return None  # usuario canceló

    # Generar conformaciones 3D
    generate_3d_conformations(data_frame, progress_bar=progress_bar)

    sdf_writer = Chem.SDWriter(save_path)
    for _, row in data_frame.iterrows():
        mol_3D = row.get('mol_3D', None)
        conf_id = row.get('best_etkdg_conf', None)
        if mol_3D is None or conf_id is None:
            continue
        sdf_writer.write(mol_3D, confId=conf_id)
    sdf_writer.close()

    return os.path.dirname(save_path)'''

def create_2d_structures(estructuras_seleccionadas, save_dir):
    """
    Crea un grid PNG con las estructuras 2D.
    """
    PandasTools.AddMoleculeColumnToFrame(
        estructuras_seleccionadas,
        'smile',
        'structure2D',
        includeFingerprints=True
    )

    if 'Compound' not in estructuras_seleccionadas.columns:
        estructuras_seleccionadas['Compound'] = estructuras_seleccionadas.index

    estructuras_seleccionadas['legend'] = estructuras_seleccionadas.apply(
        lambda row: f"{row['Compound']}",
        axis=1
    )

    img = PandasTools.FrameToGridImage(
        estructuras_seleccionadas,
        column='structure2D',
        molsPerRow=4,
        subImgSize=(500, 500),
        legendsCol='legend'
    )
    image_path = os.path.join(save_dir, "structures_grid.png")
    img.save(image_path)
    img.show()

def process_smiles_list(smiles_text, window):
    """
    Procesa la lista pegada de SMILES (lado derecho).
    """
    try:
        processing_window = show_processing_message(window)
        window.update_idletasks()

        raw_text = smiles_text.get("1.0", tk.END).strip()
        smiles_list = [line.strip() for line in raw_text.split('\n') if line.strip()]

        if len(smiles_list) == 0:
            messagebox.showerror("Error", "The SMILES list is empty.")
            processing_window.destroy()
            return

        # Validar SMILES (usamos tu función existente)
        valid_smiles = validate_smiles(smiles_list)
        if not valid_smiles:
            messagebox.showerror("Error", "No valid SMILES were found in the list.")
            processing_window.destroy()
            return

        # Construimos un DataFrame que incluye el número de línea original
        rows = []
        valid_queue = list(valid_smiles)  # para manejar SMILES repetidos sin duplicar filas

        for line_idx, smi in enumerate(smiles_list, start=1):
            if smi in valid_queue:
                rows.append({
                    'smile': smi,
                    'line_number': line_idx
                })
                # quitamos esta ocurrencia para no asignar la misma línea a varias filas
                valid_queue.remove(smi)

            if not valid_queue:
                break  # ya asignamos todos los SMILES válidos

        data_frame = pd.DataFrame(rows, columns=['smile', 'line_number'])

        # Barra de progreso
        progress_bar = ttk.Progressbar(
            processing_window,
            orient='horizontal',
            length=280,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        window.update_idletasks()

        save_dir = save_sdf_file(data_frame, os.getcwd(), progress_bar)
        if save_dir:
            create_2d_structures(data_frame.copy(), save_dir)

        processing_window.destroy()

    except Exception as e:
        try:
            processing_window.destroy()
        except Exception:
            pass
        messagebox.showerror("Error", f"Error while processing the SMILES list:\n{e}")


'''def process_smiles_list(smiles_text, window):
    """
    Procesa la lista pegada de SMILES (lado derecho).
    """
    try:
        processing_window = show_processing_message(window)
        window.update_idletasks()

        raw_text = smiles_text.get("1.0", tk.END).strip()
        smiles_list = [line.strip() for line in raw_text.split('\n') if line.strip()]

        if len(smiles_list) == 0:
            messagebox.showerror("Error", "The SMILES list is empty.")
            processing_window.destroy()
            return

        # Validar SMILES
        valid_smiles = validate_smiles(smiles_list)
        if not valid_smiles:
            messagebox.showerror("Error", "No valid SMILES were found in the list.")
            processing_window.destroy()
            return

        data_frame = pd.DataFrame(valid_smiles, columns=['smile'])

        # Barra de progreso
        progress_bar = ttk.Progressbar(
            processing_window,
            orient='horizontal',
            length=280,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        window.update_idletasks()

        save_dir = save_sdf_file(data_frame, os.getcwd(), progress_bar)
        if save_dir:
            create_2d_structures(data_frame.copy(), save_dir)

        processing_window.destroy()

    except Exception as e:
        try:
            processing_window.destroy()
        except Exception:
            pass
        messagebox.showerror("Error", f"Error while processing the SMILES list:\n{e}")'''

def process_ss_csv(ss_csv_path, acronimo_var, num_estructuras_var, window):
    """
    Procesa un archivo {name}_SS.csv generado por CADMApy (lado izquierdo),
    selecciona las mejores estructuras y genera 3D.
    """
    try:
        processing_window = show_processing_message(window)
        window.update_idletasks()

        file_path = ss_csv_path.get().strip()
        acronimo = acronimo_var.get().strip()

        if not file_path:
            messagebox.showerror("Error", "Please load a CADMApy SELECTION SCORES file (_SS.csv).")
            processing_window.destroy()
            return

        if not num_estructuras_var.get().strip():
            messagebox.showerror("Error", "Please specify the number of structures to generate.")
            processing_window.destroy()
            return

        try:
            num_estructuras = int(num_estructuras_var.get())
            if num_estructuras <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "The number of structures must be a positive integer.")
            processing_window.destroy()
            return

        merged_data = pd.read_csv(file_path)
        if 'smile' not in merged_data.columns:
            messagebox.showerror("Error", "The CSV file must contain a 'smile' column.")
            processing_window.destroy()
            return

        if 'S_S' not in merged_data.columns:
            messagebox.showerror("Error", "The CSV file must contain the column 'S_S' (Selection Score).")
            processing_window.destroy()
            return

        merged_data = merged_data.sort_values(by='S_S', ascending=False)
        initial_dir = os.path.dirname(file_path)

        if 'Compound' not in merged_data.columns:
            merged_data.rename(columns={'name': 'Compound'}, inplace=True)

        if num_estructuras > len(merged_data):
            messagebox.showwarning(
                "Warning",
                f"The maximum available number of structures is {len(merged_data)}.\n"
                f"Using {len(merged_data)} instead."
            )
            num_estructuras = len(merged_data)

        # Barra de progreso
        progress_bar = ttk.Progressbar(
            processing_window,
            orient='horizontal',
            length=280,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        window.update_idletasks()

        estructuras_seleccionadas = select_structures(merged_data, acronimo, num_estructuras)

        # Guardar SDF y generar grid 2D
        save_dir = save_sdf_file(estructuras_seleccionadas.copy(), initial_dir, progress_bar)
        if save_dir:
            create_2d_structures(estructuras_seleccionadas.copy(), save_dir)

        processing_window.destroy()

    except Exception as e:
        try:
            processing_window.destroy()
        except Exception:
            pass
        messagebox.showerror("Error", f"Error while processing the file:\n{e}")

def select_structures(merged_data, acronimo, num_estructuras):
    """
    Toma las top-N estructuras por S_S y, si existe un 'Compound' igual a acronimo,
    lo fuerza a estar incluido.
    """
    estructuras_seleccionadas = merged_data.nlargest(num_estructuras, 'S_S').copy()

    if acronimo and acronimo in merged_data['Compound'].values:
        acronimo_info = merged_data.loc[merged_data['Compound'] == acronimo]
        estructuras_seleccionadas = pd.concat(
            [acronimo_info, estructuras_seleccionadas]
        ).drop_duplicates().head(num_estructuras)

    return estructuras_seleccionadas

def load_ss_csv_file(var, check_label, file_label):
    """
    Helper específico para la ventana SMILES to 3D.
    Solo acepta archivos CSV y muestra el nombre corto.
    """
    filename = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    if filename:
        var.set(filename)
        check_label.config(text="✔")
        file_label.config(text=os.path.basename(filename))

def conformers_from_smiles():
    """
    Ventana SMILES to 3D:
    - Lado izquierdo: archivo CADMApy (_SS.csv)
    - Lado derecho: lista pegada de SMILES
    """
    window = tk.Toplevel()
    window.title("SMILES to 3D")

    # Configuración de layout principal (2 columnas)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)

    # Variables
    ss_csv_path = tk.StringVar()
    acronimo_var = tk.StringVar()
    num_estructuras_var = tk.StringVar(value="10")  # valor por defecto razonable

    # ----------------------------- LADO IZQUIERDO -----------------------------
    left_frame = ttk.LabelFrame(
        window,
        text="From CADMApy SELECTION SCORES file (_SS.csv)"
    )
    left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    left_frame.columnconfigure(0, weight=1)

    tk.Label(
        left_frame,
        text=(
            "Upload a CADMApy SELECTION SCORES file (name_SS.csv).\n"
            "The top-ranked compounds will be converted to 3D.\n"
            "Optionally, you can force one acronym to be included."
        ),
        justify="left",
        font=("Arial", 10)
    ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 10))

    # File chooser
    csv_frame = ttk.Frame(left_frame)
    csv_frame.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 10))

    ss_csv_check_label = tk.Label(csv_frame, text="", font=("Arial", 12))
    ss_csv_check_label.pack(side=tk.LEFT, padx=(0, 5))

    ss_csv_button = tk.Button(
        csv_frame,
        text="Load _SS.csv file",
        command=lambda: load_ss_csv_file(ss_csv_path, ss_csv_check_label, ss_csv_label)
    )
    ss_csv_button.pack(side=tk.LEFT)

    ss_csv_label = tk.Label(csv_frame, text="", font=("Arial", 10), anchor="w")
    ss_csv_label.pack(side=tk.LEFT, padx=(8, 0))

    # Acronym
    tk.Label(
        left_frame,
        text="Additionally include this 'Compound', no matter the rank (optional):",
        font=("Arial", 10)
    ).grid(row=2, column=0, sticky="w", padx=5, pady=(10, 0))

    tk.Entry(left_frame, textvariable=acronimo_var, width=20).grid(
        row=3, column=0, sticky="w", padx=5, pady=(0, 5)
    )

    # Number of structures
    tk.Label(
        left_frame,
        text="Number of top structures to convert to 3D:",
        font=("Arial", 10)
    ).grid(row=4, column=0, sticky="w", padx=5, pady=(10, 0))

    tk.Entry(left_frame, textvariable=num_estructuras_var, width=10).grid(
        row=5, column=0, sticky="w", padx=5, pady=(0, 10)
    )

    tk.Button(
        left_frame,
        text="Generate 3D from SELECTION SCORES",
        font=("Arial", 11, "bold"),
        command=lambda: process_ss_csv(ss_csv_path, acronimo_var, num_estructuras_var, window)
    ).grid(row=6, column=0, sticky="ew", padx=5, pady=(10, 5))

    # ----------------------------- LADO DERECHO -----------------------------
    right_frame = ttk.LabelFrame(
        window,
        text="From pasted SMILES list"
    )
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(1, weight=1)

    tk.Label(
        right_frame,
        text=(
            "Paste any list of SMILES you want to convert to 3D.\n"
            "One SMILES per line. Invalid SMILES will be skipped."
        ),
        justify="left",
        font=("Arial", 10)
    ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 5))

    smiles_text = scrolledtext.ScrolledText(
        right_frame,
        wrap=tk.NONE,
        width=60,
        height=18
    )
    smiles_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

    tk.Button(
        right_frame,
        text="Generate 3D from SMILES list",
        font=("Arial", 11, "bold"),
        command=lambda: process_smiles_list(smiles_text, window)
    ).grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 5))

    center_window(window, 800, 500)

#-------------------------------------------------------------------------------------------------------------------------------------------
# Section to modify the welcome window 🧠💊
#-------------------------------------------------------------------------------------------------------------------------------------------

# Ventana de bienvenida
welcome_window = tk.Tk()
welcome_window.configure(bg="#FFFFFF")
welcome_window.title("Welcome to CADMA-py")

# Configurar el logo y los botones en la ventana de bienvenida
logo_path = os.path.join(os.path.dirname(__file__), "CADMA-Py.png")
logo = tk.PhotoImage(file=logo_path)
logo_label = tk.Label(welcome_window, image=logo)
logo_label.configure(bg="#FFFFFF")
logo_label.grid(row=0, column=0, columnspan=3, pady=0)

welcome_label = tk.Label(welcome_window, text="Welcome to CADMA.py", font=("Helvetica", 24))
welcome_label.configure(bg="#FFFFFF")
welcome_label.grid(row=1, column=0, columnspan=3, pady=0)

#doc_button = tk.Button(welcome_window, text="DOCUMENTATION", command=open_documentation)
doc_button = tk.Button(welcome_window, text="DOCUMENTATION", command=open_notebook)
doc_button.configure(bg="#FFFFFF")
doc_button.grid(row=2, column=0, pady=10, padx=10)

contact_button = tk.Button(welcome_window, text="CONTACT & REFERENCES", command=show_contact_info)
contact_button.configure(bg="#FFFFFF")
contact_button.grid(row=3, column=2, pady=10, padx=10)

#files_button = tk.Button(welcome_window, text="DOCKING", command=lambda: messagebox.showwarning("Amazing Feature", "Imagine pressing this button and your thesis is magically written for you!\n\nBut... This functionality has not been implemented yet.") )
#files_button.configure(bg="#FFFFFF")
#files_button.grid(row=2, column=1, pady=10, padx=10)

newReferenceSet_button = tk.Button(welcome_window, text="CREATE A REFERENCE SET", command=create_reference_set_app)
newReferenceSet_button.configure(bg="#FFFFFF")
newReferenceSet_button.grid(row=2, column=1, pady=10, padx=10)

start_button = tk.Button(welcome_window, text="SELECTION SCORES", command=start_main_app)
start_button.configure(bg="#FFFFFF")
start_button.grid(row=2, column=2, pady=10, padx=10)

thesis_button = tk.Button(welcome_window, text="SMILES to 3D", command=conformers_from_smiles)
thesis_button.configure(bg="#FFFFFF")
thesis_button.grid(row=3, column=0, pady=10, padx=10)

# Centrar la ventana en la pantalla
center_window(welcome_window, 740, 450)

welcome_window.mainloop()
