import serialRead as sr
import plotTeste as pltt
import decodificador as dec
import conversorAD as cvad

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.25 # 0.25 segundosd
TRIGGER_VALUE = 200  # valor de trigger para salvar
CAPTURE_LENGTH = 8500  # número de amostras a capturar após o trigger

if __name__ == '__main__':
    data, duracao = sr.r_serial(SERIAL_PORT, BAUD_RATE, TRIGGER_VALUE, CAPTURE_LENGTH)
    bin_data = cvad.ad(data)
    fs = 82333  # Hz, valor estimado
    #fs = len(bin_data) / duracao # Hz, valor calculado dinamicamente
    address, command, status, r_edg, f_edg = dec.nec_decoder(bin_data, fs)
    if status == 0:
        print("Decodificação não realizada")
    elif status == 1:
        print("Verificação de comando: falhou")
    elif status == 2:
        print("Verificação de comando: passou")
    elif status == 3:
        print("Aviso: não foram detectados bits suficientes para decodificação")
    print(f"Número de edges de subida: {r_edg}")
    print(f"Número de edges de descida: {f_edg}")
    print(f"Endereço: {hex(address)}, Comando: {hex(command)}")
    #pltt.pltTeste(bin_data)