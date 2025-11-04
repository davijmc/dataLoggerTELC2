import serialRead as sr
import plotTeste as pltt
import decodificador as dec
import conversorAD as cvad
import pyautogui as pag

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.25 # 0.25 segundosd
TRIGGER_VALUE = 200  # valor de trigger para salvar
CAPTURE_LENGTH = 8500  # número de amostras a capturar após o trigger

def mouse(action):
    if action == 0:
        pass
    elif action == 1:
        pag.press('enter')  # pressiona Enter
    elif action == 2:
        pag.press('w')  # tecla W
    elif action == 3:
        pag.press('s')  # tecla S
    elif action == 4:
        pag.press('a')  # tecla A
    elif action == 5:
        pag.press('d')  # tecla D

if __name__ == '__main__':
    fs = 82333  # Hz, valor estimado
    action = 0
    while True:
        data, duracao = sr.r_serial(SERIAL_PORT, BAUD_RATE, TRIGGER_VALUE, CAPTURE_LENGTH)
        bin_data = cvad.ad(data)
        address, command, status, r_edg, f_edg, bits = dec.nec_decoder(bin_data, fs)
        if command == 0x0:
            action = action
        elif command == 0x8:
            action = 1
        elif command == 0x12:
            action = 2
        elif command == 0x18:
            action = 3
        elif command == 0x14:
            action = 4
        elif command == 0x16:
            action = 5
        print(f"Comando recebido: {hex(command)} -> ação: {action}")
        mouse(action)