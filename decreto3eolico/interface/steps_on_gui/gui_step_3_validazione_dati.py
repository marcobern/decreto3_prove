# interface/steps_on_gui/gui_step_3_validazione_dati.py
import customtkinter as ctk
from ..steps.step_3_validazione_dati import step_3_validazione_dati

def run_step_3_validazione(main_window, T_CMG, T_meteo, T_turbine, ri, theta_i, orografia, metaresults_dir):
    print("[DEBUG] Esecuzione run_step_3_validazione avviata")
    for widget in main_window.avvertenze_frame.winfo_children()[1:]:
        widget.destroy()

    try:
        print("[DEBUG] Dentro try di run_step_3_validazione")
        day_night_map = step_3_validazione_dati(
            T_CMG, T_meteo, T_turbine, ri, theta_i, orografia, metaresults_dir
        )

        label, frame = main_window.fasi_labels[2]
        label.configure(text="3. Validazione dei dati ✅")

        ctk.CTkLabel(
            main_window.avvertenze_frame,
            text="✅ Validazione dati completata con successo",
            text_color="green"
        ).pack(pady=10)

        return day_night_map

    except Exception as e:
        print("[DEBUG] Errore in run_step_3_validazione:", e)
        label, frame = main_window.fasi_labels[2]
        label.configure(text="3. Validazione dei dati ❌")

        ctk.CTkLabel(
            main_window.avvertenze_frame,
            text=f"❌ Errore nella validazione dei dati:\n{e}",
            text_color="red"
        ).pack()
        return None
