import numpy as np
import scipy
import matplotlib.pyplot as plt

# Configuração do modulador.


class Modulador:

    def __init__(self, Fc, Fs, Tb):
        self.Fc = Fc
        self.Fs = Fs
        self.Ts = 1/Fs
        self.Tb = Tb  # Largura de cada símbolo.
        self.L = Tb * Fs  # Número de amostras para o tempo de cada símbolo.

    def processar(self, simbolos):
        # Gera a onda quadrada (cada Tb dura L amostras).
        ondaq = np.repeat(simbolos, self.L)

        # Gera a portadora.
        t = np.linspace(0, ondaq.size, ondaq.size)
        portadora = np.cos(2 * np.pi * self.Fc * t)
        sinalm = np.multiply(ondaq, portadora)

        return (ondaq, sinalm)


class Demodulador:

    def __init__(self, modulador):
        self.modulador = modulador

    def processar(self, sinalm):

        # Estágio 1

        # Gera a portadora.
        t = np.linspace(0, sinalm.size, sinalm.size)
        portadora = np.cos(2 * np.pi * self.modulador.Fc * t)
        sinald = np.multiply(sinalm, portadora)

        # Estágio 2 (decisor)

        ondaq = sinald.copy()

        # Decide se é 1 ou -1 baseado no limiar 0.
        positivos = (sinald > 0)
        negativos = np.logical_not(positivos)

        ondaq[positivos] = 1
        ondaq[negativos] = -1

        # Faz uma subamostragem para obter os símbolos (ignorando o atraso).
        simbolos = ondaq[::self.modulador.L]
        
        return (sinald, ondaq, simbolos.astype(int))


class Canal:

    def __init__(self, SNR):
        self.SNR = SNR

    def processar(self, sinal):

        # Aplicando ruído gaussiano branco.
        potencia_sinal = np.sum(np.square(sinal))/sinal.size

        # Gerando ruído gaussiano branco (média = 0, variancia = potencia do awgn).
        potencia_ruido = potencia_sinal / self.SNR
        desvio_padrao = np.sqrt(potencia_ruido)
        ruido_gaussiano = np.random.normal(0, desvio_padrao, sinal.size)

        # Aplica o ruído ao sinal.
        sinal_ruidoso = sinal + ruido_gaussiano

        # Atenua o sinal.
        return sinal_ruidoso