# steps/step_3_validazione_dati.py
import os
from decreto3eolico.analysis import filtro_durata, filtro_missed_data, split_day_night

def step_3_validazione_dati(T_CMG, T_meteo, T_turbine_parameters, ri, theta_i, orografia, metaresults_dir): 
# ri, theta_i e orografia verranno utilizzati nello step successivo

    try:
        T_CMG_filtered_durata = filtro_durata(T_CMG)
        T_CMG_filtered_missed_data = filtro_missed_data(
            T_CMG_filtered_durata, T_meteo, T_turbine_parameters,
        )
        T_CMG = T_CMG_filtered_missed_data

        # split diurno notturno
        T_CMG_diurno, T_CMG_notturno = split_day_night(T_CMG)

        day_night_map = {
            'diurno': {
                "df": T_CMG_diurno,
                "delta": 0.2
            },
            'notturno': {
                "df": T_CMG_notturno,
                "delta": 0.1
            }
        }

        for day_night in day_night_map:
            fp = os.path.join(metaresults_dir, day_night)
            os.makedirs(fp, exist_ok=True)
            day_night_map[day_night]['subpath'] = fp

        return day_night_map

    except Exception as e:
        raise Exception(f"Errore nella validazione dei dati: {e}")
