import serialRead as sr
import plotTeste as pltt
import decodificador as dec
import conversorAD as cvad

SERIAL_PORT = 'COM6'
BAUD_RATE = 2000000
READ_DURATION = 0.25 # 0.175 segundos; use None para rodar até Ctrl+C

if __name__ == '__main__':
    data = sr.read_uint8_from_serial(SERIAL_PORT, BAUD_RATE, float(READ_DURATION))






"""
data = cvad.ad(data)
        fs = 82333  # Hz, valor estimado - corrigir calculo dinâmico
        print(f"Fs estimada: {fs} Hz")
        #vet = [0,0,0,0,0] # vetor para adicionar um 0 no início
        #data = vet + data
        address, command = dec.nec_decoder(data, fs)
        print(f"Endereço: {hex(address)}, Comando: {hex(command)}")
        save_vector_to_file(data, OUTPUT_FILE)
        print(f"{len(data)} valores salvos em {OUTPUT_FILE}")
        pltTeste.pltTeste(data)
        """