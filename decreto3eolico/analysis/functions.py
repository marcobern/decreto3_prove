import numpy as np


def Leq_calculation(data: np.array, n: np.array = None):
    if data.shape[0] == 0:
        return 0
    w = n if n is not None else 1
    div = n.sum() if n is not None else len(data)
    return 10 * np.log10((w * 10 ** (0.1 * data)).sum() / div)

def differenza_energetica(v1, v2):
    return 10 * np.log10(10 ** (v1/10) - 10 ** (v2/10))
