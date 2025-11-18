def s_to_bin(signal):
    signal_max = max(signal)
    signal_min = min(signal)
    avg = (signal_max + signal_min) / 2
    delta = signal_max - signal_min
    
    # Normaliza e inverte o sinal
    signal = [-1 * ((s - avg) / delta + 0.5) + 1 for s in signal]
    
    # Calcula nova média e binariza
    signal_max = max(signal)
    signal_min = min(signal)
    avg = (signal_max + signal_min) / 2
    signal_bin = [1 if s > avg else 0 for s in signal]
    
    return signal_bin