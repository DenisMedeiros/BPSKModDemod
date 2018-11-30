import numpy as np
from scipy.stats import rayleigh
import matplotlib.pyplot as plt
# Configuração do modulador.

class ModuladorQAM:

    def __init__(self, baud, bpb, fc, fs):
        self.baud = baud
        self.bpb = bpb  # Bits per baud
        self.fc = fc
        self.fs = fs
        self.ts = 1/fs

        # Calcula o tempo de cada símbolo (em segundos)
        self.t_simbol = 1.0/self.baud

        # Número de amostras para cada pulso.
        self.num_amostras = int(self.t_simbol * self.fs)

        # 2 amplitudes e duas fases
        self.simbolos = {
            '00': -3.0/3,
            '01': -1.0/3,
            '11':  1.0/3,
            '10':  3.0/3,
        }

    def processar(self, simbolos):

        # Se simbolos não é par, descarta o último bit.
        num_simbolos = len(simbolos)

        if num_simbolos % 2 != 0:
            simbolos = simbolos[:-1:]
            num_simbolos -= 1

        # Cria a onda discreta a ser multiplicada pela portadora.
        ondad = np.empty(self.num_amostras * num_simbolos)

        # Cria os valores de amplitude dos símbolos.
        num_amps = int(num_simbolos/self.bpb)
        amps = np.empty(num_amps)

        for i in np.arange(0, num_simbolos, self.bpb):
            par = simbolos[i:i + 2:1]
            amps[i >> 1] = self.simbolos[par]

        # Gera a onda quadrada.
        ondaq = np.repeat(amps, self.num_amostras)

        # Gera a portadora.
        t = np.linspace(0, ondaq.size*self.ts, ondaq.size)
        portadora = np.cos(2 * np.pi * self.fc * t)

        # Modula o sinal.
        sinalm = np.multiply(ondaq, portadora)

        return (ondaq, sinalm)


class DemoduladorQAM:

    def __init__(self, modulador):
        self.modulador = modulador

    def processar(self, sinalm):

        # Estágio 1

        # Gera a portadora.
        t = np.linspace(0, sinalm.size * self.modulador.ts, sinalm.size)
        portadora = np.cos(2 * np.pi * self.modulador.fc * t)

        # Demodula o sinal.
        sinald = np.multiply(sinalm, portadora)

        # Integra para melhorar o formato da onda (opcional).
        sinali = (2/self.modulador.num_amostras) * np.convolve(sinald, np.ones(self.modulador.num_amostras))

        # Remove o atraso de self.modulador.L - 1 amostras.
        sinali = sinali[self.modulador.num_amostras - 1::]

        # Estágio 2 (decisor)

        # Decisor (decide o símbolo).
        simb1 = sinali < -0.3333
        simb2 = np.logical_and(sinali > -0.3333, sinali <= 0.33333)
        simb3 = np.logical_and(sinali > 0.0, sinali <= 0.5)
        simb4 = sinali > 0.5

        ondaq = np.empty(sinali.size)

        ondaq[simb1] = -0.75
        ondaq[simb2] = -0.25
        ondaq[simb3] = 0.25
        ondaq[simb4] = 0.75

        simbolos = ondaq[::self.modulador.num_amostras]

        return (sinald, sinali, ondaq, simbolos)







        ondaq = np.empty(sinali.size)
        ondaq[positivos] = 1
        ondaq[negativos] = -1

        # Faz uma subamostragem para obter os símbolos.
        simbolos = ondaq[::self.modulador.L]

        return (sinald, sinali, ondaq, simbolos)


class ModuladorPSK:

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


class DemoduladorPSK:

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
            beta = 2 * np.random.rand() - np.pi

            for m in np.arange(1, M+1, 1):

                hi = hi + np.random.randn() * np.cos(2 * np.pi * self.Fd * k * np.cos(alfa) + teta)
                hq = hq + np.random.randn() * np.sin(2 * np.pi * self.Fd * k * np.cos(alfa) + beta)

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