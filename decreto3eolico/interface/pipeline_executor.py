import os
import pandas as pd
import numpy as np

from decreto3eolico.interface.steps_on_gui.gui_step_1_import import run_step_import
from decreto3eolico.interface.steps_on_gui.gui_step_3_validazione_dati import run_step_3_validazione


def run_full_pipeline(app):
    # Svuota tutte le avvertenze (ma solo all'inizio della pipeline!)
    for widget in app.avvertenze_frame.winfo_children()[1:]:
        widget.destroy()
    from customtkinter import CTkLabel
    # Svuota tutte le avvertenze tranne la prima "Avvertenze!"
    if not app.avvertenze_frame.winfo_children():
        from customtkinter import CTkLabel
        CTkLabel(app.avvertenze_frame,
            text="Avvertenze!", font=("Helvetica", 16, "bold"),
            text_color="red").pack(pady=10)
    else:
        for widget in app.avvertenze_frame.winfo_children()[1:]:
            widget.destroy()

    try:
        # STEP 1 - Import Data
        outputs = run_step_import(app)
        if outputs is None:
            return  # Import fallito, interrompi

        app.output_tables = outputs

        # Estrai le tabelle necessarie dai dati importati
        T_CMG = outputs.get("CMG")
        T_meteo = outputs.get("Meteo")
        T_turbine = outputs.get("Turbine")

        app.T_CMG = T_CMG
        app.T_meteo = T_meteo
        app.T_turbine = T_turbine

        # STEP 3 - Validazione dei dati
        results_dir = app.results_entry.get()
        metaresults_dir = os.path.join(results_dir, "metaresults")
        os.makedirs(metaresults_dir, exist_ok=True)

        run_step_3_validazione(app, T_CMG, T_meteo, T_turbine,
                               outputs["Distanza/Angolo WTG"],
                               outputs["Theta WTG"],
                               app.orografia_var.get(),
                               metaresults_dir)

    except Exception as e:
        CTkLabel(app.avvertenze_frame,
                 text=f"❌ Errore nella pipeline: {e}",
                 text_color="red").pack(pady=10)
