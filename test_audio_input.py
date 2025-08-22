#!/usr/bin/env python3
"""
Simple audio input test to verify guitar signal processing
"""

import numpy as np
import sounddevice as sd
import time
from scipy.fft import fft
from scipy.signal import windows

def analyze_audio(audio_data, sample_rate=48000):
    """Analyze audio data and show frequency spectrum"""
    # Apply window function to reduce spectral leakage
    window = windows.hann(len(audio_data))
    windowed_audio = audio_data * window
    
    # Compute FFT
    fft_result = fft(windowed_audio)
    frequencies = np.fft.fftfreq(len(fft_result), 1/sample_rate)
    
    # Get positive frequencies only
    positive_freqs = frequencies[:len(frequencies)//2]
    magnitudes = np.abs(fft_result[:len(fft_result)//2])
    
    # Find peaks (local maxima)
    peaks = []
    for i in range(1, len(magnitudes)-1):
        if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
            if magnitudes[i] > np.max(magnitudes) * 0.1:  # Only significant peaks
                peaks.append((positive_freqs[i], magnitudes[i]))
    
    # Sort peaks by magnitude
    peaks.sort(key=lambda x: x[1], reverse=True)
    
    return peaks, positive_freqs, magnitudes

def frequency_to_note(freq):
    """Convert frequency to musical note"""
    if freq <= 0:
        return "Unknown"
    
    # A4 = 440 Hz
    a4 = 440.0
    c0 = a4 * (2 ** (-4.75))  # C0 frequency
    
    # Calculate semitones from C0
    semitones = 12 * np.log2(freq / c0)
    
    # Note names
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Calculate octave and note
    octave = int(semitones // 12)
    note_index = int(semitones % 12)
    
    if 0 <= note_index < len(note_names):
        return f"{note_names[note_index]}{octave}"
    else:
        return "Unknown"

def audio_callback(indata, outdata, frames, time, status):
    """Audio callback for testing"""
    if status:
        print(f"Status: {status}")
    
    if indata is not None and len(indata) > 0:
        # Convert to mono if needed
        if indata.ndim == 2:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata.flatten()
        
        # Calculate audio levels
        max_level = np.max(np.abs(audio_data))
        rms_level = np.sqrt(np.mean(audio_data**2))
        
        # Only analyze if there's significant audio
        if max_level > 0.01:
            print(f"\n🎸 Audio detected! Max: {max_level:.4f}, RMS: {rms_level:.4f}")
            
            # Analyze frequency content
            peaks, freqs, mags = analyze_audio(audio_data)
            
            print("🔍 Top frequency peaks:")
            for i, (freq, magnitude) in enumerate(peaks[:10]):  # Show top 10 peaks
                note = frequency_to_note(freq)
                normalized_mag = magnitude / np.max(mags)
                print(f"   {i+1:2d}. {freq:6.1f} Hz -> {note:4s} (strength: {normalized_mag:.3f})")
            
            print("-" * 50)
    
    # Output silence
    if outdata is not None:
        outdata.fill(0)

def main():
    """Main test function"""
    print("🎸 Guitar Audio Input Test")
    print("=" * 50)
    print("This will show the raw frequency spectrum of your guitar input.")
    print("Play a chord and watch the frequency peaks!")
    print("Press Ctrl+C to stop.")
    print()
    
    try:
        # Create audio stream
        with sd.Stream(
            channels=(1, 1),
            samplerate=48000,
            blocksize=2048,
            dtype=np.float32,
            latency='high',
            callback=audio_callback
        ) as stream:
            print("✅ Audio stream started!")
            print("🎵 Play your guitar now...")
            
            # Keep running
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
