import re
import matplotlib.pyplot as plt

#arquivo = 'C:\\Users\\davij\\Desktop\\Facul\\10°Periodo\\Telc2\\14-10-2025 - 01-19-31.txt'  # Substitua pelo caminho do seu arquivo
arquivo = 'C:\\Users\\davij\\Desktop\\Facul\\10°Periodo\\sinDig.txt'

valores = []
linhas_x = []

with open(arquivo, 'r') as f:
    for idx, linha in enumerate(f, start=1):
        match = re.search(r"^([0-9]+)\n", linha)
        if match:
            valores.append(int(match.group(1)))
            linhas_x.append(idx)

plt.plot(linhas_x, valores)
plt.xlabel('Número da linha')
plt.ylabel('Valor ADC')
plt.title('Valores ADC por linha')
plt.grid(True)
plt.show()