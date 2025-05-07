# steps/step_1_import.py

from decreto3eolico.analysis.loaders import (
    load_distanza_angolo_WTG,
    load_cmg_data,
    load_meteo_data,
    load_turbine_data
)

def step_import_dati(paths: dict, results_dir: str) -> dict:
    """
    Step 1 - Caricamento dati da file.
    """
    try:
        ri, theta_i = load_distanza_angolo_WTG(paths['distanza_angolo_WTG'])
        T_CMG = load_cmg_data(paths['input_file_CMG'])
        T_meteo = load_meteo_data(paths['input_file_meteo'])
        T_turbine = load_turbine_data(paths['input_file_turbine_parameters'])

        return {
            "Distanza/Angolo WTG": ri,
            "Theta WTG": theta_i,
            "CMG": T_CMG,
            "Meteo": T_meteo,
            "Turbine": T_turbine
        }

    except Exception as e:
        raise Exception(f"Errore nella fase 'Import Dati': {e}")
