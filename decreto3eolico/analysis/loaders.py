import pandas as pd

from .utils import round_custom

DATETIME_DATA = '%d/%m/%Y %H:%M'


def load_cmg_data(input_file_read):
    T_CMG = pd.read_csv(input_file_read, sep=',')
    T_CMG = T_CMG.rename(columns={
        "datetime ": "datetime",
        "Leq": "Leq",
        "duration": "durata",
    })
    T_CMG['datetime'] = pd.to_datetime(
        T_CMG['datetime'], format=DATETIME_DATA
    )

    return T_CMG


def load_meteo_data(input_file_read):
    T_meteo = pd.read_csv(input_file_read, sep=',')

    T_meteo['datetime'] = pd.to_datetime(
        T_meteo['datetime'], format=DATETIME_DATA
    )
    T_meteo = T_meteo[['datetime', 'windspeed']]
    T_meteo['datetime'] = T_meteo['datetime']  # - pd.Timedelta(minutes=10)
    T_meteo['windspeed'] = T_meteo['windspeed'].apply(
        lambda x: round_custom(x))
    return T_meteo


def load_turbine_data(input_file_read):
    T_turbine_parameters = pd.read_csv(input_file_read, sep=',')
    s = T_turbine_parameters.shape[1]

    f = (s - 1) // 2
    var_names = ['datetime']

    for i in range(1, f + 1):
        var_names.append(f'N{i}')
    for i in range(1, f + 1):
        var_names.append(f'Q{i}')

    T_turbine_parameters.columns = var_names
    T_turbine_parameters['datetime'] = pd.to_datetime(
        T_turbine_parameters['datetime'], format=DATETIME_DATA,
    )
    return T_turbine_parameters


def load_distanza_angolo_WTG(input_file_read):
    T_distanza_angolo_WTG = pd.read_csv(input_file_read, sep=',')
    ri = T_distanza_angolo_WTG['r'].to_numpy()
    theta_i = T_distanza_angolo_WTG['theta'].to_numpy()
    return ri, theta_i
