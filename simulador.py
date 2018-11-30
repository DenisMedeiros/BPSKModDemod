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

        return (sinald, sinali, ondaq, simbolos)


class Canal:

    def __init__(self, SNR, taps, Fd):
        self.SNR = SNR
        self.taps = taps
        self.Fd = Fd

    def processar(self, sinal):

        # Sinal processado pelo canal, representado por h.
        #h = np.concatenate((np.zeros(5), rayleigh.rvs(size=10)))

        # Canal com desvanecimento (modelo de Jakes), para dist. de Rayleigh.
        M = self.taps
        K = sinal.size
        sinalc = np.zeros(sinal.size)

        for k in np.arange(1, K+1, 1):

            hi = 0.0
            hq = 0.0

            alfa = 2 * np.random.rand() - np.pi
            teta = 2 * np.random.rand() - np.pi
            #beta = 2 * np.random.rand() - np.pi

            for m in np.arange(1, M+1, 1):

                #hi = hi + np.cos(2 * np.pi * self.Fd * np.cos(((2 * m - 1) * np.pi + teta) / (4 * M)) * k + alfa)
                #hq = hq + np.sin(2 * np.pi * self.Fd * np.cos(((2 * m - 1) * np.pi + teta) / (4 * M)) * k + beta)
                hi = hi + np.random.randn() * np.cos(2 * np.pi * self.Fd * k * np.cos(alfa) + teta)
                hq = hq + np.random.randn() * np.sin(2 * np.pi * self.Fd * k * np.cos(alfa) + teta)


            h = np.abs((1 / np.sqrt(M)) * (hi + 1j * hq))
            sinalc[k-1] = sinal[k-1]*h

        '''
        for n in np.arange(0, sinal.size+1, 1):

            alpha = 2*np.random.rand() - np.pi
            phi = 2*np.random.rand() - np.pi

            x = x + np.random.randn()*np.cos(2*pi*fd*np.cos(alpha) + phi)
            y = y + np.random.randn()*np.sin(2 * pi * fd * np.cos(alpha) + phi)
        '''

        # Aplicando ruído gaussiano branco.
        potencia_sinal = np.sum(np.square(sinalc))/sinalc.size

        # Gerando ruído gaussiano branco (média = 0, variancia = potencia do awgn).
        potencia_ruido = potencia_sinal / self.SNR
        desvio_padrao = np.sqrt(potencia_ruido)
        ruido_gaussiano = np.random.normal(0, desvio_padrao, sinalc.size)

        # Aplica o ruído ao sinal.
        sinal_ruidoso = sinalc + ruido_gaussiano

        print(sinal_ruidoso.size)

        # Atenua o sinal.
        return sinal_ruidoso