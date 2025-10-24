import numpy as np
import matplotlib.pyplot as plt

Frame_size = 5200
sync_high_duration = 736
sync_high_duration_max_error = 0.1
frames = []

# separa os frames
# Estados
IDLE = 0
WAITING_SYNC_RISING_EDGE = 1
WAITING_SYNC_FALLING_EDGE = 2

estado = WAITING_SYNC_RISING_EDGE

i_start = 0
i_end = 0
i = 0

signal_bin = np.loadtxt('C:\\Users\\davij\\Desktop\\Facul\\10°Periodo\\sinDig.txt', dtype=int)

while i < len(signal_bin):
    if estado == WAITING_SYNC_RISING_EDGE:
        if signal_bin[i] == 1:  # se encontrar um nivel alto
            i_start = i
            estado = WAITING_SYNC_FALLING_EDGE
    elif estado == WAITING_SYNC_FALLING_EDGE:
        if signal_bin[i] == 0:  # se encontrar um nivel baixo
            i_end = i
            sync_high_duration_error = ((i_end - i_start) - sync_high_duration) / sync_high_duration
            if abs(sync_high_duration_error) < sync_high_duration_max_error:
                frames.append([i_start, min(i_end + Frame_size + 1, len(signal_bin))])
                i = i_end + Frame_size + 1
            estado = WAITING_SYNC_RISING_EDGE
    i = i + 1

# Plot the extracted frames
if frames:
    plt.figure(figsize=(12, 8))
    
    for idx, frame_bounds in enumerate(frames):
        start, end = frame_bounds
        frame_data = signal_bin[start:end]
        
        plt.subplot(len(frames), 1, idx + 1)
        plt.plot(frame_data, 'b-', linewidth=0.5)
        plt.title(f'Frame {idx + 1} (samples {start} to {end-1})')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        if idx == len(frames) - 1:
            plt.xlabel('Sample')
    
    plt.tight_layout()
    plt.show()
    
    print(f"Total frames extracted: {len(frames)}")
    for i, frame_bounds in enumerate(frames):
        print(f"Frame {i+1}: samples {frame_bounds[0]} to {frame_bounds[1]-1} (length: {frame_bounds[1]-frame_bounds[0]})")
else:
    print("No frames were extracted")
