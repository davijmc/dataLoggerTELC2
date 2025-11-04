import re
import matplotlib.pyplot as plt

#arquivo = 'C:\\Users\\davij\\Desktop\\Facul\\10°Periodo\\Telc2\\14-10-2025 - 01-19-31.txt'  # Substitua pelo caminho do seu arquivo
def pltTeste(data):
    valores = []
    linhas_x = list(range(1, len(data) + 1))
    valores = data


    plt.plot(linhas_x, valores)
    plt.xlabel('Número da linha')
    plt.ylabel('Valor ADC')
    plt.title('Valores ADC por linha')
    plt.grid(True)
    plt.show()