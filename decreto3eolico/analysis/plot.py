import os
from matplotlib import pyplot as plt
import numpy as np


def plot_activation_threshold_search(Lx, L_R0, SOGLIA_ATTIVAZIONE, resuts_dir):
    plt.figure(figsize=(10, 5))
    x_values = [str(i + 4) for i in range(len(Lx))]
    plt.title('RICERCA SOGLIA DI ATTIVAZIONE')
    plt.plot(x_values, Lx, label='Lx')
    plt.plot(x_values, [L_R0 for _ in Lx], label='L0')
    plt.axvline(x=SOGLIA_ATTIVAZIONE - 4, color='r', label='SOGLIA ATTIVAZIONE')
    plt.xlabel('x [rpm]')
    plt.ylabel('dB(A)')
    plt.grid(True)
    plt.legend()
    # plt.show()
    plt.tight_layout()
    fp = os.path.join(resuts_dir, 'activation_threshold_search.png')
    plt.savefig(fp)
    return fp


def plot_fit_curve(LE_x, LR_k, TABELLA_DELLE_OCORRENZE, SOGLIA_ATTIVAZIONE, resuts_dir):
    mask = np.logical_and(LE_x > min(LR_k) - 10,
                          TABELLA_DELLE_OCORRENZE[1:].sum(axis=1) > 10)
    x = np.array(
        list(range(SOGLIA_ATTIVAZIONE, len(LE_x) + SOGLIA_ATTIVAZIONE)))[mask]
    y = LE_x[mask]

    A, B = np.polyfit(np.log(x), y, 1)
    ylog = A * np.log(x) + B
    W1, W2, W3, B = np.polyfit(x, y, 3)
    ypol = W1 * x ** 3 + W2 * x ** 2 + W3 * x + B

    plt.figure(figsize=(10, 5))
    plt.title('Curva LE,x,fit')
    plt.plot(x, y, label='LE_x')
    plt.plot(x, ylog, label='log')
    plt.plot(x, ypol, label='pol')
    plt.xlabel('NeqTOT [rpm]')
    plt.ylabel('LE [dB(A]')
    plt.grid(True)
    plt.legend()
    # plt.show()
    plt.tight_layout()
    fp = os.path.join(resuts_dir, 'fit_curve.png')
    plt.savefig(fp)
    return fp
    
