#!/usr/bin/env python3
"""
Specialized guitar tuner algorithm for accurate note detection
Uses harmonic analysis and peak clustering similar to professional guitar tuners
"""

import numpy as np
from scipy import signal
from scipy.fft import fft
import math

class GuitarTuner:
    def __init__(self, sample_rate=48000):
        # Optimize sample rate for guitar detection
        # 44.1kHz is sufficient and more standard for audio
        if sample_rate > 44100:
            self.sample_rate = 44100
            print(f"⚠️  Sample rate reduced from {sample_rate} to 44100 Hz for optimal guitar detection")
        else:
            self.sample_rate = sample_rate
        
        # Calculate frequency resolution
        self.window_size = 4096
        self.freq_resolution = self.sample_rate / self.window_size
        print(f"📊 Frequency resolution: {self.freq_resolution:.1f} Hz (window: {self.window_size} samples)")
        
        # Anti-aliasing: Nyquist frequency should be well above guitar range
        self.nyquist_freq = self.sample_rate / 2
        if self.nyquist_freq < 1200:
            print(f"⚠️  Warning: Sample rate may be too low for guitar detection")
        else:
            print(f"✅ Sample rate adequate: Nyquist at {self.nyquist_freq:.0f} Hz")
        
        # Guitar string fundamental frequencies (open strings)
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        # Note frequencies for all 12 chromatic notes
        self.note_frequencies = {
            'C': [65.41, 130.81, 261.63, 523.25, 1046.50],
            'C#': [69.30, 138.59, 277.18, 554.37, 1108.73],
            'D': [73.42, 146.83, 293.66, 587.33, 1174.66],
            'D#': [77.78, 155.56, 311.13, 622.25, 1244.51],
            'E': [82.41, 164.81, 329.63, 659.25, 1318.51],
            'F': [87.31, 174.61, 349.23, 698.46, 1396.91],
            'F#': [92.50, 185.00, 369.99, 739.99, 1479.98],
            'G': [98.00, 196.00, 392.00, 783.99, 1567.98],
            'G#': [103.83, 207.65, 415.30, 830.61, 1661.22],
            'A': [110.00, 220.00, 440.00, 880.00, 1760.00],
            'A#': [116.54, 233.08, 466.16, 932.33, 1864.66],
            'B': [123.47, 246.94, 493.88, 987.77, 1975.53]
        }
        
        # Guitar-specific harmonic ratios (fundamental + overtones)
        self.harmonic_ratios = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]  # Fundamental + 5 harmonics
        
    def detect_note(self, audio_data):
        """Main note detection using guitar-optimized algorithm"""
        try:
            # Apply multiple analysis windows for better accuracy
            windows = self.create_analysis_windows(audio_data)
            
            # Analyze each window
            window_results = []
            for window_data in windows:
                result = self.analyze_window(window_data)
                if result:
                    window_results.append(result)
            
            if not window_results:
                return None
            
            # Combine results from multiple windows
            final_result = self.combine_window_results(window_results)
            
            return final_result
            
        except Exception as e:
            print(f"Note detection error: {e}")
            return None
    
    def create_analysis_windows(self, audio_data):
        """Create multiple overlapping analysis windows with optimized sizes"""
        windows = []
        
        # Use larger windows for better low-frequency resolution
        # At 48kHz: 4096 samples = ~11.7 Hz resolution (much better for guitar)
        # At 44.1kHz: 4096 samples = ~10.8 Hz resolution
        window_size = min(4096, len(audio_data))
        
        if len(audio_data) < window_size:
            return [audio_data]
        
        # Create overlapping windows for better frequency resolution
        # 75% overlap for maximum resolution
        overlap = window_size // 4
        for start in range(0, len(audio_data) - window_size + 1, overlap):
            window = audio_data[start:start + window_size]
            windows.append(window)
        
        return windows
    
    def analyze_window(self, window_data):
        """Analyze a single window using harmonic analysis with anti-aliasing"""
        # Apply low-pass filter to prevent aliasing (cutoff at 1.5kHz)
        if len(window_data) > 4:
            # Design a low-pass filter
            cutoff_freq = 1500  # Hz
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            
            # Create Butterworth filter
            b, a = signal.butter(4, normalized_cutoff, btype='low')
            filtered_audio = signal.filtfilt(b, a, window_data)
        else:
            filtered_audio = window_data
        
        # Apply Hann window to reduce spectral leakage
        window = signal.windows.hann(len(filtered_audio))
        windowed_audio = filtered_audio * window
        
        # Perform FFT
        fft_result = fft(windowed_audio)
        frequencies = np.fft.fftfreq(len(fft_result), 1/self.sample_rate)
        magnitudes = np.abs(fft_result)
        
        # Focus on guitar frequency range (80-1200 Hz) with better low-end resolution
        # Lower bound reduced for better detection of low E string
        mask = (frequencies > 60) & (frequencies < 1200)
        guitar_freqs = frequencies[mask]
        guitar_mags = magnitudes[mask]
        
        if len(guitar_mags) == 0:
            return None
        
        # Find peaks with guitar-specific filtering
        peaks = self.find_guitar_peaks(guitar_freqs, guitar_mags)
        
        if not peaks:
            return None
        
        # Analyze harmonics for each peak
        harmonic_analysis = self.analyze_harmonics(peaks)
        
        return harmonic_analysis
    
    def find_guitar_peaks(self, frequencies, magnitudes):
        """Find peaks optimized for guitar frequencies"""
        # Adaptive threshold based on signal strength
        max_mag = np.max(magnitudes)
        threshold = max_mag * 0.1  # 10% of maximum
        
        # Find peaks with guitar-specific parameters
        peaks, properties = signal.find_peaks(
            magnitudes,
            height=threshold,
            distance=5,  # Minimum separation for guitar notes
            prominence=threshold * 0.3
        )
        
        # Get peak data
        peak_data = []
        for i in peaks:
            freq = frequencies[i]
            mag = magnitudes[i]
            
            # Only include peaks that could be guitar notes
            if self.is_guitar_frequency(freq):
                peak_data.append({
                    'frequency': freq,
                    'magnitude': mag,
                    'index': i
                })
        
        # Sort by magnitude
        peak_data.sort(key=lambda x: x['magnitude'], reverse=True)
        
        return peak_data[:8]  # Top 8 peaks
    
    def is_guitar_frequency(self, frequency):
        """Check if frequency could be produced by a guitar"""
        # Check if it's close to any guitar string frequency
        for string_freq in self.guitar_strings.values():
            # Allow for tuning variations (±50 Hz)
            if abs(frequency - string_freq) < 50:
                return True
            
            # Check harmonics of guitar strings
            for harmonic in self.harmonic_ratios[1:]:  # Skip fundamental
                harmonic_freq = string_freq * harmonic
                if abs(frequency - harmonic_freq) < 50:
                    return True
        
        return False
    
    def analyze_harmonics(self, peaks):
        """Analyze harmonic relationships between peaks"""
        if len(peaks) < 2:
            return None
        
        # Group peaks by harmonic relationships
        harmonic_groups = []
        
        for i, peak in enumerate(peaks):
            fundamental_freq = peak['frequency']
            group = [peak]
            
            # Look for harmonics of this fundamental
            for other_peak in peaks[i+1:]:
                ratio = other_peak['frequency'] / fundamental_freq
                
                # Check if this is a harmonic (within 5% tolerance)
                for harmonic in self.harmonic_ratios:
                    if abs(ratio - harmonic) < 0.05:
                        group.append(other_peak)
                        break
            
            if len(group) > 1:  # At least fundamental + 1 harmonic
                harmonic_groups.append({
                    'fundamental': fundamental_freq,
                    'harmonics': group,
                    'strength': sum(p['magnitude'] for p in group)
                })
        
        if not harmonic_groups:
            return None
        
        # Find the strongest harmonic group
        best_group = max(harmonic_groups, key=lambda x: x['strength'])
        
        # Determine the most likely note
        note_info = self.identify_note_from_fundamental(best_group['fundamental'])
        
        return {
            'note': note_info['note'],
            'octave': note_info['octave'],
            'frequency': best_group['fundamental'],
            'confidence': note_info['confidence'],
            'cents_off': note_info['cents_off'],
            'harmonic_count': len(best_group['harmonics']),
            'total_strength': best_group['strength']
        }
    
    def identify_note_from_fundamental(self, frequency):
        """Identify the most likely note from fundamental frequency"""
        best_match = None
        best_score = float('inf')
        
        for note_name, octave_frequencies in self.note_frequencies.items():
            for octave_index, note_freq in enumerate(octave_frequencies):
                # Calculate cents deviation
                cents_off = 1200 * math.log2(frequency / note_freq)
                
                # Score based on cents deviation and octave preference
                # Lower octaves (guitar range) get preference
                octave_penalty = abs(octave_index - 2) * 50  # Prefer octave 2-3
                score = abs(cents_off) + octave_penalty
                
                if score < best_score:
                    best_score = score
                    best_match = {
                        'note': note_name,
                        'octave': octave_index + 2,
                        'frequency': note_freq,
                        'cents_off': cents_off,
                        'confidence': max(0, 1 - abs(cents_off) / 100)  # Higher confidence for better tuning
                    }
        
        return best_match
    
    def combine_window_results(self, window_results):
        """Combine results from multiple analysis windows"""
        if not window_results:
            return None
        
        # Group results by note
        note_groups = {}
        for result in window_results:
            note_key = f"{result['note']}{result['octave']}"
            if note_key not in note_groups:
                note_groups[note_key] = []
            note_groups[note_key].append(result)
        
        # Find the most consistent note across windows
        best_note = None
        best_consistency = 0
        
        for note_key, results in note_groups.items():
            if len(results) > best_consistency:
                best_consistency = len(results)
                best_note = results[0]
        
        # Calculate average confidence and cents deviation
        if best_note:
            avg_confidence = np.mean([r['confidence'] for r in note_groups[best_note['note'] + str(best_note['octave'])]])
            avg_cents = np.mean([r['cents_off'] for r in note_groups[best_note['note'] + str(best_note['octave'])]])
            
            best_note['confidence'] = avg_confidence
            best_note['cents_off'] = avg_cents
        
        return best_note

# Test function
def test_guitar_tuner():
    """Test the guitar tuner with synthetic audio"""
    tuner = GuitarTuner()
    
    # Generate a test C note (C3 = 130.81 Hz)
    sample_rate = 48000
    duration = 0.1  # 100ms
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # C3 fundamental + harmonics
    c3_fundamental = 130.81
    c3_harmonics = [c3_fundamental * h for h in [1, 2, 3, 4, 5]]
    
    # Create audio with harmonics
    audio = np.zeros_like(t)
    for i, freq in enumerate(c3_harmonics):
        amplitude = 1.0 / (i + 1)  # Decreasing amplitude for harmonics
        audio += amplitude * np.sin(2 * np.pi * freq * t)
    
    # Add some noise
    audio += np.random.normal(0, 0.1, len(audio))
    
    # Detect the note
    result = tuner.detect_note(audio)
    
    if result:
        print(f"✅ Detected: {result['note']}{result['octave']}")
        print(f"   Frequency: {result['frequency']:.1f} Hz")
        print(f"   Cents off: {result['cents_off']:+.1f}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Harmonics: {result['harmonic_count']}")
    else:
        print("❌ No note detected")

if __name__ == "__main__":
    test_guitar_tuner()
