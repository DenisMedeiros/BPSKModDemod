import numpy as np
from scipy.stats import rayleigh

# Configuração do modulador.


class Modulador:

    def __init__(self, Fc, Fs, Tb):
        self.Fc = Fc
        self.Fs = Fs
        self.Ts = 1/Fs
        self.Tb = Tb  # Largura de cada símbolo.
        self.L = int(Tb * Fs)  # Número de amostras para o tempo de cada símbolo.

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

        # Integra para melhorar o formato da onda (opcional).
        sinali = np.convolve(sinald, np.ones(self.modulador.L))

        # Remove o atraso de self.modulador.L - 1 amostras.
        sinali = sinali[int(self.modulador.L) - 1::]

        # Estágio 2 (decisor)

        # Decide se é 1 ou -1 baseado no limiar 0.
        positivos = (sinali > 0)
        negativos = np.logical_not(positivos)

        ondaq = np.empty(sinali.size)
        ondaq[positivos] = 1
        ondaq[negativos] = -1

        # Faz uma subamostragem para obter os símbolos.
        simbolos = ondaq[::self.modulador.L]

        return (sinald, sinali, ondaq, simbolos.astype(int))


class Canal:

    def __init__(self, SNR):
        self.SNR = SNR

    def processar(self, sinal):

        # Sinal processado pelo canal, representado por h.
        #h = np.concatenate((np.zeros(5), rayleigh.rvs(size=10)))
        h = np.array([1])
        sinalc = np.convolve(sinal, h)

        # Aplicando ruído gaussiano branco.
        potencia_sinal = np.sum(np.square(sinalc))/sinalc.size

        # Gerando ruído gaussiano branco (média = 0, variancia = potencia do awgn).
        potencia_ruido = potencia_sinal / self.SNR
        desvio_padrao = np.sqrt(potencia_ruido)
        ruido_gaussiano = np.random.normal(0, desvio_padrao, sinalc.size)

        # Aplica o ruído ao sinal.
        sinal_ruidoso = sinalc + ruido_gaussiano

        # Atenua o sinal.
        return sinal_ruidoso