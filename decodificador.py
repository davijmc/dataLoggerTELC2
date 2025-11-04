import numpy as np

def nec_decoder(signal, fs):
    decoded_address = 0
    decoded_command = 0
    status = 0
    r_edg = 0
    f_edg = 0

    T_bit_off = 562e-6
    T_bit_on = 1687e-6
    T_tolerance = 0.2

    signal = np.array(signal).flatten()
    signal_diff = np.diff(np.concatenate(([0], signal)))

    rising_edges = np.where(signal_diff > 0)[0]
    falling_edges = np.where(signal_diff < 0)[0]
    r_edg = len(rising_edges)
    f_edg = len(falling_edges)
    #print(f"Rising edges: {len(rising_edges)}")
    #print(f"Falling edges: {len(falling_edges)}")

    if len(rising_edges) > 2 and len(falling_edges) > 2:
        rising_edges = rising_edges[1:]
        falling_edges = falling_edges[1:]

    bits = []
    
    for i in range(min(len(rising_edges), len(falling_edges) - 1)):
        if i < len(rising_edges) - 1:
            space_duration = (rising_edges[i + 1] - falling_edges[i]) / fs
        else:
            space_duration = 0

        if space_duration > 0:
            if abs(space_duration - T_bit_off) / T_bit_off < T_tolerance:
                bits.append(0)
            elif abs(space_duration - T_bit_on) / T_bit_on < T_tolerance:
                bits.append(1)

    #print(f"Bits detectados: {len(bits)}")
    if len(bits) == 32:
        address_bits = bits[0:16]
        command_bits = bits[16:24]
        inv_command_bits = bits[24:32]

        def bits_to_int(b): 
            return int(''.join(str(x) for x in reversed(b)), 2)

        decoded_address = bits_to_int(address_bits)
        decoded_command = bits_to_int(command_bits)
        decoded_inv_command = bits_to_int(inv_command_bits)

        if (decoded_command ^ 0xFF) != decoded_inv_command:
            #print("Verificação de comando: falhou")
            status = 1
        else:
            #print("Verificação de comando: passou")
            status = 2
    else:
        #print("Aviso: não foram detectados bits suficientes para decodificação")
        status = 3

    return decoded_address, decoded_command, status, r_edg, f_edg, bits
