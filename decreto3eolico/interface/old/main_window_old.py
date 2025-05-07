import customtkinter as ctk
import os
from tkinter import filedialog
from decreto3eolico.analysis_executor import run_analysis

# Configura CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colori personalizzati
BOTTONI_FG = "#006400"
BOTTONI_HOVER = "#228B22"


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Decreto3 Eolico Report Generator")
        self.geometry("1200x700")

        self.build_interface()

    def build_interface(self):
        # Frame principali
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True)

        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        top_buttons_frame = ctk.CTkFrame(self)
        top_buttons_frame.pack(side='top', fill='x', pady=10)

        self.guida_button = ctk.CTkButton(top_buttons_frame, text="Guida", command=self.apri_finestra_benvenuto,
                                          fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.guida_button.pack(side='right', padx=10)

        self.pdf_button = ctk.CTkButton(top_buttons_frame, text="Apri Decreto", command=self.apri_pdf_decreto,
                                        fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.pdf_button.pack(side='right', padx=10)

        # Sinistra: form di input
        self.file1_entry = ctk.CTkEntry(left_frame, width=400)
        self.file2_entry = ctk.CTkEntry(left_frame, width=400)
        self.file3_entry = ctk.CTkEntry(left_frame, width=400)
        self.file4_entry = ctk.CTkEntry(left_frame, width=400)
        self.results_entry = ctk.CTkEntry(left_frame, width=400)

        self.file_entries = [self.file1_entry, self.file2_entry, self.file3_entry, self.file4_entry, self.results_entry]

        browse_buttons = [
            ctk.CTkButton(left_frame, text="Browse", command=lambda e=entry: self.browse_file(e),
                          fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
            for entry in self.file_entries[:-1]
        ]
        browse_buttons.append(ctk.CTkButton(left_frame, text="Browse", command=lambda: self.browse_directory(self.results_entry),
                                            fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white"))

        self.orografia_var = ctk.StringVar()
        orografia_dropdown = ctk.CTkOptionMenu(left_frame, variable=self.orografia_var, values=["complessa", "semplice"])
        self.orografia_var.set("complessa")

        labels = [
            "Distanza Angolo WTG:", "Input File CMG:", "Input File Meteo:",
            "Input File Turbine Parameters:", "Directory Risultati:"
        ]

        for i, label in enumerate(labels):
            ctk.CTkLabel(left_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            self.file_entries[i].grid(row=i, column=1, padx=5, pady=5)
            browse_buttons[i].grid(row=i, column=2, padx=5, pady=5)

        ctk.CTkLabel(left_frame, text="Orografia:").grid(row=5, column=0, padx=5, pady=10, sticky='w')
        orografia_dropdown.grid(row=5, column=1, padx=5, pady=10)

        self.generate_button = ctk.CTkButton(left_frame, text="Genera Report", command=self.generate_report,
                                             fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.generate_button.grid(row=6, column=0, columnspan=3, pady=20)

        self.status_label = ctk.CTkLabel(left_frame, text="")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)

        # Destra: Fasi operative e avvertenze
        fasi_frame = ctk.CTkFrame(right_frame)
        fasi_frame.pack(fill='both', expand=True, pady=10)

        ctk.CTkLabel(fasi_frame, text="Fasi Operative", font=("Helvetica", 18, "bold")).pack(pady=10)

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

        ctk.CTkLabel(avvertenze_frame, text="Avvertenze!", font=("Helvetica", 16, "bold"), text_color="red").pack(pady=10)

        self.after(1000, self.apri_finestra_benvenuto)

    def browse_file(self, entry_widget):
        filename = filedialog.askopenfilename()
        if filename:
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, filename)

    def browse_directory(self, entry_widget):
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, directory)

    def generate_report(self):
        files = {
            "distanza_angolo_WTG": self.file1_entry.get(),
            "input_file_CMG": self.file2_entry.get(),
            "input_file_meteo": self.file3_entry.get(),
            "input_file_turbine_parameters": self.file4_entry.get()
        }
        orografia_choice = self.orografia_var.get()
        results_dir = self.results_entry.get()

        if not all(files.values()) or not results_dir:
            self.status_label.configure(text="Errore: Seleziona tutti i file e la directory di output", text_color="red")
            return

        self.status_label.configure(text="Analisi in corso...", text_color="yellow")
        self.update_idletasks()

        try:
            run_analysis(
                files["distanza_angolo_WTG"],
                files["input_file_CMG"],
                files["input_file_meteo"],
                files["input_file_turbine_parameters"],
                orografia_choice,
                results_dir,
            )
            self.status_label.configure(text="Analisi completata con successo!", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Errore durante l'analisi: {e}", text_color="red")

        for entry in self.file_entries:
            entry.delete(0, ctk.END)

    def apri_finestra_benvenuto(self):
        finestra = ctk.CTkToplevel(self)
        finestra.title("Benvenuto - Procedura")
        finestra.geometry("600x400")
        finestra.resizable(False, False)

        testo = ("Passaggi principali dell'algoritmo:\n\n"
                 "1. Caricamento dei dati fonometrici e meteorologici\n"
                 "2. Caricamento dei parametri delle turbine\n"
                 "3. Validazione e filtraggio dei dati\n"
                 "4. Organizzazione dei dati iniziali\n"
                 "5. Verifica condizioni attivazione procedura\n"
                 "6. Avvio procedura iterativa\n"
                 "7. Immissione specifica\n"
                 "8. Rumore residuo\n"
                 "9. Procedura iterativa\n"
                 "10. Espressione dei risultati")

        label = ctk.CTkLabel(finestra, text=testo, justify="left")
        label.pack(expand=True, fill='both', padx=20, pady=20)

        ctk.CTkButton(finestra, text="Chiudi", command=finestra.destroy,
                      fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white").pack(pady=10)

    def apri_pdf_decreto(self):
        try:
            pdf_path = os.path.join(os.getcwd(), "decreto_allegato3.pdf")
            os.startfile(pdf_path)
        except Exception as e:
            self.status_label.configure(text=f"Errore apertura PDF: {e}", text_color="red")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()