import numpy as np
from scipy.io import wavfile

def create_shoot_sound():
    # Laser-like shooting sound
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = np.linspace(1000, 500, len(t))
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-5 * t)
    waveform = np.int16(waveform * 32767)
    wavfile.write('shoot.wav', sample_rate, waveform)

def create_hit_sound():
    # Impact sound
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 200
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-20 * t)
    waveform = np.int16(waveform * 32767)
    wavfile.write('hit.wav', sample_rate, waveform)

def create_death_sound():
    # Explosion-like sound
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = np.linspace(300, 50, len(t))
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-5 * t)
    noise = np.random.normal(0, 0.5, len(t))
    waveform = (waveform + noise) * np.exp(-5 * t)
    waveform = np.int16(waveform * 32767)
    wavfile.write('death.wav', sample_rate, waveform)

def create_victory_sound():
    # Triumphant sound
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    f1, f2, f3 = 440, 550, 660
    waveform = (np.sin(2 * np.pi * f1 * t) + 
                np.sin(2 * np.pi * f2 * t) + 
                np.sin(2 * np.pi * f3 * t)) / 3
    waveform *= np.exp(-3 * t)
    waveform = np.int16(waveform * 32767)
    wavfile.write('victory.wav', sample_rate, waveform)

def create_game_over_sound():
    # Sad game over sound
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    f1, f2 = 440, 220
    waveform = (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)) / 2
    waveform *= np.exp(-3 * t)
    waveform = np.int16(waveform * 32767)
    wavfile.write('game_over.wav', sample_rate, waveform)

if __name__ == "__main__":
    create_shoot_sound()
    create_hit_sound()
    create_death_sound()
    create_victory_sound()
    create_game_over_sound()
    print("Sound files created successfully!")
