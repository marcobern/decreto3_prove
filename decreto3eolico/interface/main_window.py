import customtkinter as ctk
import os
import pandas as pd
import numpy as np
from tkinter import filedialog
from decreto3eolico.interface.steps_on_gui.gui_step_1_import import run_step_import

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BOTTONI_FG = "#006400"
BOTTONI_HOVER = "#228B22"

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Decreto3 Eolico Report Generator")
        self.geometry("1500x900")
        self.fasi_labels = []
        self.fasi_buttons = []
        self.output_tables = {}
        self.dropdown_menu = None
        self.build_interface()

    def build_interface(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True)

        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        bottom_output_frame = ctk.CTkFrame(left_frame)
        bottom_output_frame.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        left_frame.grid_rowconfigure(8, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)

        # Scrollable textbox for output
        self.output_textbox = ctk.CTkTextbox(bottom_output_frame, height=300, wrap="none")
        self.output_textbox.pack(fill="both", expand=True)
        self.output_textbox.configure(fg_color="white", text_color="black", font=("Courier", 12))


        top_buttons_frame = ctk.CTkFrame(self)
        top_buttons_frame.pack(side='top', fill='x', pady=10)

        self.guida_button = ctk.CTkButton(top_buttons_frame, text="Guida", command=self.apri_finestra_benvenuto,
                                          fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.guida_button.pack(side='right', padx=10)

        self.pdf_button = ctk.CTkButton(top_buttons_frame, text="Apri Decreto", command=self.apri_pdf_decreto,
                                        fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.pdf_button.pack(side='right', padx=10)

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

        self.generate_button = ctk.CTkButton(left_frame, text="Genera Report", command=lambda: run_step_import(self),
                                             fg_color=BOTTONI_FG, hover_color=BOTTONI_HOVER, text_color="white")
        self.generate_button.grid(row=6, column=0, columnspan=3, pady=20)

        self.status_label = ctk.CTkLabel(left_frame, text="")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)

        fasi_frame = ctk.CTkFrame(right_frame)
        fasi_frame.pack(fill='both', expand=True, pady=10)

        ctk.CTkLabel(fasi_frame, text="Fasi Operative", font=("Helvetica", 18, "bold")).pack(pady=10)

        fasi = [
            "1. Import data",

            "2. Tempi di misura",
            "3. Validazione dati", 
            "4. Organizzazione dati iniziali",
            "5. Verifica condizioni di attivazione",
            "6. Avvio procedura iterativa",
            "7. Immissione specifica",
            "8. Rumore residuo",
            "9. Procedura Iterativa",
            "10. Espressione dei risultati"
        ]

        for fase in fasi:
            frame = ctk.CTkFrame(fasi_frame)
            frame.pack(fill='x', padx=10, pady=2)
            label = ctk.CTkLabel(frame, text=fase)
            label.pack(side='left')
            self.fasi_labels.append((label, frame))

        self.avvertenze_frame = ctk.CTkFrame(right_frame)
        self.avvertenze_frame.pack(fill='x', pady=20)

        ctk.CTkLabel(self.avvertenze_frame, text="Avvertenze!", font=("Helvetica", 16, "bold"), text_color="red").pack(pady=10)

        

    def run_step_import(self):
        try:
            # Cancella le avvertenze precedenti
            for widget in self.avvertenze_frame.winfo_children():
                widget.destroy()

            # Reinserisci il titolo "Avvertenze!"
            ctk.CTkLabel(self.avvertenze_frame, text="Avvertenze!", font=("Helvetica", 16, "bold"), text_color="red").pack(pady=10)
            
            files = {
                "distanza_angolo_WTG": self.file1_entry.get(),
                "input_file_CMG": self.file2_entry.get(),
                "input_file_meteo": self.file3_entry.get(),
                "input_file_turbine_parameters": self.file4_entry.get()
            }
            results_dir = self.results_entry.get()

            outputs = step_import_dati(files, results_dir)

            msg_label = ctk.CTkLabel(self.avvertenze_frame, text="✅ Importazione dati avvenuta con successo", text_color="green")
            msg_label.pack()

            label, frame = self.fasi_labels[0]
            label.configure(text="1. Import Data ✅")

            # Salva output completo
            self.output_tables = outputs

            self.output_textbox.configure(state="normal")
            self.output_textbox.delete("0.0", ctk.END)

            # Dropdown per la selezione
            if self.dropdown_menu:
                self.dropdown_menu.destroy()

            def mostra_tabella(scelta):
                self.output_textbox.configure(state="normal")
                self.output_textbox.delete("0.0", ctk.END)

                tabella = self.output_tables[scelta]
                if isinstance(tabella, pd.DataFrame):
                    testo = f"=== {scelta} ===\n\n{tabella.round(1).to_string(index=False)}"
                elif isinstance(tabella, np.ndarray):
                    testo = f"=== {scelta} ===\n\n{np.round(tabella, 1)}"
                else:
                    testo = f"=== {scelta} ===\n\n{str(tabella)}"

                self.output_textbox.insert("0.0", testo)
                self.output_textbox.configure(state="disabled")
            # Posiziona dropdown accanto a "Import Data ✅"
            label, frame = self.fasi_labels[0]
            self.dropdown_menu = ctk.CTkOptionMenu(frame, values=list(outputs.keys()), command=mostra_tabella)
            self.dropdown_menu.pack(side="left", padx=5)


        except Exception as e:
            self.status_label.configure(text="", text_color="red")
            errore_label = ctk.CTkLabel(
                self.avvertenze_frame,
                text="❌ Errore nell'importazione dei dati.\nServirsi della guida per controllare la formattazione dei file .csv importati.",
                text_color="red",
                font=("Helvetica", 12, "bold"),
                justify="left"
            )
            errore_label.pack(pady=10)

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

        finestra.attributes('-topmost', True)  # forza sopra tutto
        finestra.focus_force()       # forza il focus


    def apri_pdf_decreto(self):
        try:
            pdf_path = os.path.join(os.getcwd(), "decreto_allegato3.pdf")
            os.startfile(pdf_path)
        except Exception as e:
            self.status_label.configure(text=f"Errore apertura PDF: {e}", text_color="red")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()