import customtkinter as ctk
import os
from tkinter import filedialog
from decreto3eolico.analysis_executor import run_analysis

# Configura CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colori personalizzati
BOTTONI_FG = "#006400"      # Verde scuro
BOTTONI_HOVER = "#228B22"   # Verde più chiaro


def browse_file(entry_widget):
    filename = filedialog.askopenfilename()
    if filename:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, filename)


def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, directory)


def generate_report():
    files = {
        "distanza_angolo_WTG": file1_entry.get(),
        "input_file_CMG": file2_entry.get(),
        "input_file_meteo": file3_entry.get(),
        "input_file_turbine_parameters": file4_entry.get()
    }
    orografia_choice = orografia_var.get()
    results_dir = results_entry.get()

    if not all(files.values()) or not results_dir:
        status_label.configure(text="Errore: Seleziona tutti i file e la directory di output", text_color="red")
        return

    status_label.configure(text="Analisi in corso...", text_color="yellow")
    root.update_idletasks()

    try:
        run_analysis(
            files["distanza_angolo_WTG"],
            files["input_file_CMG"],
            files["input_file_meteo"],
            files["input_file_turbine_parameters"],
            orografia_choice,
            results_dir,
        )
        status_label.configure(text="Analisi completata con successo!", text_color="green")
    except Exception as e:
        status_label.configure(text=f"Errore durante l'analisi: {e}", text_color="red")
        return

    for entry in file_entries:
        entry.delete(0, ctk.END)


def apri_finestra_benvenuto():
    finestra = ctk.CTkToplevel(root)
    finestra.title("Benvenuto - Procedura")
    finestra.geometry("600x400")
    finestra.resizable(False, False)

    testo = """Passaggi principali dell'algoritmo:\n\n"""
    testo += """
    1. Caricamento dei dati meteo e CMG
    2. Validazione e filtraggio dei dati
    3. Calcolo soglia di attivazione
    4. Organizzazione dei dati iniziali
    5. Verifica condizioni attivazione procedura
    6. Avvio procedura iterativa
    7. Immissione specifica
    8. Rumore residuo
    9. Procedura iterativa
    10. Espressione dei risultati
    """

    label = ctk.CTkLabel(finestra, text=testo, justify="left")
    label.pack(expand=True, fill='both', padx=20, pady=20)

    bottone_chiudi = ctk.CTkButton(finestra, text="Chiudi", command=finestra.destroy,
                                   fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
    bottone_chiudi.pack(pady=10)


def apri_pdf_decreto():
    try:
        pdf_path = os.path.join(os.getcwd(), "decreto_allegato3.pdf")
        os.startfile(pdf_path)
    except Exception as e:
        status_label.configure(text=f"Errore apertura PDF: {e}", text_color="red")


# Crea finestra principale
root = ctk.CTk()
root.title("Decreto3 Eolico Report Generator")
root.geometry("1200x700")

# Frame principale
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill='both', expand=True)

left_frame = ctk.CTkFrame(main_frame)
left_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

right_frame = ctk.CTkFrame(main_frame)
right_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

# Bottoni in alto
top_buttons_frame = ctk.CTkFrame(root)
top_buttons_frame.pack(side='top', fill='x', pady=10)

guida_button = ctk.CTkButton(top_buttons_frame, text="Guida", command=apri_finestra_benvenuto,
                              fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
guida_button.pack(side='right', padx=10)

pdf_button = ctk.CTkButton(top_buttons_frame, text="Apri Decreto", command=apri_pdf_decreto,
                            fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
pdf_button.pack(side='right', padx=10)

# --- SINISTRA: Form di input ---
file1_entry = ctk.CTkEntry(left_frame, width=400)
file2_entry = ctk.CTkEntry(left_frame, width=400)
file3_entry = ctk.CTkEntry(left_frame, width=400)
file4_entry = ctk.CTkEntry(left_frame, width=400)
results_entry = ctk.CTkEntry(left_frame, width=400)

file_entries = [file1_entry, file2_entry, file3_entry, file4_entry, results_entry]

browse_buttons = [
    ctk.CTkButton(left_frame, text="Browse", command=lambda e=entry: browse_file(e),
                  fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
    for entry in file_entries[:-1]
]
browse_buttons.append(ctk.CTkButton(left_frame, text="Browse", command=lambda: browse_directory(results_entry),
                                    fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white"))

orografia_var = ctk.StringVar()
orografia_dropdown = ctk.CTkOptionMenu(left_frame, variable=orografia_var, values=["complessa", "semplice"])
orografia_dropdown.set("complessa")

labels = [
    "Distanza Angolo WTG:", "Input File CMG:", "Input File Meteo:",
    "Input File Turbine Parameters:", "Directory Risultati:"
]

for i, label in enumerate(labels):
    ctk.CTkLabel(left_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
    file_entries[i].grid(row=i, column=1, padx=5, pady=5)
    browse_buttons[i].grid(row=i, column=2, padx=5, pady=5)

ctk.CTkLabel(left_frame, text="Orografia:").grid(row=5, column=0, padx=5, pady=10, sticky='w')
orografia_dropdown.grid(row=5, column=1, padx=5, pady=10)

generate_button = ctk.CTkButton(left_frame, text="Genera Report", command=generate_report,
                                 fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
generate_button.grid(row=6, column=0, columnspan=3, pady=20)

status_label = ctk.CTkLabel(left_frame, text="")
status_label.grid(row=7, column=0, columnspan=3, pady=10)

# --- DESTRA: Fasi operative e avvertenze ---
fasi_frame = ctk.CTkFrame(right_frame)
fasi_frame.pack(fill='both', expand=True, pady=10)

titolo_fasi = ctk.CTkLabel(fasi_frame, text="Fasi Operative", font=("Helvetica", 18, "bold"))
titolo_fasi.pack(pady=10)

fasi = [
    "1. Import Data",
    "4. Organizzazione dati iniziali",
    "5. Verifica condizioni di attivazione",
    "6. Avvio procedura iterativa",
    "7. Immissione specifica",
    "8. Rumore residuo",
    "9. Procedura Iterativa",
    "10. Espressione dei risultati"
]

for fase in fasi:
    ctk.CTkLabel(fasi_frame, text=fase).pack(anchor='w', padx=10, pady=2)

avvertenze_frame = ctk.CTkFrame(right_frame)
avvertenze_frame.pack(fill='x', pady=20)

titolo_avvertenze = ctk.CTkLabel(avvertenze_frame, text="Avvertenze!", font=("Helvetica", 16, "bold"), text_color="red")
titolo_avvertenze.pack(pady=10)

# Avvia il messaggio di benvenuto all'inizio
root.after(1000, apri_finestra_benvenuto)

root.mainloop()
