import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

import serialRead as sr
import plotTeste as pltt
import decodificador as dec
import conversorAD as cvad

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.25 # 0.25 segundos
TRIGGER_VALUE = 200  # valor de trigger para salvar
CAPTURE_LENGTH = 8500  # número de amostras a capturar após o trigger

# add matplotlib for embedded plots
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def build_gui():
    root = tk.Tk()
    root.title("Data Logger TELC2")
    root.geometry("1300x530")

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill='both', expand=True)

    # layout: left column = inputs + log, right column = two plots (top: data, bottom: bin_data)
    # configure columns
    frm.columnconfigure(0, weight=0)  # inputs column
    frm.columnconfigure(1, weight=1)  # plots column

    # Left side (inputs & log)
    left_frame = ttk.Frame(frm)
    left_frame.grid(row=0, column=0, sticky='nsw', padx=(0,10))
    left_frame.columnconfigure(0, weight=1)

    labels = ["Serial Port", "Baud Rate", "Read Duration (s)", "Trigger Value", "Capture Length"]
    defaults = [SERIAL_PORT, str(BAUD_RATE), str(READ_DURATION), str(TRIGGER_VALUE), str(CAPTURE_LENGTH)]
    entries = {}
    
    for i, (lbl, dflt) in enumerate(zip(labels, defaults)):
        ttk.Label(left_frame, text=lbl).grid(row=i, column=0, sticky='w', pady=4)
        ent = ttk.Entry(left_frame)
        ent.grid(row=i, column=1, sticky='ew', padx=6)
        ent.insert(0, dflt)
        entries[lbl] = ent
        left_frame.columnconfigure(1, weight=1)

    # Log area
    log = scrolledtext.ScrolledText(left_frame, height=12)
    log.grid(row=6, column=0, columnspan=2, sticky='nsew', pady=(10,0))
    left_frame.rowconfigure(6, weight=1)

    # Buttons
    btn_frame = ttk.Frame(left_frame)
    btn_frame.grid(row=7, column=0, columnspan=2, pady=8)
    start_btn = ttk.Button(btn_frame, text="Start Capture")
    start_btn.pack(side='left', padx=6)

    def clear_all():
        """Clear the text log and reset both plots to the empty state."""
        # clear log text
        log.delete('1.0', tk.END)
        # schedule plot update on the main thread to show 'Sem dados'
        try:
            root.after(0, lambda: update_plots([], []))
        except Exception:
            # if update_plots isn't available for some reason, ignore silently
            pass

    # Stop capture button (disabled until capture is started)
    stop_btn = ttk.Button(btn_frame, text="Stop Capture")
    stop_btn.pack(side='left', padx=6)
    stop_btn.config(state='disabled')

    # Clear log button
    clear_btn = ttk.Button(btn_frame, text="Clear Log", command=clear_all)
    clear_btn.pack(side='left')

    def append_log(text):
        log.after(0, lambda: (log.insert(tk.END, text + "\n"), log.see(tk.END)))

    # Right side (plots)
    right_frame = ttk.Frame(frm)
    right_frame.grid(row=0, column=1, sticky='nsew')
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(0, weight=1)
    right_frame.rowconfigure(1, weight=1)

    plot_top_frame = ttk.Frame(right_frame)
    plot_top_frame.grid(row=0, column=0, sticky='nsew', pady=(0,6))
    plot_bottom_frame = ttk.Frame(right_frame)
    plot_bottom_frame.grid(row=1, column=0, sticky='nsew', pady=(6,0))

    # Figure for raw data (top)
    fig_top = Figure(figsize=(5, 2.5), dpi=100)
    ax_top = fig_top.add_subplot(111)
    ax_top.set_title("Raw data")
    ax_top.set_xlabel("Sample")
    ax_top.set_ylabel("Amplitude")
    canvas_top = FigureCanvasTkAgg(fig_top, master=plot_top_frame)
    canvas_top.get_tk_widget().pack(fill='both', expand=True)

    # Figure for bin data (bottom)
    fig_bot = Figure(figsize=(5, 2.5), dpi=100)
    ax_bot = fig_bot.add_subplot(111)
    ax_bot.set_title("Binary data")
    ax_bot.set_xlabel("Bit index / Sample")
    ax_bot.set_ylabel("Value")
    canvas_bot = FigureCanvasTkAgg(fig_bot, master=plot_bottom_frame)
    canvas_bot.get_tk_widget().pack(fill='both', expand=True)

    def update_plots(raw_data, bin_data):
        # safe conversions
        try:
            x = list(range(len(raw_data)))
        except Exception:
            x = []
        try:
            bx = list(range(len(bin_data)))
        except Exception:
            bx = []

        ax_top.cla()
        ax_top.set_title("Raw data")
        ax_top.set_xlabel("Sample")
        ax_top.set_ylabel("Amplitude")
        if len(x) > 0:
            ax_top.plot(x, raw_data, lw=0.8)
        else:
            ax_top.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        canvas_top.draw_idle()

        ax_bot.cla()
        ax_bot.set_title("Binary data")
        ax_bot.set_xlabel("Bit index / Sample")
        ax_bot.set_ylabel("Value")
        if len(bx) > 0:
            ax_bot.step(bx, bin_data, where='mid')
        else:
            ax_bot.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        canvas_bot.draw_idle()

    # Event to control continuous capture loop
    capture_stop_event = threading.Event()

    def capture_thread(port, baud, read_dur, trigger, cap_len):
        """Loop de captura contínua. Executa capturas sucessivas até que
        `capture_stop_event` seja setado (quando o usuário clicar em Stop).
        """
        try:
            append_log(f"Iniciando captura contínua: port={port} baud={baud}")
            while not capture_stop_event.is_set():
                append_log("Aguardando trigger / iniciando nova captura...")
                data, duracao = sr.r_serial(port, baud, trigger, cap_len)
                append_log(f"Captura finalizada, duração: {duracao:.3f}s, amostras: {len(data)}")
                bin_data = cvad.s_to_bin(data)
                fs = 84000  # Hz
                # dec.nec_decoder may return bits as part of tuple; keep compatibility
                try:
                    address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)
                except Exception:
                    # fallback if module returns 5 elements
                    address, command, status, r_edg, f_edg = dec.nec_decoder(bin_data, fs)
                    bits = []
                if status == 0:
                    append_log("Decodificação não realizada")
                elif status == 1:
                    append_log("Verificação de comando: falhou")
                elif status == 2:
                    append_log("Verificação de comando: passou")
                elif status == 3:
                    append_log("Aviso: não foram detectados bits suficientes para decodificação")
                #append_log(f"Número de edges de subida: {r_edg}")
                #append_log(f"Número de edges de descida: {f_edg}")
                append_log(f"Bits detectados: {len(bits)}")
                append_log(f"Endereço: {hex(address)}, Comando: {hex(command)}\n\n")

                # update plots in main thread
                root.after(0, lambda d=data, b=bin_data: update_plots(d, b))
                # small idle to allow UI events to be processed
                if capture_stop_event.is_set():
                    break
        except Exception as e:
            append_log(f"Erro: {e}")
        finally:
            # re-enable start button and disable stop button when loop ends
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')

    def on_start():
        try:
            port = entries["Serial Port"].get().strip()
            baud = int(entries["Baud Rate"].get())
            read_dur = float(entries["Read Duration (s)"].get())
            trigger = int(entries["Trigger Value"].get())
            cap_len = int(entries["Capture Length"].get())
        except Exception as e:
            append_log(f"Parâmetros inválidos: {e}")
            return

        # start continuous capture
        start_btn.config(state='disabled')
        stop_btn.config(state='normal')
        capture_stop_event.clear()
        t = threading.Thread(target=capture_thread, args=(port, baud, read_dur, trigger, cap_len), daemon=True)
        t.start()

    def on_stop():
        """Signal to stop the capture loop. The actual stop will occur after
        the current capture finishes (since r_serial is blocking)."""
        append_log("Solicitado stop de captura. Aguardando fim da captura atual...")
        capture_stop_event.set()

    # wire stop button
    stop_btn.config(command=on_stop)

    start_btn.config(command=on_start)

    return root

if __name__ == '__main__':
    app = build_gui()
    app.mainloop()