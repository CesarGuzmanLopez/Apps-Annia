import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser

# Optional LaTeX rendering for equations in the Selection Scores tab
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _MATPLOTLIB_AVAILABLE = True
except Exception:
    _MATPLOTLIB_AVAILABLE = False


try:
    from CADMA import center_window
except Exception:
    center_window = None


def make_text(parent, font=("Helvetica", 12)):
    w = ScrolledText(parent, wrap="word", width=100, height=20)
    w.configure(font=font, spacing1=2, spacing3=4)
    w.pack(fill="both", expand=True)
    return w

def open_notebook():
    """
    Open the CADMA.py documentation window with a tabbed notebook.
    Tabs:
        - Overview (CADMA-Chem protocol and design philosophy)
        - ADME properties
        - Reference sets
        - Selection scores
        - Conformers from SMILES
    """
    doc_window = tk.Toplevel()
    doc_window.title("CADMA.py • Documentation")
    doc_window.configure(bg="#FFFFFF")
    doc_window.resizable(True, True)

    try:
        if center_window:
            center_window(doc_window, 1000, 770)
        else:
            doc_window.geometry("1000x770")
    except Exception:
        doc_window.geometry("1000x770")

    root = ttk.Frame(doc_window, padding=12)
    root.grid(sticky="nsew")
    doc_window.columnconfigure(0, weight=1)
    doc_window.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    # Header
    header = ttk.Frame(root)
    header.grid(row=0, column=0, sticky="ew")
    ttk.Label(header, text="CADMA.py",
              font=("Helvetica", 20, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(
        header,
        text="Computer-Assisted Design of Multifunctional Antioxidants (CADMA-Chem workflow helper)",
        font=("Helvetica", 12)
    ).grid(row=1, column=0, sticky="w", pady=(2, 0))
    ttk.Separator(root).grid(row=1, column=0, sticky="ew", pady=(6, 8))

    nb = ttk.Notebook(root)
    nb.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
    root.rowconfigure(2, weight=1)

    # ------------------------------------------------------------------
    # TAB 1 — Overview / CADMA-Chem protocol
    # ------------------------------------------------------------------
    tab_over = ttk.Frame(nb, padding=8)
    nb.add(tab_over, text="Overview")

    txt_over = make_text(tab_over)

    overview_text = """What CADMA.py is for
CADMA.py is a companion graphical interface for the CADMA-Chem protocol (Computational protocol Aimed to Design Multifunctional Antioxidants based on Chemical properties) and is intended to:
  • Compare pharmacokinetic-relevant properties between a reference set and one or more sets of proposed molecules.
  • Combine ADME, toxicity and synthetic accessibility into a single selection score S_S that can be used as a first filter.
  • Help you build or update disease-specific reference sets that will serve as normalization anchors for future projects.

The software does **not** replace detailed pharmacokinetic modelling, full QSAR development or expert medicinal chemistry judgement. Instead, it provides a transparent scoring layer that helps you triage large lists drug-like molecules in a consistent way. The central idea is to use a *reference set* of oral drugs associated with a specific disease of interest or therapeutic context and compare proposed candidates against this reference.

In a conceptual view the CADMA-Chem protocol is implemented in three stages:
  Stage 1 – Data model and reference set
    • Define the disease or therapeutic problem.
    • Build a reference set: a curated list of drugs used for that indication, with experimental or predicted ADMETSA data.
    • Compute average values and standard deviations for all properties in the reference set (ADME, toxicity and synthetic accessibility).

  Stage 2 – First-pass screening (this is where CADMA.py is focused)
    • Design or import new candidates (SMILES).
    • Predict ADME descriptors, toxicity and SA for each candidate.
    • Normalize each property with respect to the reference set.
    • Compute multiparametric scores (ADME, toxicity, SA and global selection score S_S).
    • Rank the candidates and select a first subset for deeper studies.

  Stage 3 – Refinement
    • For the most promising candidates, perform detailed quantum chemistry, pKa and speciation analysis, passive transport estimations, docking, similarity indices and retrosynthetic planning.
    • Combine these data with experimental evidence to decide which structures should go to synthesis.
"""
    txt_over.insert("end", overview_text)
    txt_over.configure(state="disabled")

    # ------------------------------------------------------------------
    # TAB 1.1 — CADMA-Chem workflow
    # ------------------------------------------------------------------
    tab_workflow = ttk.Frame(nb, padding=8)
    nb.add(tab_workflow, text="Workflow")

    txt_workflow = make_text(tab_workflow)

    workflow_text ="""----------------------------------------------------------------------------
STAGE 1: Problem and reference definition
----------------------------------------------------------------------------
    Disease / therapeutic problem
          │
          ▼
    Lead compounds, targets and key interactions
          │
          ├──► Pharmacophore model 
          ▼
    Design of fragments, functional groups and scaffolds
          │
          ▼
    Reference set (approved drugs / leads for this indication)
          │   (ADME, Toxicity, SA statistics are computed here)
----------------------------------------------------------------------------
  STAGE 2: First-pass screening with CADMA.py
----------------------------------------------------------------------------
    Design candidates (create series of derivatives with SMILE-it or equivalent protocol with toxicophores detection)  
          │
          ├──► ADME descriptor calculation
          ├──► Toxicity prediction (LD50, M, DT)
          ├──► Synthetic accessibility (SA index)
          │
          ▼
    Selection scores (S_ADME, S_T, S_SA, S_S)
          │
          ▼
    Ranked candidate list and top-N subset (Subset 1)
----------------------------------------------------------------------------
  STAGE 3: Computational refinement and synthesis
----------------------------------------------------------------------------
    Top-N subset
          │
          ├──► pKa and molar fractions; Q(passive)
          ├──► Docking and similarity indices
          │
          ▼
    Best candidates (Subset 2) ───────────────────
          │                                                                                                       │
          ├──► Retrosynthesis and route prioritization                             └──► Computational refinment 
          ├──► Synthesis                                                                                            |──► Thermochemistry     
          └──► In vitro / in vivo evaluation and model refinement                           └──► Chemical Kinetics
                                                                                                                                     └──► ONIOM
                                                                                                                                     └──► Molecular Dynamics
"""
    txt_workflow.insert("end", workflow_text)
    txt_workflow.configure(state="disabled")

    # ------------------------------------------------------------------                                                                                                                                                                                                                                                                              # ------------------------------------------------------------------
    # TAB 1.2 — CADMA-Chem intervals
    # ------------------------------------------------------------------
    tab_intervals = ttk.Frame(nb, padding=8)
    nb.add(tab_intervals, text="ADME intervals")

    txt_intervals = make_text(tab_intervals)

    intervals_text =""" 
ADME PROPERTY INTERVALS IN CADMA-Chem
=====================================

The ADME intervals in CADMA-Chem derive from classical medicinal chemistry rules for oral drug-likeness and passive membrane permeability. Each rule proposes acceptable physicochemical limits; CADMA-Chem adopts the restrictive overlap of these ranges to create a clear, practical filter for early screening.
1. Molar Weight (MW)
    Lipinski:           ≤ 500
    Ghose:              160–480
    Walters & Murcko:   200–500
    Teague (lead-like): 100–350
    CNS-oriented:       typically ≤ 400
    CADMA-Chem:         200–480
    Reason: MW strongly influences passive diffusion; very large molecules tend to show poor permeability.

2. LogP
    Lipinski:           ≤ 5
    Ghose:              –0.4 to 5.6
    Egan:               –0.4 to 5.88
    Walters & Murcko:   –2.0 to 5.0
    Teague (lead-like): 1–3
    CNS-friendly:       moderate ~2–4
    CADMA-Chem:         –0.4 to 5.0
    Reason: lipophilicity balances solubility and permeability. Extremely low or high values increase ADME risk.

3. H-Bond Donors (HBD)
    Lipinski:           ≤ 5
    Walters & Murcko:   ≤ 5
    CNS-preferable:     ≤ 3
    CADMA-Chem:         ≤ 5
    Reason: a high number of donors penalizes passive diffusion.

4. H-Bond Acceptors (HBA)
    Lipinski:           ≤ 10
    Walters & Murcko:   ≤ 10
    CNS-friendly:       ~≤ 6
    CADMA-Chem:         ≤ 10
    Reason: acceptors contribute to polarity and reduce permeability when present in excess.

5. Topological Polar Surface Area (TPSA)
    Veber:              ≤ 140 Å²
    Egan:               ≤ 131.6 Å²
    CNS-oriented:       ≤ 60–70 Å²
    CADMA-Chem:         ≤ 70 Å²
    Reason: TPSA tracks polarity and passive transport. Values below ~70 Å² are associated with good permeability and potential CNS entry.

6. Rotatable Bonds (RB)
    Veber:              ≤ 10
    Walters & Murcko:   ≤ 8
    CADMA-Chem:         ≤ 8
    Reason: molecular flexibility inversely correlates with oral bioavailability; fewer rotatable bonds generally improve ADME.

7. Molar Refractivity (MR)
    Ghose:              40–130
    Walters & Murcko:   similar guidance
    CADMA-Chem:         40–130
    Reason: MR reflects molecular volume and polarizability, which are relevant for intermolecular recognition and binding.

8. Heavy Atom Count (XAt)
    Ghose:              20–70
    Walters & Murcko:   20–50
    CADMA-Chem:         20–50
    Reason: heavy atom count is a simple measure of size and structural complexity; very large frameworks tend to have poor PK.

9. Total H-Bonding Capacity (HBD + HBA)
    General guidance:   ≤ 12
    CADMA-Chem:         ≤ 12
    Reason: combines donors and acceptors into a global polarity measure relevant for passive permeability.

Additional Heuristics
    CNS polarity window:
        TPSA ≤ 60–70 Å², MW ≤ 400, logP ~2–4 → favors CNS penetration.
    Pfizer 3/75:
        logP > 3 and TPSA < 75 Å² → higher risk of toxicity from excessive permeability.
    Pfizer 2/100:
        HBD ≤ 2 and TPSA < 100 Å² → good probability of oral absorption.
    GSK 4/400:
        logP ≤ 4 and MW ≤ 400 → reduced probability of clinical failure due to toxicity.
    Teague lead-optimization guidance:
        during lead optimization, MW and logP typically increase; keeping early leads near 100–350 Da and logP 1–3 leaves room for growth while remaining in the drug-like space.
    Brenk structural alerts:
        identifies reactive or unstable substructures ("toxicophores") that may compromise safety or pharmacokinetics.

These intervals define a concise drug-likeness window and support the calculation of the ADME score (S_ADME) in CADMA-Chem. Users may adjust them for specialized chemotypes or non-classical delivery strategies.
"""
    txt_intervals.insert("end", intervals_text)
    txt_intervals.configure(state="disabled")

    # ------------------------------------------------------------------
    # TAB 2 — ADME properties
    # ------------------------------------------------------------------
    tab_adme = ttk.Frame(nb, padding=8)
    nb.add(tab_adme, text="ADME properties")

    txt_adme = make_text(tab_adme)

    adme_text = """
ADME values for compounds
==========================

This tab summarizes how CADMA.py computes the ADME-like descriptors and how they are turned into binary in-range flags and aggregate scores.
Descriptor calculation
----------------------
For every molecule, CADMA.py relies on RDKit to compute a small panel of physicochemical descriptors. In the code this is implemented in the functions:
  *load_and_process_smiles_for_RefSet* and *load_and_process_smiles*
For each `ROMol` object (RDKit molecule), the following functions are used:
        • Molecular weight (MW)                                   -> Descriptors.MolWt(ROMol)
        • Octanol/water partition coefficient (logP)        -> Descriptors.MolLogP(ROMol)
        • Molar refractivity (MR)                                     -> Descriptors.MolMR(ROMol)
        • Heavy-atom count (AtX)                                  -> Descriptors.HeavyAtomCount(ROMol)
        • H-bond acceptors (HBLA)                               -> rdMolDescriptors.CalcNumLipinskiHBA(ROMol)
        • H-bond donors (HBLD)                                    -> rdMolDescriptors.CalcNumLipinskiHBD(ROMol)
        • Rotatable bonds (RB)                                      -> rdMolDescriptors.CalcNumRotatableBonds(ROMol)
        • Topological polar surface area (PSA, Å²)       -> rdMolDescriptors.CalcTPSA(ROMol)

All descriptors are stored in the main working DataFrame with the column names: ['MW', 'logP', 'MR', 'AtX', 'HBLA', 'HBLD', 'RB', 'PSA']

Conversion to ADME flags
-----------------------
Each property P has a target interval [P_min, P_max] as listed in the Overview tab. For a given molecule i, CADMA.py evaluates a helper function:
    ADME_P(i) = 1  if  P_min <= P(i) <= P_max
                        = 0  otherwise

This is implemented in the helper function `en_rango` and applied to all properties in the dictionary `rangos`. The resulting binary flags are stored as:
    ADME_MW, ADME_logP, ..., ADME_PSA
and represent whether each descriptor lies inside the “ADME window” defined by the reference set design.

Aggregate ADME score S_ADME
---------------------------
For each molecule i, CADMA.py sums all ADME contributions: 
    
    N_ADME(i) = ADME_MW(i) + ADME_logP(i) + ... + ADME_PSA(i)

and then normalizes this sum by a constant defined for the current disease/reference set:

    S_ADME(i) = N_ADME(i) / Σ_ADME,ref

where Σ_ADME,ref is stored internally as `suma_adme_disease_var`. By construction, S_ADME is a dimensionless number that grows when more properties fall inside the desired ADME window and shrinks when several properties are out of range. In the plotting tools, S_ADME can be visualized either alone or as part of composite scores such as S_ADMET and S_S.
"""
    txt_adme.insert("end", adme_text)
    txt_adme.configure(state="disabled")

    # ------------------------------------------------------------------
    # TAB 3 — Create a new reference set
    # ------------------------------------------------------------------
    tab_ref = ttk.Frame(nb, padding=8)
    nb.add(tab_ref, text="Reference sets")

    txt_ref = make_text(tab_ref)

    ref_text = """
CREATE A NEW REFERENCE SET
==========================

A *reference set* is a curated collection of drugs or bioactive molecules that define the “desired” ADMETSA behaviour for a given
disease or therapeutic problem (e.g., Rett syndrome, Parkinson's disease, vascular dementia).

CADMA.py uses reference sets to compute:

  • Mean and standard deviation of ADME descriptors.
  • Mean and standard deviation of toxicity endpoints (LD50, M, DT).
  • Mean and standard deviation of synthetic accessibility (SA).
  • Global normalization constants (Σ_ADME,ref, LD50_ref, etc.)
    that are later used by the selection scores.

Required input files
--------------------
To build a new reference set you need several files, each one generated by an external tool:

  1) SMILES file for the reference drugs
     A `.smi`, `.smiles`, `.txt` or `.csv` file containing at least two columns:

       name, smile

     SMILES strings can be curated with any preferred pipeline (for example SMILE-It or RDKit notebooks).

  2) ADME / physicochemical properties
     CADMA.py can compute MW, logP, MR, AtX, HBLA, HBLD, RB and PSA directly from the SMILES using RDKit, so no external file is strictly required here.

  3) Toxicity CSV files (usually obtained from EPA TEST or similar tools)
     • Developmental toxicity (DT)
     • Mutagenicity (Ames test, M)
     • Oral rat LD50 (mg·kg⁻¹)

  4) Synthetic accessibility CSV
     A table containing a numerical SA index for each molecule in the reference set. In CADMA-Chem we typically use the AMBIT implementation, which returns values on a 1–10 scale where larger numbers indicate more difficult synthesis.

How CADMA.py processes a reference set
--------------------------------------
Internally, the function `reference_csv_data`:

  • Reads and sanitizes the SMILES file (via `load_and_process_smiles_for_RefSet`).
  • Attaches the ADME descriptors computed with RDKit.
  • Merges the toxicity CSV tables (DT, M, LD50) and the SA CSV using the molecule names as keys.
  • Computes averages and standard deviations for each property.
  • Stores these statistics in a disease-specific dictionary so they can be reused when calculating selection scores for new candidates.

Once a reference set has been built and saved, it becomes available in the main CADMA.py interface and can be selected whenever you want to screen a new series of molecules against that therapeutic context.
"""
    txt_ref.insert("end", ref_text)
    txt_ref.configure(state="disabled")


    # ------------------------------------------------------------------
    # TAB 4 — Selection scores
    # ------------------------------------------------------------------
    tab_scores = ttk.Frame(nb, padding=8)
    nb.add(tab_scores, text="Selection scores")

    # Usamos fuente monoespaciada para que las fórmulas se vean claras
    txt_scores = make_text(tab_scores, font=("Helvetica", 12))

    scores_text = r"""
SELECTION SCORES
==========================

CADMA.py combines ADME, toxicity and synthetic accessibility into a set of scalar scores. These are exactly the definitions implemented in the CADMA.py code, so any ranking based on S_S can be traced back to explicit formulas.
The mathematical expressions used for toxicity sub-scores, the combined ADMET score, the synthetic accessibility score and the final selection score S_S are shown below:

Notation
--------
For each candidate molecule i:

    LD50(i)   : predicted oral rat LD50 (mg·kg^-1)
    M(i)      : predicted Ames mutagenicity index
    DT(i)     : predicted developmental toxicity index
    SA(i)     : synthetic accessibility index
    S_ADME(i) : normalized ADME score (see ADME tab)

Reference-set averages:

    LD50_ref, M_ref, DT_ref, SA_ref  : mean values over the drugs in the selected reference set.

Toxicity sub-scores
-------------------
The toxicity block is encoded through three dimensionless sub-scores:

    S_LD50(i) = 1 + log10( (1 + LD50(i)) / (1 + LD50_ref) )

    S_M(i)    = 1 - log10( (1 + M(i))    / (1 + M_ref) )

    S_DT(i)   = 1 - log10( (1 + DT(i))   / (1 + DT_ref) )

Here the "+1" shift avoids taking the logarithm of zero and keeps the scores finite for very small predicted values. High LD50 or low M and DT values are rewarded with larger S_LD50, S_M and S_DT, respectively.

The overall toxicity score is the simple average:

    S_T(i) = ( S_LD50(i) + S_M(i) + S_DT(i) ) / 3


ADME–toxicity combined score
----------------------------
CADMA.py also defines a combined ADMET score:

    S_ADMET(i) = S_ADME(i) + S_T(i)

This is useful for quick two-dimensional plots (e.g. S_ADMET vs. index) and for inspecting the global behaviour of different derivative series.


Synthetic accessibility score
-----------------------------
Synthetic accessibility is summarized as:

    S_SA(i) = SA(i) / SA_ref

where SA_ref is the mean SA value in the reference set.

Molecules that are synthetically easier than the reference drugs (lower SA values) receive S_SA > 1, whereas structurally more complex molecules tend to show S_SA < 1.


Global selection score S_S
--------------------------
The final selection score S_S combines three weighted blocks:

    • ADME block        → weight 0.40
    • Toxicity block    → weight 0.40
    • Synth. access.    → weight 0.20

Internally, CADMA.py computes

    S_ADME^w(i) = 0.40 * S_ADME(i)
    S_T^w(i)    = 0.40 * S_T(i)
    S_SA^w(i)   = 0.20 * S_SA(i)

and the global selection score is:

    S_S(i) = S_ADME^w(i) + S_T^w(i) + S_SA^w(i)

which can also be written explicitly as:

    S_S(i) = 0.40 * S_ADME(i) + 0.40 * S_T(i) + 0.20 * S_SA(i)

The program stores this value in the column 'S_S' and uses it to:

    • sort the table of candidates
    • select the top-N molecules for conformer generation
    • produce plots of S_S vs. compound identifiers

Because the functional form is explicit and relatively simple, you can always reconstruct why a candidate ranks higher or lower by inspecting its ADME, toxicity and synthetic accessibility contributions separately.
"""
    txt_scores.insert("end", scores_text)
    txt_scores.configure(state="disabled")

    # ------------------------------------------------------------------
    # TAB 5 — Conformers from SMILES
    # ------------------------------------------------------------------
    tab_conf = ttk.Frame(nb, padding=8)
    nb.add(tab_conf, text="Conformers from SMILES")

    txt_conf = make_text(tab_conf)

    conf_text = """
CONFORMERS FROM SMILES
==========================

CADMA.py can generate 3D conformers for selected molecules and export them as an SDF file suitable for quantum chemistry, docking or other 3D-based workflows.
The corresponding GUI section is opened by the **CONFORMERS OF SMILES** button and is backed by the functions:
  • conformers_from_smiles
  • generate_3d_conformations
  • save_sdf_file

Two input modes
---------------
There are two ways of specifying which molecules should be converted to 3D:
  1) From a selection-score CSV ({name}_SS.csv)
     • Load a CSV file containing a column 'S_S' and the original SMILES.
     • Specify how many top-ranking structures you want to convert (e.g. the top 20 molecules according to S_S).
     • CADMA.py selects the top-N rows and feeds their SMILES to the conformer generator.

  2) From a manual SMILES list
     • Paste or type a list of SMILES strings into the text box on the right-hand side of the window (one SMILES per line).
     • The program parses and sanitizes each SMILES and discards invalid entries.
     • The remaining molecules are sent to the same 3D generator.

Conformer generation workflow
-----------------------------
The algorithm uses RDKit's ETKDGv3 protocol to generate multiple 3D conformers per molecule and then optimizes them with UFF:

    SMILES
      └─► RDKit MolFromSmiles
              └─► AddHs (explicit hydrogens)
                      └─► EmbedMultipleConfs(ETKDGv3, N)
                              └─► UFFOptimizeMoleculeConfs
                                      └─► rank by energy
                                              └─► select lowest-energy conformer

In code, the key steps inside `generate_3d_conformations` are:

  • Define ETKDGv3 parameters:
        ps = AllChem.ETKDGv3()
        ps.clearConfs = False

  • Build a 3D-enabled molecule with hydrogens:
        mol_3D = AddHs(MolFromSmiles(smile))

  • Generate N trial conformers:
        AllChem.EmbedMultipleConfs(mol_3D, numConfs=N, params=ps)

  • Optimize all conformers with the UFF force field:
        energies = AllChem.UFFOptimizeMoleculeConfs(mol_3D, numThreads=0)

  • Sort conformers by energy and keep the index of the lowest-energy one:
        best_conf_id = sorted(energies, key=lambda x: x[1])[0][0]

The selected `mol_3D` together with `best_conf_id` is stored in the working DataFrame for each molecule. When you call **Save SDF**, the function `save_sdf_file` writes an SDF where each entry contains:

  • The optimized 3D coordinates of the chosen conformer.
  • The original compound name and acronym.
  • The selection score and other relevant properties as SD tags.

This makes it straightforward to continue the CADMA-Chem workflow with external tools (quantum-chemical geometry optimizations, docking, molecular dynamics, etc.) starting from a consistent, reproducible set of 3D structures generated directly from the SMILES handled in CADMA.py.
"""
    txt_conf.insert("end", conf_text)
    txt_conf.configure(state="disabled")

    # Footer
    footer = ttk.Frame(root)
    footer.grid(row=3, column=0, sticky="ew")
    footer.columnconfigure(0, weight=1)

    def open_repo():
        webbrowser.open_new("https://github.com/")

    ttk.Button(footer, text="Open repository", command=open_repo).grid(
        row=0, column=0, sticky="w", pady=4
    )
    ttk.Button(footer, text="Close", command=doc_window.destroy).grid(
        row=0, column=1, sticky="e", pady=4
    )

    doc_window.focus_set()
