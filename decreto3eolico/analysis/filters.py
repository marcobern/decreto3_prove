import pandas as pd


def filtro_durata(T_CMG):
    T_CMG['durata'] = pd.to_timedelta(T_CMG['durata'])
    T_CMG = T_CMG[T_CMG['durata'] >= pd.Timedelta(minutes=5)]
    T_CMG = T_CMG.drop(columns=['durata'])
    return T_CMG


def filtro_missed_data(T_CMG, T_meteo, T_turbine_parameters):
    T_CMG = T_CMG[T_CMG['datetime'].isin(T_meteo['datetime'])]
    T_CMG = T_CMG[T_CMG['datetime'].isin(T_turbine_parameters['datetime'])]
    return T_CMG
