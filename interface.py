import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

class SerialPlotInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface de Leitura Serial COM5")
        self.root.geometry("800x600")
        
        # Variáveis para controle
        self.serial_port = None
        self.is_recording = False
        self.data_points = []
        self.time_points = []
        
        # Configuração da interface
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Gravador Serial COM5", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Frame para seleção de porta
        port_frame = ttk.Frame(control_frame)
        port_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(port_frame, text="Porta:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="COM5")
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, 
                                      width=8, state="readonly")
        self.port_combo.pack(side=tk.LEFT, padx=(5, 5))
        
        # Botão para atualizar portas
        self.refresh_button = ttk.Button(port_frame, text="↻", width=3,
                                        command=self.refresh_ports)
        self.refresh_button.pack(side=tk.LEFT)
        
        # Botão de gravação
        self.record_button = ttk.Button(control_frame, text="Iniciar Gravação (3s)", 
                                       command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT, padx=(10, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Pronto")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Carregar portas disponíveis
        self.refresh_ports()
        
        # Frame para o gráfico
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        # Configurar matplotlib
        self.setup_plot(plot_frame)
    
    def refresh_ports(self):
        """Atualiza a lista de portas COM disponíveis"""
        try:
            ports = serial.tools.list_ports.comports()
            available_ports = [port.device for port in ports]
            
            if available_ports:
                self.port_combo['values'] = available_ports
                # Se COM5 estiver disponível, manter selecionado
                if 'COM5' in available_ports:
                    self.port_var.set('COM5')
                else:
                    # Senão, selecionar a primeira porta disponível
                    self.port_var.set(available_ports[0])
                
                self.status_label.config(text=f"Status: {len(available_ports)} porta(s) encontrada(s)")
            else:
                self.port_combo['values'] = ['Nenhuma porta encontrada']
                self.port_var.set('Nenhuma porta encontrada')
                self.status_label.config(text="Status: Nenhuma porta COM encontrada")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar portas COM:\n{str(e)}")
            self.port_combo['values'] = ['COM5']
            self.port_var.set('COM5')
        
    def setup_plot(self, parent):
        # Criar figura matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Dados da Serial COM5")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True)
        
        # Canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar de navegação
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Adicionar toolbar do matplotlib
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
    def connect_serial(self):
        """Conecta à porta serial COM5"""
        try:
            # Tentar fechar conexões anteriores se existirem
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                time.sleep(0.5)  # Aguardar um pouco para liberar a porta
            
            # Configurar a conexão serial
            selected_port = self.port_var.get()
            if not selected_port or selected_port == 'Nenhuma porta encontrada':
                messagebox.showerror("Erro", "Selecione uma porta COM válida")
                return False
                
            self.serial_port = serial.Serial()
            self.serial_port.port = selected_port
            self.serial_port.baudrate = 250000
            self.serial_port.timeout = 0.1
            self.serial_port.write_timeout = 0.1
            self.serial_port.bytesize = serial.EIGHTBITS
            self.serial_port.parity = serial.PARITY_NONE
            self.serial_port.stopbits = serial.STOPBITS_ONE
            self.serial_port.rtscts = False
            self.serial_port.dsrdtr = False
            self.serial_port.xonxoff = False
            
            # Abrir a conexão
            self.serial_port.open()
            
            # Limpar buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            return True
            
        except serial.SerialException as e:
            error_msg = str(e).lower()
            
            if "access is denied" in error_msg or "acesso negado" in error_msg:
                messagebox.showerror("Erro de Acesso", 
                    f"Acesso negado à {selected_port}!\n\n"
                    "Possíveis soluções:\n"
                    f"1. Feche outros programas que possam estar usando {selected_port}\n"
                    "   (Arduino IDE, PuTTY, Tera Term, etc.)\n"
                    "2. Execute este programa como Administrador\n"
                    "3. Desconecte e reconecte o dispositivo USB\n"
                    "4. Verifique se o driver está instalado corretamente\n"
                    "5. Clique em ↻ para atualizar a lista de portas")
            elif "could not open port" in error_msg:
                messagebox.showerror("Erro Serial", 
                    f"Não foi possível abrir {selected_port}!\n\n"
                    "Verifique se:\n"
                    "1. O dispositivo está conectado\n"
                    f"2. A porta {selected_port} existe\n"
                    "3. O driver está instalado\n"
                    "4. Clique em ↻ para atualizar portas")
            else:
                messagebox.showerror("Erro Serial", f"Erro ao conectar {selected_port}:\n{str(e)}")
            
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado:\n{str(e)}")
            return False
    
    def disconnect_serial(self):
        """Desconecta da porta serial"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
    
    def toggle_recording(self):
        """Inicia ou para a gravação"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia a gravação de dados"""
        if not self.connect_serial():
            return
            
        self.is_recording = True
        self.record_button.config(text="Gravando...", state="disabled")
        self.status_label.config(text="Status: Gravando dados por 3 segundos...")
        
        # Limpar dados anteriores
        self.data_points = []
        self.time_points = []
        
        # Iniciar thread de gravação
        self.recording_thread = threading.Thread(target=self.record_data)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def record_data(self):
        """Thread para gravar dados da serial por 3 segundos"""
        start_time = time.time()
        recording_duration = 3.0  # 3 segundos
        
        # Configurar progress bar
        self.root.after(0, lambda: self.progress.config(maximum=recording_duration))
        
        try:
            while time.time() - start_time < recording_duration:
                current_time = time.time() - start_time
                
                # Atualizar progress bar
                self.root.after(0, lambda t=current_time: self.progress.config(value=t))
                
                if self.serial_port and self.serial_port.in_waiting > 0:
                    try:
                        # Ler linha da serial
                        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        
                        if line:
                            # Tentar converter para float
                            try:
                                value = float(line)
                                self.data_points.append(value)
                                self.time_points.append(current_time)
                            except ValueError:
                                # Se não conseguir converter, tentar extrair números da linha
                                import re
                                numbers = re.findall(r'-?\d+\.?\d*', line)
                                if numbers:
                                    value = float(numbers[0])
                                    self.data_points.append(value)
                                    self.time_points.append(current_time)
                    except Exception as e:
                        print(f"Erro ao ler serial: {e}")
                
                time.sleep(0.01)  # Pequena pausa para não sobrecarregar
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante gravação:\n{str(e)}"))
        
        finally:
            # Finalizar gravação
            self.root.after(0, self.finish_recording)
    
    def finish_recording(self):
        """Finaliza a gravação e atualiza a interface"""
        self.is_recording = False
        self.disconnect_serial()
        
        self.record_button.config(text="Iniciar Gravação (3s)", state="normal")
        self.progress.config(value=0)
        
        if self.data_points:
            self.status_label.config(text=f"Status: Gravação concluída - {len(self.data_points)} pontos coletados")
            self.update_plot()
        else:
            self.status_label.config(text="Status: Nenhum dado coletado")
            messagebox.showwarning("Aviso", "Nenhum dado foi coletado da serial.\nVerifique se há dados sendo enviados na COM5.")
    
    def update_plot(self):
        """Atualiza o gráfico com os dados coletados"""
        self.ax.clear()
        
        if self.data_points and self.time_points:
            self.ax.plot(self.time_points, self.data_points, 'b-', linewidth=1)
            self.ax.set_title(f"Dados da Serial COM5 - {len(self.data_points)} pontos")
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Valor")
            self.ax.grid(True)
            
            # Adicionar estatísticas
            if len(self.data_points) > 0:
                mean_val = np.mean(self.data_points)
                std_val = np.std(self.data_points)
                min_val = np.min(self.data_points)
                max_val = np.max(self.data_points)
                
                stats_text = f"Média: {mean_val:.2f}, Std: {std_val:.2f}\nMin: {min_val:.2f}, Max: {max_val:.2f}"
                self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes,
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.canvas.draw()
    
    def on_closing(self):
        """Função chamada ao fechar a janela"""
        if self.is_recording:
            self.stop_recording()
        self.disconnect_serial()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = SerialPlotInterface(root)
    
    # Configurar evento de fechamento
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Iniciar loop da interface
    root.mainloop()

if __name__ == "__main__":
    main()