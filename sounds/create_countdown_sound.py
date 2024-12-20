import numpy as np
from scipy.io import wavfile

def create_countdown_sound():
    sample_rate = 44100
    duration = 0.2  # 200ms beep
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a beep sound
    frequency = 440.0  # A4 note
    beep = np.sin(2 * np.pi * frequency * t)
    
    # Add harmonics for richer sound
    beep += 0.5 * np.sin(4 * np.pi * frequency * t)
    beep += 0.25 * np.sin(6 * np.pi * frequency * t)
    
    # Apply envelope
    envelope = np.exp(-3 * np.linspace(0, 1, len(t)))
    beep = beep * envelope
    
    # Normalize and convert to 16-bit integer
    beep = np.int16(beep * 32767)
    
    # Save the countdown beep
    wavfile.write('countdown_beep.wav', sample_rate, beep)

if __name__ == "__main__":
    create_countdown_sound()
    print("Countdown sound created successfully!")
