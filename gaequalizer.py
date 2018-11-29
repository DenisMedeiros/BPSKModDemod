#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy import signal
from random import random

import matplotlib.pyplot as plt

## Dados a serem enviados.

# Sequência de bits.
data = np.random.choice(np.array([-1, 1]), size=(1, 3))

# Convertendo para onda quadrada.
tp = np.arange(0, T*M, Ts)

## Parâmetros da onda portadora.

# Frequência da portadora.
f = 1000
T = 1/f
# Frequência de amostragem da portadora (pelo menos a freq. de Nyquist).
Fs = 100 * f
Ts = 1/Fs

M = 10
n = M * data.size
t = np.arange(0, n*T, Ts)
carrier = np.cos(2*np.pi*f*t)

plt.plot(carrier)
plt.show()


