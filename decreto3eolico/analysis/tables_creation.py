import numpy as np
import pandas as pd

from .functions import Leq_calculation, differenza_energetica
from .utils import apply_func_to_array, clean_values, round_custom


def crea_tabella_dati_iniziali(T_CMG, T_meteo, T_turbine_parameters):
    TABELLA_DATI_INIZIALI = T_CMG.join(
        T_meteo.set_index('datetime'), on='datetime')
    TABELLA_DATI_INIZIALI = TABELLA_DATI_INIZIALI.join(
        T_turbine_parameters.set_index('datetime'), on='datetime')
    return TABELLA_DATI_INIZIALI


def crea_tabella_avvio_procedura(TABELLA_DATI_INIZIALI, ri, theta_i, delta, alpha):
    m = len(ri)
    r1 = min(ri)
    Ki = 10 ** (alpha * (r1 - ri))
    Ni = TABELLA_DATI_INIZIALI[[f'N{i + 1}' for i in range(m)]].to_numpy()
    Qi = TABELLA_DATI_INIZIALI[[f'Q{i + 1}' for i in range(m)]].to_numpy()

    Ci = 1 + delta * np.cos(np.deg2rad(Qi - theta_i))
    Neq_i = Ni * ((r1 / ri) ** (2 / 5)) * Ki * Ci
    Neq_TOT_tmp = (Neq_i ** 5).sum(axis=1) ** (1 / 5)
    Neq_TOT = [int(round_custom(v)) for v in Neq_TOT_tmp]

    TABELLA_AVVIO_PROCEDURA = pd.DataFrame()
    for key_trg, key_src in [
        ('datetime', 'datetime'),
        ('LAeq,10min [dB(A)]', 'Leq'),
        ('Vr [m/s]', 'windspeed')
    ]:
        TABELLA_AVVIO_PROCEDURA[key_trg] = TABELLA_DATI_INIZIALI[key_src]
    for i in range(m):
        TABELLA_AVVIO_PROCEDURA[f'Neq{i + 1} [rpm]'] = Neq_i[:, i]
    TABELLA_AVVIO_PROCEDURA['NeqTOT(arrot.) [rpm]'] = Neq_TOT

    return TABELLA_AVVIO_PROCEDURA


def selection_wind_speed(TABELLA_DELLE_MEDIE_ENERGETICHE, tabella_x, x_i, callback):
    for k_i in range(6):
        tabella_xk = tabella_x[tabella_x["Vr [m/s]"] == k_i]
        if len(tabella_xk) > 2:
            TABELLA_DELLE_MEDIE_ENERGETICHE[x_i, k_i] = callback(
                tabella_xk["LAeq,10min [dB(A)]"])


def creazione_tabella_procedura_iterativa_n6(TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE, table_type):
    callback = None
    if table_type == 'MEDIA ENERGETICA':
        def callback(x): return round_custom(Leq_calculation(x), 1)
    elif table_type == 'OCCORRENZE':
        def callback(x): return len(x)
    TABELLA_DELLE_MEDIE_ENERGETICHE = np.zeros(
        (TABELLA_AVVIO_PROCEDURA['NeqTOT(arrot.) [rpm]'].max() - SOGLIA_ATTIVAZIONE + 2, 6))

    tabella_sotto_attivazione = TABELLA_AVVIO_PROCEDURA[
        TABELLA_AVVIO_PROCEDURA['NeqTOT(arrot.) [rpm]'] < SOGLIA_ATTIVAZIONE]
    selection_wind_speed(TABELLA_DELLE_MEDIE_ENERGETICHE,
                         tabella_sotto_attivazione, 0, callback)

    for x_i in range(SOGLIA_ATTIVAZIONE, TABELLA_AVVIO_PROCEDURA['NeqTOT(arrot.) [rpm]'].max() + 1):
        tabella_x = TABELLA_AVVIO_PROCEDURA[
            TABELLA_AVVIO_PROCEDURA["NeqTOT(arrot.) [rpm]"] == x_i]
        selection_wind_speed(TABELLA_DELLE_MEDIE_ENERGETICHE,
                             tabella_x, x_i - SOGLIA_ATTIVAZIONE + 1, callback)
    return TABELLA_DELLE_MEDIE_ENERGETICHE


def creazione_tabella_media_energetica(TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE):
    return creazione_tabella_procedura_iterativa_n6(TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE, 'MEDIA ENERGETICA')


def creazione_tabella_occorrenze(TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE):
    return creazione_tabella_procedura_iterativa_n6(TABELLA_AVVIO_PROCEDURA, SOGLIA_ATTIVAZIONE, 'OCCORRENZE')


def crezione_tabella_immissione_specifica(TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE, LE_x_prev=None, LR_k_prev=None):
    if LR_k_prev is None:
        LR_k_prev = TABELLA_DELLE_MEDIE_ENERGETICHE[0]
    TABELLA_DI_IMMISSIONE_SPECIFICA = differenza_energetica(
        TABELLA_DELLE_MEDIE_ENERGETICHE[1:],  LR_k_prev)
    clean_values(TABELLA_DI_IMMISSIONE_SPECIFICA)
    diff = TABELLA_DELLE_MEDIE_ENERGETICHE[1:] - LR_k_prev
    TABELLA_DI_IMMISSIONE_SPECIFICA[diff <= 1] = 0
    TABELLA_DI_IMMISSIONE_SPECIFICA = TABELLA_DI_IMMISSIONE_SPECIFICA * \
        (LR_k_prev > 0)

    if LE_x_prev is not None:
        cond = np.logical_and(np.abs(
            TABELLA_DI_IMMISSIONE_SPECIFICA - LE_x_prev.reshape(-1, 1)) > 7, LE_x_prev.reshape(-1, 1) > 0)
        cond = np.logical_and(TABELLA_DI_IMMISSIONE_SPECIFICA > 0, cond)
        for i in range(TABELLA_DI_IMMISSIONE_SPECIFICA.shape[1]):
            filt = cond[:, i]
            TABELLA_DI_IMMISSIONE_SPECIFICA[:, i][filt] = LE_x_prev[filt]

    TABELLA_DI_IMMISSIONE_SPECIFICA = apply_func_to_array(
        TABELLA_DI_IMMISSIONE_SPECIFICA, round_custom, dec=1)

    LE_x = np.array([Leq_calculation(row_e[row_e > 0], n=row_o[row_e > 0])
                    for row_e, row_o in zip(TABELLA_DI_IMMISSIONE_SPECIFICA, TABELLA_DELLE_OCORRENZE[1:])])
    clean_values(LE_x)
    LE_x = apply_func_to_array(LE_x, round_custom, dec=1)

    return TABELLA_DI_IMMISSIONE_SPECIFICA, LE_x


def creazione_tabella_residuo(TABELLA_DELLE_MEDIE_ENERGETICHE, TABELLA_DELLE_OCORRENZE, LE_x, LR_k_prev=None):
    if LR_k_prev is None:
        LR_k_prev = TABELLA_DELLE_MEDIE_ENERGETICHE[0]
    TABELLA_RESIDUO = differenza_energetica(
        TABELLA_DELLE_MEDIE_ENERGETICHE[1:], LE_x.reshape(-1, 1))
    clean_values(TABELLA_RESIDUO)

    diff = TABELLA_DELLE_MEDIE_ENERGETICHE[1:] - LE_x.reshape(-1, 1)
    TABELLA_RESIDUO[diff < 1] = 0
    TABELLA_RESIDUO = np.concatenate(
        (np.array([LR_k_prev]), TABELLA_RESIDUO), axis=0)

    cond = np.logical_and(
        np.abs(TABELLA_RESIDUO - LR_k_prev) > 7, LR_k_prev > 0)
    cond = np.logical_and(TABELLA_RESIDUO > 0, cond)
    for i in range(TABELLA_RESIDUO.shape[0]):
        TABELLA_RESIDUO[i][cond[i]] = LR_k_prev[cond[i]]
    TABELLA_RESIDUO[1:][LE_x == 0, :] = 0
    TABELLA_RESIDUO = apply_func_to_array(TABELLA_RESIDUO, round_custom, dec=1)

    LR_k = np.array([Leq_calculation(
        row_r[row_r > 0], n=row_o[row_r > 0]) for row_r, row_o in zip(TABELLA_RESIDUO.T, TABELLA_DELLE_OCORRENZE.T)])
    clean_values(LR_k)
    LR_k = apply_func_to_array(LR_k, round_custom, dec=1)

    return TABELLA_RESIDUO, LR_k
