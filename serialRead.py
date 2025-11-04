import serial
import time
from datetime import datetime
import plotTeste as pltTeste
import decodificador as dec
import conversorAD as cvad

def r_serial(port, baud, TRIGGER_VALUE, CAPTURE_LENGTH): #read_uint8_from_serial
    ser = serial.Serial(port, baud, timeout=1)
    ser.set_buffer_size(rx_size=16000, tx_size=16000)
    ser.reset_input_buffer()
    data = []
    #start_time = time.time()
    count = 0
    begin = 0
    end = 0 
    estado = 'IDLE'
    try:
        while True:
            # Lê todos os bytes disponíveis (uint8)
            dados = ser.read(ser.in_waiting or 1)
            if not dados:
                continue  # nada novo, volta pro loop

            for v in dados:
                if estado == 'IDLE':
                    if v < TRIGGER_VALUE:
                        print("Trigger detectado!")
                        estado = 'TRIGGERED'
                        captura = [v]
                        inicio_captura = time.time()
                elif estado == 'TRIGGERED':
                    captura.append(v)
                    if len(captura) >= CAPTURE_LENGTH:
                        duracao = time.time() - inicio_captura
                        print(f"Capturados {len(captura)} amostras em {duracao:.6f} s")
                        estado = 'IDLE'
                        # guarda a captura e sai do loop para pós-processamento
                        data = captura
                        print("Captura armazenada; saindo do loop para processamento")
                        # retorna da função — o bloco finally executará a limpeza e o processamento
                        return
    except StopIteration:
        # StopIteration não esperado no fluxo atual — não há dados a extrair aqui.
        # Deixar a limpeza e o pós-processamento para o bloco finally.
        pass

    except KeyboardInterrupt:
        print("Interrompido pelo usuário")
    finally:
        ser.close()
        print("Serial fechada")
        return data, duracao

# if __name__ == '__main__':
#     read_uint8_from_serial(SERIAL_PORT, BAUD_RATE)
    