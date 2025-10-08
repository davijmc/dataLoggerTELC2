import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configurações da porta serial
SERIAL_PORT = 'COM5'
BAUD_RATE = 250000

# Inicializa a porta serial
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Dados para plotar
x_data = []
y_data = []

# Inicializa valores mínimo e máximo
min_val = float('inf')
max_val = float('-inf')

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_xlabel('Amostras')
ax.set_ylabel('Valor')
ax.set_title('Serial Plotter')

def init():
    ax.set_xlim(0, 100)
    ax.set_ylim(-2, 2)  # Limite fixo esperado para senoide de +/-1.5
    line.set_data([], [])
    return line,

def update(frame):
    global min_val, max_val

    if ser.in_waiting:
        try:
            raw = ser.readline().decode(errors='ignore').strip()
            if raw:
                value = float(raw)

                # Atualiza valores
                x_data.append(len(x_data))
                y_data.append(value)

                # Atualiza min e max
                if value > max_val:
                    max_val = value
                if value < min_val:
                    min_val = value

                # Print bonito no terminal
                print(f"Valor: {value:7.4f} | Máximo: {max_val:7.4f} | Mínimo: {min_val:7.4f}")

                # Mantém apenas as últimas 100 amostras
                if len(x_data) > 100:
                    x_data.pop(0)
                    y_data.pop(0)
                    for i in range(len(x_data)):
                        x_data[i] = i

                # Atualiza a linha
                line.set_data(x_data, y_data)

                # Mantém eixo Y fixo em torno de ±1.5 com folga
                ax.set_ylim(-2, 2)

        except ValueError:
            # Ignora linhas inválidas (ruído, caracteres errados, etc.)
            pass
        except Exception as e:
            print(f"Erro: {e}")
            pass

    return line,

ani = animation.FuncAnimation(fig, update, init_func=init, blit=True, interval=50)
plt.show()

ser.close()
