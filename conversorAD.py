import statistics

# Constante para comparação (será calculada como média dos extremos)
separador = 0

# Lê os dados do arquivo
with open('C:\\Users\\davij\\Desktop\\Facul\\10°Periodo\\Telc2\\codigosOficiais\\teste.txt', 'r') as arquivo:
    dados = [float(linha.strip()) for linha in arquivo if linha.strip()]

# Ordena os dados
dados_ordenados = sorted(dados)

# Calcula a média dos 5 menores e 5 maiores valores
cinco_menores = dados_ordenados[:5]
cinco_maiores = dados_ordenados[-5:]
separador = statistics.mean(cinco_menores + cinco_maiores)
separador = 200

# Converte os dados: maior que média -> 0, menor ou igual -> 1
dados_digitais = ['0\n' if valor > separador else '1\n' for valor in dados]

# Escreve os dados digitalizados no arquivo de saída
with open('sinDig.txt', 'w') as arquivo_saida:
    arquivo_saida.writelines(dados_digitais)

print(f"Processamento concluído. Média dos extremos (separador): {separador}")