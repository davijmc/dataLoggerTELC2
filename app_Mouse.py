import serialRead as sr
import decodificador as dec
import conversorAD as cvad
import pyautogui as pag

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.25 # 0.25 segundos
TRIGGER_VALUE = 200  # valor de trigger para começar a salvar os dados
CAPTURE_LENGTH = 8500  # número de amostras a capturar após o trigger

def mouse(action):
    if action == 0:
        pass
    elif action == 1:
        pag.leftClick()  # clique esquerdo
    elif action == 2:
        pag.moveRel(0, -10)  # cima (y diminui)
    elif action == 3:
        pag.moveRel(0, 10)   # baixo (y aumenta)
    elif action == 4:
        pag.moveRel(-10, 0)  # esquerda
    elif action == 5:
        pag.moveRel(10, 0)   # direita

if __name__ == '__main__':
    fs = 84000  # Hz
    action = 0
    while True:
        data, duracao = sr.r_serial(SERIAL_PORT, BAUD_RATE, TRIGGER_VALUE, CAPTURE_LENGTH)
        bin_data = cvad.s_to_bin(data)
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
        print(f"Comando recebido: {hex(command)} -> acao: {action}")
        mouse(action)