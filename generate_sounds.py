"""
Generate WAV sound files for Plinko game.
Run this script once to create the sound files.
"""

import numpy as np
import wave
import struct
import os

def generate_wav(filename, frequency, duration, volume=0.3, decay=30):
    """Generate a WAV sound file."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Create sound wave with decay
    wave_data = np.sin(2 * np.pi * frequency * t) * np.exp(-t * decay)
    wave_data = (wave_data * 32767 * volume).astype(np.int16)
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wave_data:
            wav_file.writeframes(struct.pack('<h', sample))

def generate_score_sound(filename):
    """Generate a satisfying coin/win sound."""
    sample_rate = 44100
    duration = 0.4
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Coin sound: Two high pitched tones quickly jumping
    f1 = 1200
    f2 = 1800
    
    # Mix two sines: one constant, one slight arp or just harmonic
    # Let's do a quick 'bling'
    # First 0.1s is f1, rest is f2, but smooth transition? 
    # Let's try overlapping bells
    
    decay1 = np.exp(-t * 15)
    wave1 = np.sin(2 * np.pi * f1 * t) * decay1
    
    # Second tone starts slightly later (0.05s)
    delay_samples = int(0.05 * sample_rate)
    t2 = np.linspace(0, duration - 0.05, n_samples - delay_samples, False)
    decay2 = np.exp(-t2 * 10)
    wave2 = np.sin(2 * np.pi * f2 * t2) * decay2
    
    # Combine
    wave_data = np.zeros(n_samples)
    wave_data += wave1 * 0.5
    wave_data[delay_samples:] += wave2 * 0.5
    
    wave_data = (wave_data * 32767 * 0.3).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wave_data:
            wav_file.writeframes(struct.pack('<h', sample))

def generate_click_sound(filename):
    """Generate a satisfying mechanical keycap click."""
    sample_rate = 44100
    duration = 0.08
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Thock sound: Low frequency impulse + noise click
    f_thock = 300
    thock = np.sin(2 * np.pi * f_thock * t) * np.exp(-t * 80)
    
    # Click transient (high pitch burst)
    noise = np.random.normal(0, 1, n_samples)
    click = noise * np.exp(-t * 200) * 0.5
    
    wave_data = thock * 0.7 + click * 0.3
    
    wave_data = (wave_data * 32767 * 0.5).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wave_data:
            wav_file.writeframes(struct.pack('<h', sample))

def generate_error_sound(filename):
    """Generate an error/buzz sound."""
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    frequency = 200
    wave_data = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10)
    wave_data = (wave_data * 32767 * 0.2).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wave_data:
            wav_file.writeframes(struct.pack('<h', sample))

def generate_ping_sound(filename):
    """Generate a high-pitched metal ping sound."""
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Metal ping: high frequency with very fast decay + overtones
    fundamental = 2100
    wave_data = (
        np.sin(2 * np.pi * fundamental * t) * 0.6 +
        np.sin(2 * np.pi * fundamental * 2.1 * t) * 0.2 + # non-integer harmonic for "metal" sound
        np.sin(2 * np.pi * fundamental * 3.8 * t) * 0.1
    )
    
    # Exponential decay
    decay_envelope = np.exp(-t * 20)
    
    wave_data = wave_data * decay_envelope
    wave_data = (wave_data * 32767 * 0.15).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wave_data:
            wav_file.writeframes(struct.pack('<h', sample))

if __name__ == "__main__":
    os.makedirs('sounds', exist_ok=True)
    generate_score_sound('sounds/score.wav')
    generate_click_sound('sounds/click.wav')
    generate_error_sound('sounds/error.wav')
    generate_ping_sound('sounds/ping.wav')
    print("Sound files generated successfully!")
