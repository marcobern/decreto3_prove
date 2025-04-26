import numpy as np
from .functions import Leq_calculation
from .utils import round_custom


def Lx_L0_extraction(TABELLA_AVVIO_PROCEDURA):
    tabella_verifica_condizioni_iniziali = TABELLA_AVVIO_PROCEDURA[
        TABELLA_AVVIO_PROCEDURA["Vr [m/s]"] < 2]
    Lx = []
    for i in range(4, int(tabella_verifica_condizioni_iniziali['NeqTOT(arrot.) [rpm]'].max() + 1)):
        T_NeqX = tabella_verifica_condizioni_iniziali[
            tabella_verifica_condizioni_iniziali['NeqTOT(arrot.) [rpm]'] == i]
        Lx_now = Leq_calculation(T_NeqX['LAeq,10min [dB(A)]'].to_numpy())
        Lx_now = round_custom(Lx_now, 1)
        Lx.append(Lx_now)

    tabella_stima_L_R0 = tabella_verifica_condizioni_iniziali[
        tabella_verifica_condizioni_iniziali['NeqTOT(arrot.) [rpm]'] < 4]
    L_R0 = Leq_calculation(tabella_stima_L_R0['LAeq,10min [dB(A)]'])
    L_R0 = round_custom(L_R0, 1)
    return np.array(Lx), L_R0


def activation_threshold_extraction(Lx, L_R0):
    Lx_meno_L_R0 = Lx - L_R0

    SOGLIA_ATTIVAZIONE = None
    stop = False
    i = 0
    while not stop:
        if Lx_meno_L_R0[i] > 2 and Lx_meno_L_R0[i+1] > 2:
            stop = True
            SOGLIA_ATTIVAZIONE = i + 4
        i += 1

    return SOGLIA_ATTIVAZIONE
