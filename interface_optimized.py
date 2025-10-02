import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import numpy as np

# Apply a more modern visual style to the plot
plt.style.use('seaborn-v0_8-whitegrid')

class SerialOscilloscope:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Real-Time Serial Plotter")
        self.root.geometry("1000x700")

        # --- Control Variables ---
        self.serial_port = None
        self.is_streaming = False
        self.stop_event = threading.Event()

        # A deque (double-ended queue) is highly efficient for this purpose
        self.data_points = deque(maxlen=2000)
        self.time_points = deque(maxlen=2000)
        self.start_time = 0

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # --- Main Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # --- Controls Frame ---
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # COM Port Selection
        ttk.Label(control_frame, text="Porta:").pack(side=tk.LEFT, padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(control_frame, textvariable=self.port_var, width=10, state="readonly")
        self.port_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_button = ttk.Button(control_frame, text="↻", width=3, command=self.refresh_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Baud Rate Selection
        ttk.Label(control_frame, text="Baud Rate:").pack(side=tk.LEFT, padx=(0, 5))
        self.baud_var = tk.StringVar(value="250000")
        common_bauds = ['9600', '38400', '115200', '250000', '256000', '921600', '2000000']
        self.baud_combo = ttk.Combobox(control_frame, textvariable=self.baud_var, values=common_bauds, width=10)
        self.baud_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Action Buttons
        self.start_stop_button = ttk.Button(control_frame, text="START", command=self.toggle_streaming, width=10)
        self.start_stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(control_frame, text="Limpar", command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status Label
        self.status_label = ttk.Label(control_frame, text="Status: Pronto")
        self.status_label.pack(side=tk.RIGHT, padx=(10, 0))

        # --- Plotting Frame ---
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=0, sticky="nsew")
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        self.setup_plot(plot_frame)

        # Call refresh_ports at the end, after ALL widgets are created (including status_label)
        self.refresh_ports()

    def setup_plot(self, parent):
        self.fig, self.ax = plt.subplots(facecolor='#f0f0f0')
        self.ax.set_title("Aguardando Dados...")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")

        # OPTIMIZATION: Create the plot line object only once
        self.line, = self.ax.plot([], [], color='royalblue', lw=1.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.draw()

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_var.set(ports[0])
            # Verificar se status_label existe antes de usar
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Status: Portas atualizadas")
        else:
            self.port_var.set("N/A")
            # Verificar se status_label existe antes de usar
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Status: Nenhuma porta encontrada")

    def toggle_streaming(self):
        if self.is_streaming:
            self.stop_streaming()
        else:
            self.start_streaming()

    def start_streaming(self):
        try:
            port = self.port_var.get()
            baud = int(self.baud_var.get())
            if port == "N/A":
                messagebox.showerror("Erro", "Nenhuma porta serial selecionada.")
                return

            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.serial_port.flushInput()
        except (serial.SerialException, ValueError) as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível abrir a porta {port}:\n{e}")
            return

        self.is_streaming = True
        self.stop_event.clear()
        self.start_time = time.time()
        
        self.data_points.clear()
        self.time_points.clear()

        # Start the data reading thread
        self.read_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.read_thread.start()

        # Start the plot updating loop
        self.update_plot()

        # Update UI state
        self.start_stop_button.config(text="STOP")
        self.status_label.config(text=f"Status: Lendo {port}...")
        self.port_combo.config(state="disabled")
        self.baud_combo.config(state="disabled")
        self.refresh_button.config(state="disabled")

    def stop_streaming(self):
        self.is_streaming = False
        self.stop_event.set()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        self.start_stop_button.config(text="START")
        self.status_label.config(text="Status: Parado")
        self.port_combo.config(state="readonly")
        self.baud_combo.config(state="normal")
        self.refresh_button.config(state="normal")

    def read_serial_data(self):
        while not self.stop_event.is_set():
            try:
                line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    value = float(line)
                    current_time = time.time() - self.start_time
                    self.data_points.append(value)
                    self.time_points.append(current_time)
            except (ValueError, TypeError):
                # Ignore lines that can't be converted to float
                continue
            except serial.SerialException:
                # Device was disconnected
                self.root.after(0, self.stop_streaming) # Stop streaming on the main thread
                break

    def update_plot(self):
        if not self.is_streaming:
            return

        if self.data_points:
            # OPTIMIZATION: Only update the line's data, don't redraw the whole plot
            self.line.set_data(self.time_points, self.data_points)

            # --- Auto-Scaling and Sliding Window Logic ---
            current_time = self.time_points[-1]
            
            # 10-second viewing window
            if current_time > 10:
                self.ax.set_xlim(current_time - 10, current_time)
            else:
                self.ax.set_xlim(0, 10)
            
            # Auto-scale the Y-axis
            values_np = np.array(self.data_points)
            y_min = values_np.min()
            y_max = values_np.max()
            y_margin = (y_max - y_min) * 0.1
            self.ax.set_ylim(y_min - y_margin - 0.1, y_max + y_margin + 0.1)

            self.ax.set_title(f"Recebendo Dados... ({len(self.data_points)} pontos)")
            self.canvas.draw()

        # Schedule the next update (approx. 30 FPS)
        self.root.after(33, self.update_plot)

    def clear_data(self):
        self.data_points.clear()
        self.time_points.clear()
        # Clear the plot without stopping the stream
        self.line.set_data([], [])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title("Dados Limpos")
        self.canvas.draw()

    def on_closing(self):
        self.stop_streaming()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialOscilloscope(root)
    root.mainloop()