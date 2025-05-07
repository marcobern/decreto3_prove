# steps_on_gui/gui_step_1_import.py

import customtkinter as ctk
import pandas as pd
import numpy as np
from ..steps.step_1_import import step_import_dati

def run_step_import(self):
    try:
        # Reset avvertenze
        for widget in self.avvertenze_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.avvertenze_frame, text="Avvertenze!", font=("Helvetica", 16, "bold"),
                     text_color="red").pack(pady=10)

        # Prepara input
        files = {
            "distanza_angolo_WTG": self.file1_entry.get(),
            "input_file_CMG": self.file2_entry.get(),
            "input_file_meteo": self.file3_entry.get(),
            "input_file_turbine_parameters": self.file4_entry.get()
        }
        results_dir = self.results_entry.get()

        # Esegui lo step
        outputs = step_import_dati(files, results_dir)

        ctk.CTkLabel(self.avvertenze_frame, text="✅ Importazione dati avvenuta con successo", text_color="green").pack()
        label, frame = self.fasi_labels[0]
        label.configure(text="1. Import Data ✅")

        self.output_tables = outputs
        self.T_CMG = outputs["CMG"]
        self.T_meteo = outputs["Meteo"]
        self.T_turbine = outputs["Turbine"]
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("0.0", ctk.END)

        # Dropdown
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

        self.dropdown_menu = ctk.CTkOptionMenu(frame, values=list(outputs.keys()), command=mostra_tabella)
        self.dropdown_menu.pack(side="left", padx=5)
        
        return outputs

    except Exception as e:
        self.status_label.configure(text="", text_color="red")
        errore_label = ctk.CTkLabel(
            self.avvertenze_frame,
            text="❌ Errore nell'importazione dei dati.\nServirsi della guida per controllare la formattazione dei file importati.",
            text_color="red",
            font=("Helvetica", 12, "bold"),
            justify="left"
        )
        errore_label.pack(pady=10)
        
        return None
