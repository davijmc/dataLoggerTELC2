import serial
import time
from datetime import datetime

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.09  # 90 milissegundos; use None para rodar até Ctrl+C
TRIGGER_VALUE = 200  # valor de trigger para salvar
OUTPUT_FILE = 'dados.txt'

def save_vector_to_file(vec, filename=OUTPUT_FILE):
    """Salva os valores do vetor em arquivo, um por linha."""
    with open(filename, 'w') as f:
        for v in vec:
            f.write(f"{v}\n")

def read_uint8_from_serial(port, baud, duration=None):
    ser = serial.Serial(port, baud, timeout=1)
    data = []
    start = time.time()
    try:
        print(f"Abrindo {port} @ {baud} bps")
        while True:
            # if duration is not None and (time.time() - start) >= duration:
            #     break
            if ser.in_waiting:
                b = ser.read(1)  # lê 1 byte
                if b:
                    # uint8 little-endian (para 1 byte não muda)
                    val = int.from_bytes(b, byteorder='little', signed=False)
                    # if val <=200 salva por 90ms
                    if val <= TRIGGER_VALUE:
                        start = time.time()
                        while (time.time() - start) < (READ_DURATION):
                            val = int.from_bytes(b, byteorder='little', signed=False)
                            data.append(val)
                            # print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {val}")
                        break
            else:
                time.sleep(0.000001)  # evita loop ocupado
    except KeyboardInterrupt:
        print("Interrompido pelo usuário")
    finally:
        ser.close()
        print("Serial fechada")
        save_vector_to_file(data, OUTPUT_FILE)
        print(f"{len(data)} valores salvos em {OUTPUT_FILE}")

if __name__ == '__main__':
    read_uint8_from_serial(SERIAL_PORT, BAUD_RATE, READ_DURATION)
