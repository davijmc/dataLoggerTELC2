import serial

# Configurações da porta serial
SERIAL_PORT = 'COM5'
BAUD_RATE = 250000

# Inicializa a porta serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Inicializa limites
min_val = float('inf')
max_val = float('-inf')

print("Lendo valores da serial...\nPressione Ctrl+C para parar.\n")

try:
    while True:
        if ser.in_waiting:
            try:
                raw = ser.readline().decode().strip()
                if raw:
                    value = float(raw)

                    # Atualiza limites
                    if value > max_val:
                        max_val = value
                    if value < min_val:
                        min_val = value

                    print(f"Valor: {value:.4f} | Maximo: {max_val:.4f} | Minimo: {min_val:.4f}")

            except ValueError:
                # Ignora linhas que não são números válidos
                pass

except KeyboardInterrupt:
    print("\nLeitura encerrada.")

finally:
    ser.close()
