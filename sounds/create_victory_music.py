import numpy as np
from scipy.io import wavfile

def create_victory_music():
    sample_rate = 44100
    duration = 3.0  # 3 seconds
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a triumphant melody
    frequencies = [
        440.0,  # A4
        554.37, # C#5
        659.25, # E5
        880.0   # A5
    ]
    
    # Create the melody with timing
    melody = np.zeros_like(t)
    current_time = 0
    note_duration = 0.25  # quarter note
    
    for i, freq in enumerate(frequencies):
        start = int(current_time * sample_rate)
        end = int((current_time + note_duration) * sample_rate)
        if end > len(t):
            break
        note = np.sin(2 * np.pi * freq * t[start:end])
        # Add harmonics
        note += 0.5 * np.sin(4 * np.pi * freq * t[start:end])
        note += 0.25 * np.sin(6 * np.pi * freq * t[start:end])
        # Apply envelope
        envelope = np.exp(-3 * np.linspace(0, 1, end-start))
        melody[start:end] = note * envelope
        current_time += note_duration
    
    # Normalize and convert to 16-bit integer
    melody = np.int16(melody * 32767)
    
    # Save the victory music
    wavfile.write('victory_music.wav', sample_rate, melody)

if __name__ == "__main__":
    create_victory_music()
    print("Victory music created successfully!")
