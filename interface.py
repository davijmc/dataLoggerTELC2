import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
# import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from collections import deque

class SerialPlotInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface de Leitura Serial - Tempo Real")
        self.root.geometry("1000x700")
        
        # Variáveis para controle
        self.serial_port = None
        self.is_streaming = False
        self.data_points = deque(maxlen=1000)  # Buffer circular para 1000 pontos
        self.time_points = deque(maxlen=1000)
        self.start_time = 0
        self.recording_thread = None
        self.stop_event = threading.Event()
        
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
        title_label = ttk.Label(main_frame, text="Monitor Serial - Tempo Real", 
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
        
        # Botão Start/Stop
        self.start_stop_button = ttk.Button(control_frame, text="START", 
                                           command=self.toggle_streaming)
        self.start_stop_button.pack(side=tk.LEFT, padx=(10, 10))
        
        # Botão para limpar dados
        self.clear_button = ttk.Button(control_frame, text="Limpar", 
                                      command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão de teste
        self.test_button = ttk.Button(control_frame, text="Teste", 
                                     command=self.test_plot)
        self.test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Pronto")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Label para estatísticas
        self.stats_label = ttk.Label(control_frame, text="Pontos: 0")
        self.stats_label.pack(side=tk.RIGHT, padx=(10, 0))
        
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
        self.fig = Figure(figsize=(12, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Configurar aparência inicial
        self.ax.set_title("Monitor Serial - Tempo Real")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, 30)
        self.ax.set_ylim(-2, 2)
        
        # Configurar cor de fundo
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('#f8f8f8')
        
        # Canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Desenhar o gráfico inicial
        self.canvas.draw()
        
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
    
    def toggle_streaming(self):
        """Alterna entre iniciar e parar o streaming"""
        if not self.is_streaming:
            self.start_streaming()
        else:
            self.stop_streaming()
    
    def start_streaming(self):
        """Inicia o streaming de dados em tempo real"""
        if not self.connect_serial():
            return
            
        self.is_streaming = True
        self.start_stop_button.config(text="STOP")
        self.status_label.config(text="Status: Streaming em tempo real...")
        self.port_combo.config(state="disabled")
        self.refresh_button.config(state="disabled")
        
        # Resetar dados
        self.data_points.clear()
        self.time_points.clear()
        self.start_time = time.time()
        self.stop_event.clear()
        
        # Iniciar thread de leitura
        self.recording_thread = threading.Thread(target=self.read_serial_data)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Iniciar timer para atualização do gráfico
        print("Iniciando timer do gráfico...")  # Debug
        self.update_plot_timer()
        print("Timer iniciado!")  # Debug
    
    def stop_streaming(self):
        """Para o streaming de dados"""
        self.is_streaming = False
        self.stop_event.set()
        self.start_stop_button.config(text="START")
        self.status_label.config(text=f"Status: Parado - {len(self.data_points)} pontos coletados")
        self.port_combo.config(state="readonly")
        self.refresh_button.config(state="normal")
        
        # Parar timer (será parado automaticamente quando is_streaming for False)
        
        # Desconectar serial
        self.disconnect_serial()
    
    def clear_data(self):
        """Limpa todos os dados coletados"""
        self.data_points.clear()
        self.time_points.clear()
        self.stats_label.config(text="Pontos: 0")
        
        # Limpar gráfico
        self.ax.clear()
        self.ax.set_title("Monitor Serial - Tempo Real")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.grid(True, alpha=0.3)
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5, alpha=0.8)
        self.canvas.draw()
    
    def read_serial_data(self):
        """Thread para ler dados da serial continuamente"""
        print("Iniciando leitura da serial...")
        try:
            while not self.stop_event.is_set() and self.is_streaming:
                if self.serial_port and self.serial_port.is_open:
                    try:
                        # Verificar se há dados disponíveis
                        if self.serial_port.in_waiting > 0:
                            # Ler linha da serial
                            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                            print(f"Linha lida: '{line}'")  # Debug
                            
                            if line:
                                # Tentar converter para float
                                try:
                                    value = float(line)
                                    current_time = time.time() - self.start_time
                                    self.data_points.append(value)
                                    self.time_points.append(current_time)
                                    print(f"Valor adicionado: {value} no tempo {current_time:.2f}s")  # Debug
                                    
                                    # Atualizar contador de pontos na UI thread
                                    self.root.after_idle(self.update_stats)
                                    
                                except ValueError:
                                    # Se não conseguir converter, tentar extrair números da linha
                                    import re
                                    numbers = re.findall(r'-?\d+\.?\d*', line)
                                    if numbers:
                                        value = float(numbers[0])
                                        current_time = time.time() - self.start_time
                                        self.data_points.append(value)
                                        self.time_points.append(current_time)
                                        print(f"Número extraído: {value} no tempo {current_time:.2f}s")  # Debug
                                        
                                        # Atualizar contador de pontos na UI thread
                                        self.root.after_idle(self.update_stats)
                                    else:
                                        print(f"Não foi possível extrair número da linha: '{line}'")  # Debug
                        # else:
                            # Comentado: dados de teste removidos para não interferir
                                    
                    except Exception as e:
                        print(f"Erro ao ler serial: {e}")
                
                time.sleep(0.01)  # Pausa pequena para leitura mais rápida
                
        except Exception as e:
            print(f"Erro geral na thread de leitura: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante streaming:\n{str(e)}"))
    
    def update_stats(self):
        """Atualiza as estatísticas na interface"""
        self.stats_label.config(text=f"Pontos: {len(self.data_points)}")
    
    def test_plot(self):
        """Função de teste para adicionar dados e ver se o plot funciona"""
        print("Adicionando dados de teste...")
        # Limpar dados existentes
        self.data_points.clear()
        self.time_points.clear()
        
        # Adicionar alguns pontos de teste
        for i in range(10):
            t = i * 0.1
            value = np.sin(2 * np.pi * t) + np.random.normal(0, 0.1)
            self.data_points.append(value)
            self.time_points.append(t)
        
        print(f"Adicionados {len(self.data_points)} pontos de teste")
        self.update_stats()
        
        # Atualizar plot manualmente
        if len(self.data_points) > 0:
            times = list(self.time_points)
            values = list(self.data_points)
            
            self.ax.clear()
            self.ax.plot(times, values, 'b-', linewidth=1.5, alpha=0.8)
            self.ax.set_title(f"Teste - {len(values)} pontos")
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Valor")
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()
            print("Plot atualizado manualmente")
    
    def update_plot_timer(self):
        """Timer para atualizar o gráfico periodicamente"""
        if self.is_streaming:
            try:
                self.update_plot_display()
                # Agendar próxima atualização
                self.root.after(50, self.update_plot_timer)  # Atualizar a cada 50ms
            except Exception as e:
                print(f"Erro no timer do plot: {e}")
    
    def update_plot_display(self):
        """Atualiza a exibição do gráfico"""
        try:
            if len(self.data_points) > 0:
                # Converter para listas para plotagem
                times = list(self.time_points)
                values = list(self.data_points)
                
                print(f"Atualizando plot com {len(values)} pontos")  # Debug
                
                # Limpar e redesenhar completamente o gráfico
                self.ax.clear()
                self.ax.plot(times, values, 'b-', linewidth=1.5, alpha=0.8, marker='o', markersize=2)
                
                # Configurar aparência do gráfico
                self.ax.set_xlabel("Tempo (s)")
                self.ax.set_ylabel("Valor")
                self.ax.grid(True, alpha=0.3)
                self.ax.set_facecolor('#f8f8f8')
                
                # Ajustar limites dos eixos
                if times and values:
                    # Mostrar últimos 30 segundos ou todos os dados se menos que isso
                    time_window = 30
                    if len(times) > 1 and times[-1] > time_window:
                        x_min = times[-1] - time_window
                        x_max = times[-1] + 1
                    else:
                        x_min = 0 if len(times) == 0 else min(0, min(times) - 0.5)
                        x_max = max(time_window, (times[-1] + 1 if len(times) > 0 else 1))
                    
                    self.ax.set_xlim(x_min, x_max)
                    
                    # Ajustar limites Y com margem
                    if len(values) == 1:
                        # Se só há um ponto, criar uma janela ao redor dele
                        y_center = values[0]
                        y_margin = max(abs(y_center) * 0.1, 1)  # 10% ou pelo menos 1 unidade
                        self.ax.set_ylim(y_center - y_margin, y_center + y_margin)
                    else:
                        # Se há múltiplos pontos, usar o range normal
                        y_min, y_max = min(values), max(values)
                        y_range = y_max - y_min
                        y_margin = max(y_range * 0.1, 0.1)  # 10% ou pelo menos 0.1
                        self.ax.set_ylim(y_min - y_margin, y_max + y_margin)
                
                # Atualizar título com estatísticas
                if len(values) > 0:
                    mean_val = np.mean(values)
                    self.ax.set_title(f"Monitor Serial - Tempo Real | Pontos: {len(values)} | Média: {mean_val:.2f}")
                
                # Redesenhar o canvas (otimizado)
                self.canvas.draw_idle()
                print(f"Plot redesenhado com sucesso")  # Debug
            else:
                # Se não há dados, manter eixos padrão
                self.ax.clear()
                self.ax.set_xlim(0, 30)
                self.ax.set_ylim(-2, 2)
                self.ax.set_title("Monitor Serial - Tempo Real | Aguardando dados...")
                self.ax.set_xlabel("Tempo (s)")
                self.ax.set_ylabel("Valor")
                self.ax.grid(True, alpha=0.3)
                self.ax.set_facecolor('#f8f8f8')
                self.canvas.draw()
                
        except Exception as e:
            print(f"Erro ao atualizar plot: {e}")
    
    def on_closing(self):
        """Função chamada ao fechar a janela"""
        if self.is_streaming:
            self.stop_streaming()
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