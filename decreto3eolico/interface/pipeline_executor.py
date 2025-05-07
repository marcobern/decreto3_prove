import os
import pandas as pd
import numpy as np

from decreto3eolico.interface.steps_on_gui.gui_step_1_import import run_step_import
from decreto3eolico.interface.steps_on_gui.gui_step_3_validazione_dati import run_step_3_validazione


def run_full_pipeline(app):
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

        run_step_3_validazione(app, T_CMG, T_meteo, T_turbine, outputs["Distanza/Angolo WTG"], outputs["Theta WTG"], app.orografia_var.get(), metaresults_dir)

    except Exception as e:
        from customtkinter import CTkLabel
        CTkLabel(app.avvertenze_frame,
                 text=f"❌ Errore nella pipeline: {e}",
                 text_color="red").pack(pady=10)
