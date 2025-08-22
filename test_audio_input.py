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
    
    # Find peaks (local maxima) with better filtering
    peaks = []
    for i in range(1, len(magnitudes)-1):
        if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
            # Only peaks above noise threshold
            if magnitudes[i] > np.max(magnitudes) * 0.05:
                peaks.append((positive_freqs[i], magnitudes[i]))
    
    # Filter peaks to only include musical frequencies
    musical_peaks = []
    for freq, magnitude in peaks:
        # Only include frequencies that could be musical notes
        if freq >= 80 and freq <= 1200:  # Guitar range (E2 to E6)
            musical_peaks.append((freq, magnitude))
    
    # Sort peaks by magnitude
    musical_peaks.sort(key=lambda x: x[1], reverse=True)
    
    return musical_peaks, positive_freqs, magnitudes

def frequency_to_note(freq):
    """Convert frequency to musical note with tuning accuracy"""
    if freq <= 0:
        return "Unknown", 0
    
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
        note_name = f"{note_names[note_index]}{octave}"
        
        # Calculate cents deviation from perfect tuning
        perfect_freq = c0 * (2 ** (semitones))
        cents_off = 1200 * np.log2(freq / perfect_freq)
        
        return note_name, cents_off
    else:
        return "Unknown", 0

def get_guitar_string_info(freq):
    """Get information about which guitar string could produce this frequency"""
    # Standard guitar tuning (E2, A2, D3, G3, B3, E4)
    string_frequencies = {
        'E2': 82.41,   # 6th string (thickest)
        'A2': 110.00,  # 5th string
        'D3': 146.83,  # 4th string
        'G3': 196.00,  # 3rd string
        'B3': 246.94,  # 2nd string
        'E4': 329.63   # 1st string (thinnest)
    }
    
    # Find closest string
    closest_string = None
    min_diff = float('inf')
    
    for string, string_freq in string_frequencies.items():
        diff = abs(freq - string_freq)
        if diff < min_diff:
            min_diff = diff
            closest_string = string
    
    return closest_string, string_frequencies.get(closest_string, 0)

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
            
            print("🔍 Top musical frequency peaks:")
            for i, (freq, magnitude) in enumerate(peaks[:8]):  # Show top 8 peaks
                note, cents_off = frequency_to_note(freq)
                normalized_mag = magnitude / np.max(mags)
                
                # Color code tuning accuracy
                if abs(cents_off) < 10:
                    tuning_status = "✅ In tune"
                elif abs(cents_off) < 25:
                    tuning_status = "⚠️  Slightly off"
                else:
                    tuning_status = "❌ Out of tune"
                
                # Get guitar string info
                string_info, expected_freq = get_guitar_string_info(freq)
                
                print(f"   {i+1:2d}. {freq:6.1f} Hz -> {note:4s} (strength: {normalized_mag:.3f})")
                print(f"       Tuning: {cents_off:+6.1f} cents {tuning_status}")
                if string_info and abs(freq - expected_freq) < 50:  # Within 50 Hz
                    print(f"       Guitar: {string_info} (expected: {expected_freq:.1f} Hz)")
            
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
    print("📚 Expected frequencies for common guitar notes:")
    print("   Open strings:")
    print("     E2 (6th): 82.4 Hz    A2 (5th): 110.0 Hz")
    print("     D3 (4th): 146.8 Hz   G3 (3rd): 196.0 Hz")
    print("     B3 (2nd): 246.9 Hz   E4 (1st): 329.6 Hz")
    print()
    print("   Common fretted notes:")
    print("     C3 (5th string, 3rd fret): 130.8 Hz")
    print("     C4 (2nd string, 1st fret): 261.6 Hz")
    print("     G3 (6th string, 3rd fret): 196.0 Hz")
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
