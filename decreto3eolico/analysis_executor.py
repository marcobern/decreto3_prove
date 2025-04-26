import os
from typing import Literal
import numpy as np
import pandas as pd
from decreto3eolico.documentation import generate_docx
from .analysis import (
    plot_activation_threshold_search, 
    plot_fit_curve,
    Lx_L0_extraction, 
    activation_threshold_extraction,
    load_cmg_data, 
    load_meteo_data, 
    load_turbine_data, 
    load_distanza_angolo_WTG,
    split_day_night,
    filtro_durata, 
    filtro_missed_data,
    crea_tabella_avvio_procedura, 
    crea_tabella_dati_iniziali,
    creazione_tabella_media_energetica, 
    creazione_tabella_occorrenze, 
    creazione_tabella_residuo, 
    crezione_tabella_immissione_specifica,
)


def save_table(table, path, SOGLIA_ATTIVAZIONE=None):
    df = pd.DataFrame(table)
    if SOGLIA_ATTIVAZIONE is not None:
        df.index = [
            "< Attiv." if i == 0 else f"{i-1+SOGLIA_ATTIVAZIONE}" for i in range(len(df))
        ]
        df.to_csv(path)
    else:
        df.to_csv(path, index=False)
    return df


def run_analysis(
    distanza_angolo_WTG: str,
    input_file_CMG: str,
    input_file_meteo: str,
    input_file_turbine_parameters: str,
    orografia: Literal['complessa', 'semplice'],
    resuts_dir: str,
):
    metaresults_dir = os.path.join(resuts_dir, 'metaresults')
    total_entities = []
    os.makedirs(metaresults_dir, exist_ok=True)
    match orografia:
        case 'complessa':
            alpha = 10 ** (-4)
        case 'semplice':
            alpha = 6*10 ** (-5)

    try:
        ri, theta_i = load_distanza_angolo_WTG(distanza_angolo_WTG)
    except Exception as e:
        raise Exception(f"Error loading Distanza Angolo WTG: {e}")

    try:
        T_CMG = load_cmg_data(input_file_CMG)
    except Exception as e:
        raise Exception(f"Error loading CMG data: {e}")
    
    try:
        T_meteo = load_meteo_data(input_file_meteo)
    except Exception as e:
        raise Exception(f"Error loading Meteo data: {e}")
    
    try:
        T_turbine_parameters = load_turbine_data(input_file_turbine_parameters)
    except Exception as e:
        raise Exception(f"Error loading Turbine Parameters data: {e}")

    # 3. VALIDAZIONE DEI DATI [ALLEGATO 3]
    T_CMG_filtered_durata = filtro_durata(T_CMG)
    T_CMG_filtered_missed_data = filtro_missed_data(
        T_CMG_filtered_durata, T_meteo, T_turbine_parameters,)
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
    for day_night in day_night_map.keys():
        fp = os.path.join(metaresults_dir, day_night)
        os.makedirs(fp, exist_ok=True)
        day_night_map[day_night]['subpath'] = fp

    for day_night in day_night_map.keys():
        try:
            entities = []
            delta = day_night_map[day_night]['delta']
            T_CMG = day_night_map[day_night]['df']
            subpath_dir = day_night_map[day_night]['subpath']
            # 4.ORGANIZZAZIONE DEI DATI INIZIALI[ALLEGATO 3](CONVERTIRE IN FUNZIONE PER APPLICARE A DIURNO E NOTTURNO)
            TABELLA_DATI_INIZIALI = crea_tabella_dati_iniziali(
                T_CMG, T_meteo, T_turbine_parameters)
            save_table(
                TABELLA_DATI_INIZIALI,
                os.path.join(subpath_dir, "TABELLA_DATI_INIZIALI.csv"),
            )
            TABELLA_AVVIO_PROCEDURA = crea_tabella_avvio_procedura(
                TABELLA_DATI_INIZIALI, ri, theta_i, delta, alpha)
            save_table(
                TABELLA_AVVIO_PROCEDURA,
                os.path.join(subpath_dir, "TABELLA_AVVIO_PROCEDURA.csv"),
            )

            # 5.VERIFICA DELLE CONDIZIONI DI ATTIVAZIONE DELLA PROCEDURA[ALLEGATO 3](CONVERTIRE IN FUNZIONE PER APPLICARE A DIURNO E NOTTURNO)
            Lx, L_R0 = Lx_L0_extraction(TABELLA_AVVIO_PROCEDURA)
            SOGLIA_ATTIVAZIONE = activation_threshold_extraction(Lx, L_R0)

            fp_act_plot = plot_activation_threshold_search(
                Lx, L_R0, SOGLIA_ATTIVAZIONE, subpath_dir)
            entities.append(
                (f"Activation Threshold Search {day_night}", fp_act_plot))

            """T_out_ATTIVAZIONE = pd.DataFrame()
            T_out_ATTIVAZIONE['Lx'] = Lx
            T_out_ATTIVAZIONE['L_R0'] = [L_R0 for _ in Lx]
            T_out_ATTIVAZIONE['Verifica'] = [
                ("ATTIVAZIONE" if f else "NO") for f in T_out_ATTIVAZIONE.index >= SOGLIA_ATTIVAZIONE]"""

            # 6.AVVIO PROCEDURA ITERATIVA(1): Creazione delle tabelle di calcolo(CONVERTIRE IN FUNZIONE PER APPLICARE A DIURNO E NOTTURNO)
            TABELLA_DELLE_MEDIE_ENERGETICHE = creazione_tabella_media_energetica(
                TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE)
            df_energ = save_table(
                TABELLA_DELLE_MEDIE_ENERGETICHE,
                os.path.join(subpath_dir,
                             "TABELLA_DELLE_MEDIE_ENERGETICHE.csv"),
                SOGLIA_ATTIVAZIONE
            )
            entities.append(
                (f"Mean Energetic Table {day_night}", df_energ))

            TABELLA_DELLE_OCORRENZE = creazione_tabella_occorrenze(
                TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE)
            df_occ = save_table(
                TABELLA_DELLE_OCORRENZE,
                os.path.join(subpath_dir,
                             "TABELLA_DELLE_OCORRENZE.csv"),
                SOGLIA_ATTIVAZIONE
            )
            entities.append(
                (f"Occurrences Table {day_night}", df_occ))

            # 7. AVVIO DELLA PROCEDURA ITERATIVA(2): Tabella di immissione specifica(CONVERTIRE IN FUNZIONE PER APPLICARE A DIURNO E NOTTURNO e NEL PROCESSO ITERATIVO)
            TABELLA_DI_IMMISSIONE_SPECIFICA, LE_x = crezione_tabella_immissione_specifica(
                TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE)

            # 8. AVVIO DELLA PROCEDURA ITERATIVA(2): Tabella dei livelli di rumore residuo(CONVERTIRE IN FUNZIONE PER APPLICARE A DIURNO E NOTTURNO e NEL PROCESSO ITERATIVO)
            TABELLA_RESIDUO, LR_k = creazione_tabella_residuo(
                TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE, LE_x)

            def save_imm_res(desc):
                return [
                    save_table(
                        TABELLA_DI_IMMISSIONE_SPECIFICA,
                        os.path.join(subpath_dir,
                                     f"TABELLA_DI_IMMISSIONE_SPECIFICA_{desc}.csv"),
                        SOGLIA_ATTIVAZIONE
                    ),
                    save_table(
                        TABELLA_RESIDUO,
                        os.path.join(
                            subpath_dir, f"TABELLA_RESIDUO_{desc}.csv"),
                        SOGLIA_ATTIVAZIONE
                    ),
                    save_table(
                        LE_x.reshape(-1, 1),
                        os.path.join(subpath_dir, f"LEx_{desc}.csv"),
                        SOGLIA_ATTIVAZIONE
                    ),
                    save_table(
                        LR_k.reshape(1, -1),
                        os.path.join(subpath_dir, f"LRk_{desc}.csv"),
                    ),
                ]
            save_imm_res('INIZIALE')

            # 9. PROCEDURA ITERATIVA
            LE_cond, LR_cond = True, True
            iter = 0
            while LE_cond or LR_cond:
                # TABELLA_DELLE_MEDIE_ENERGETICHE[0] = LR_k
                print(f'{iter}) LE_x: {(LE_x)} - LR_k: {LR_k}')
                TABELLA_DI_IMMISSIONE_SPECIFICA, LE_x_new = crezione_tabella_immissione_specifica(
                    TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE, LE_x, LR_k_prev=LR_k)
                LE_cond = sum(np.abs(LE_x_new - LE_x) > 0.1) > 0
                LE_x = LE_x_new
                TABELLA_RESIDUO, LR_k_new = creazione_tabella_residuo(
                    TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE, LE_x, LR_k_prev=LR_k)
                LR_cond = sum(np.abs(LR_k_new - LR_k) > 0.1) > 0
                LR_k = LR_k_new
                iter += 1
                save_imm_res(f'ITER={iter}')

            print(f'{iter}) \tLE_x: {LE_x} \tLR_k: {LR_k}')
            dfs_final_tables = save_imm_res('FINALE')
            entities.append(
                (f"Final Immission Table {day_night}", dfs_final_tables[0]))
            entities.append(
                (f"Final Residual Table {day_night}", dfs_final_tables[1]))
            entities.append(
                (f"LE_x {day_night}", dfs_final_tables[2]))
            entities.append(
                (f"LR_k {day_night}", dfs_final_tables[3]))

            # 10. Espressione dei risultati
            fp_fit_curve = plot_fit_curve(LE_x, LR_k, TABELLA_DELLE_OCORRENZE,
                                          SOGLIA_ATTIVAZIONE, subpath_dir)
            entities.append(
                (f"Fit Curve {day_night}", fp_fit_curve))
            total_entities.extend(entities)
        except Exception as e:
            print(f"Error in {day_night}: {e}")
            continue

    report_path = os.path.join(resuts_dir, "generated_report.docx")
    generate_docx(total_entities, report_path)
    return report_path


def main():
    base_dir = "assets/Eolico/Dati Montecatini-Scapiccioli notturno/"
    distanza_angolo_WTG = f"{base_dir}distanza_angolo_WTG.csv"
    input_file_CMG = f"{base_dir}input_file_CMG.csv"
    input_file_meteo = f"{base_dir}input_file_meteo.csv"
    input_file_turbine_parameters = f"{base_dir}input_file_turbine_parameters.csv"
    orografia = 'complessa'
    resuts_dir = f"{base_dir}results/"
    report_path = run_analysis(
        distanza_angolo_WTG,
        input_file_CMG,
        input_file_meteo,
        input_file_turbine_parameters,
        orografia,
        resuts_dir,
    )
    print(f"Report saved at: {report_path}")


if __name__ == '__main__':
    main()
