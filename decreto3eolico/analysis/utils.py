import math

import numpy as np


def split_day_night(T_CMG):
    T_CMG_diurno = T_CMG[(T_CMG['datetime'].dt.hour >= 6) & (T_CMG['datetime'].dt.hour < 22)]
    T_CMG_notturno = T_CMG[(T_CMG['datetime'].dt.hour >= 22) | (T_CMG['datetime'].dt.hour < 6)]
    return T_CMG_diurno, T_CMG_notturno
    

def round_custom(n, dec=0):
    mul = 10 ** dec
    ref = int(n * (mul)) / mul
    comp = 10 ** (- dec - 1) * 5
    diff = n - ref
    if np.abs(diff - comp) < 1e-10:
        return math.ceil(n * mul) / (mul)
    return round(n, dec)


def apply_func_to_array(array: np.ndarray, func, *args, **kwargs):
    shape = array.shape
    array = np.array([func(v, *args, **kwargs) for v in array.reshape(-1)])
    return array.reshape(*shape)
    

def clean_values(array):
    array[np.isnan(array)] = 0
    array[np.abs(array) == np.inf] = 0
