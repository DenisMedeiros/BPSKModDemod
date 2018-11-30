#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from simulador import ModuladorQAM, DemoduladorQAM, Canal

# Configurações.

N = 4  # Número de símbolos a ser enviado.
Fc = 200  # Frequência da portadora.
Fs = 4 * Fc  # Frequência de amostragem.
Tb = 0.1  # Largura de cada símbolo (em seg).

SNRdB = 100  # Potência do sinal é duas vezes o dobro da potência do ruído.
SNR = 10.0 ** (SNRdB/10.0)

Fd = 50  # Frequência de Doppler para o canal de múltiplos caminhos.

TAPS = 10  # Número de elementos (caminhos) do canal.

# Cria o modulador.
#
modulador = ModuladorQAM(baud=10, bpb=2, fc=50, fs=1000)
demodulador = DemoduladorQAM(modulador)

(ondaq, sinalm) = modulador.processar('00011011')

(sinald, sinali, ondaq_recebida, simbolos) = demodulador.processar(sinalm)

plt.figure(1)
plt.plot(ondaq)
plt.figure(2)
plt.plot(sinald)
plt.figure(3)
plt.plot(ondaq_recebida)
plt.figure(4)
plt.plot(sinali)
plt.show()


'''

canal = Canal(SNR, TAPS, Fd)

# Dados a serem enviados.
dados = np.random.choice(np.array([0, 1]), size=(N))

# Criando símbols para o BPSK (-1 e 1).
simbolos_enviados = 2*dados - 1

# Modula os símbolos.
(ondaq_enviada, sinalm) = modulador.processar(simbolos_enviados)

# Processa pelo canal.
sinalc = canal.processar(sinalm)

# Demodula o sinal recebido.
(sinald,  sinali, ondaq_recebida, simbolos_recebidos) = demodulador.processar(sinalc)

dados_recebidos = ((simbolos_recebidos + 1)/2).astype(int)

# Calculando os erros de decisão.
num_erros = np.sum(simbolos_enviados != simbolos_recebidos)
BER = num_erros/simbolos_enviados.size

print('Do total de {} bits, {} foram decodificados de formada errada.'.format(
    simbolos_enviados.size, num_erros
))
print('BER: {}'.format(BER))

# Exibindo gráficos do transmissor.
f1, (f1_ax1, f1_ax2, f1_ax3) = plt.subplots(3)
f1.suptitle('Sinal enviado a partir do transmissor', fontsize=14)
f1_ax1.stem(dados)
f1_ax1.set_title('Bits enviados')
f1_ax2.plot(ondaq_enviada)
f1_ax2.set_title('Onda quadrada gerada a partir dos símbolos')
f1_ax3.plot(sinalm)
f1_ax3.set_title('Sinal modulado')
f1.subplots_adjust(hspace=1)

# Exibindo gráficos do receptor.
f2, (f2_ax1, f2_ax2, f2_ax3, f2_ax4, f2_ax5) = plt.subplots(5)
f2.suptitle('Sinal recebido no receptor.', fontsize=14)
f2_ax1.plot(sinalc)
f2_ax1.set_title('Sinal recebido do canal')
f2_ax2.plot(sinald)
f2_ax2.set_title('Sinal demodulado')
f2_ax3.plot(sinali)
f2_ax3.set_title('Sinal após integração')
f2_ax4.plot(ondaq_recebida)
f2_ax4.set_title('Onda quadrada recebida')
f2_ax5.stem(dados_recebidos)
f2_ax5.set_title('Dados recebidos')
f2.subplots_adjust(hspace=1)
plt.show()
'''