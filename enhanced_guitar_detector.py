#!/usr/bin/env python3
"""
Enhanced Guitar Note Detection System

Based on piano key frequencies and equal temperament tuning principles.
Uses the A4 = 440 Hz reference and calculates all frequencies using
the twelfth root of 2 (approximately 1.059463) for each semitone.

This system provides accurate note detection for guitar by:
1. Using precise mathematical frequency calculations
2. Implementing harmonic analysis for better accuracy
3. Supporting multiple detection methods (FFT, autocorrelation, YIN)
4. Providing real-time tuning feedback
5. Handling guitar-specific frequency ranges and string identification
"""

import numpy as np
import math
import time
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedGuitarDetector:
    """
    Enhanced guitar note detector using piano key frequency principles
    and multiple detection algorithms for maximum accuracy.
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        
        # A4 reference frequency (440 Hz) as per international standard
        self.A4_FREQUENCY = 440.0
        
        # Twelfth root of 2 for equal temperament calculations
        self.SEMITONE_RATIO = 2 ** (1/12)
        
        # Guitar frequency range (E2 to E6)
        self.MIN_FREQ = 80.0   # Hz (E2)
        self.MAX_FREQ = 1320.0 # Hz (E6)
        
        # Initialize note frequency database using piano key principles
        self._initialize_note_frequencies()
        
        # Guitar string information
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        # Detection parameters
        self.window_size = 4096
        self.hop_length = 1024
        self.min_confidence = 0.6
        
        print(f"🎸 Enhanced Guitar Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎯 Frequency range: {self.MIN_FREQ}-{self.MAX_FREQ} Hz")
        print(f"🎵 A4 reference: {self.A4_FREQUENCY} Hz")
        print(f"🔧 Semitone ratio: {self.SEMITONE_RATIO:.6f}")
    
    def _initialize_note_frequencies(self):
        """Initialize note frequencies using equal temperament principles"""
        self.note_frequencies = {}
        
        # Chromatic scale starting from C
        chromatic_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Calculate frequencies for octaves 2-6 (guitar range)
        for octave in range(2, 7):
            for note_index, note_name in enumerate(chromatic_notes):
                # Calculate semitones from A4 (49th key in piano)
                # A4 is in octave 4, note index 9 (A)
                a4_octave = 4
                a4_note_index = 9
                
                # Calculate semitones difference
                octave_diff = octave - a4_octave
                note_diff = note_index - a4_note_index
                total_semitones = octave_diff * 12 + note_diff
                
                # Calculate frequency using the formula: f(n) = 2^(n/12) * 440 Hz
                frequency = self.A4_FREQUENCY * (self.SEMITONE_RATIO ** total_semitones)
                
                # Store with octave notation
                note_key = f"{note_name}{octave}"
                self.note_frequencies[note_key] = frequency
    
    def detect_note_from_audio(self, audio_data: np.ndarray) -> Dict:
        """
        Detect the primary note from audio data using multiple algorithms
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dictionary with note information
        """
        try:
            # Check audio level
            audio_level = np.max(np.abs(audio_data))
            if audio_level < 0.005:
                return self._empty_note_result()
            
            # Try multiple detection methods for better accuracy
            detection_results = []
            
            # Method 1: Enhanced FFT with harmonic analysis
            fft_result = self._fft_detection(audio_data)
            if fft_result and fft_result['confidence'] > 0.3:
                detection_results.append(fft_result)
            
            # Method 2: Autocorrelation for fundamental frequency
            autocorr_result = self._autocorrelation_detection(audio_data)
            if autocorr_result and autocorr_result['confidence'] > 0.3:
                detection_results.append(autocorr_result)
            
            # Method 3: YIN algorithm for pitch detection
            yin_result = self._yin_detection(audio_data)
            if yin_result and yin_result['confidence'] > 0.3:
                detection_results.append(yin_result)
            
            # Combine results for best detection
            if detection_results:
                best_result = self._combine_detection_results(detection_results)
                return best_result
            
            return self._empty_note_result()
            
        except Exception as e:
            print(f"❌ Note detection error: {e}")
            return self._empty_note_result()
    
    def _fft_detection(self, audio_data: np.ndarray) -> Optional[Dict]:
        """Enhanced FFT detection with harmonic analysis"""
        try:
            # Ensure proper window size
            if len(audio_data) < self.window_size:
                padded_audio = np.pad(audio_data, (0, self.window_size - len(audio_data)))
            else:
                padded_audio = audio_data[:self.window_size]
            
            # Apply Hann window
            window = np.hanning(self.window_size)
            windowed_audio = padded_audio * window
            
            # Perform FFT
            fft_result = np.fft.fft(windowed_audio)
            magnitude = np.abs(fft_result)
            
            # Convert to frequency domain
            freqs = np.fft.fftfreq(self.window_size, 1.0 / self.sample_rate)
            
            # Filter to guitar range
            guitar_mask = (freqs >= self.MIN_FREQ) & (freqs <= self.MAX_FREQ)
            guitar_freqs = freqs[guitar_mask]
            guitar_magnitudes = magnitude[guitar_mask]
            
            if len(guitar_magnitudes) == 0:
                return None
            
            # Find peaks
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(
                guitar_magnitudes,
                height=np.max(guitar_magnitudes) * 0.1,
                distance=10,
                prominence=np.max(guitar_magnitudes) * 0.05
            )
            
            if len(peaks) == 0:
                return None
            
            # Analyze harmonics to find fundamental frequency
            fundamental_freq = self._find_fundamental_frequency(guitar_freqs[peaks], guitar_magnitudes[peaks])
            
            if fundamental_freq is None:
                return None
            
            # Convert to note
            note_info = self._frequency_to_note(fundamental_freq)
            if not note_info:
                return None
            
            # Calculate confidence based on harmonic content
            confidence = self._calculate_harmonic_confidence(guitar_freqs[peaks], guitar_magnitudes[peaks], fundamental_freq)
            
            return {
                'frequency': fundamental_freq,
                'note': note_info['note'],
                'octave': note_info['octave'],
                'cents_off': note_info['cents_off'],
                'confidence': confidence,
                'method': 'fft_harmonic',
                'guitar_string': self._identify_guitar_string(fundamental_freq)
            }
            
        except Exception as e:
            print(f"⚠️  FFT detection error: {e}")
            return None
    
    def _autocorrelation_detection(self, audio_data: np.ndarray) -> Optional[Dict]:
        """Autocorrelation-based fundamental frequency detection"""
        try:
            # Normalize audio
            audio_norm = audio_data / np.max(np.abs(audio_data))
            
            # Calculate autocorrelation
            autocorr = np.correlate(audio_norm, audio_norm, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks in autocorrelation
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(
                autocorr,
                height=np.max(autocorr) * 0.3,
                distance=int(self.sample_rate / self.MAX_FREQ)
            )
            
            if len(peaks) < 2:
                return None
            
            # Calculate fundamental frequency from first peak
            fundamental_period = peaks[1] - peaks[0]
            fundamental_freq = self.sample_rate / fundamental_period
            
            # Check if frequency is in guitar range
            if fundamental_freq < self.MIN_FREQ or fundamental_freq > self.MAX_FREQ:
                return None
            
            # Convert to note
            note_info = self._frequency_to_note(fundamental_freq)
            if not note_info:
                return None
            
            # Calculate confidence
            confidence = min(autocorr[peaks[1]] / np.max(autocorr), 1.0)
            
            return {
                'frequency': fundamental_freq,
                'note': note_info['note'],
                'octave': note_info['octave'],
                'cents_off': note_info['cents_off'],
                'confidence': confidence,
                'method': 'autocorrelation',
                'guitar_string': self._identify_guitar_string(fundamental_freq)
            }
            
        except Exception as e:
            print(f"⚠️  Autocorrelation detection error: {e}")
            return None
    
    def _yin_detection(self, audio_data: np.ndarray) -> Optional[Dict]:
        """YIN algorithm for pitch detection"""
        try:
            # YIN algorithm implementation
            fundamental_freq = self._yin_algorithm(audio_data)
            
            if fundamental_freq is None:
                return None
            
            # Convert to note
            note_info = self._frequency_to_note(fundamental_freq)
            if not note_info:
                return None
            
            return {
                'frequency': fundamental_freq,
                'note': note_info['note'],
                'octave': note_info['octave'],
                'cents_off': note_info['cents_off'],
                'confidence': 0.7,  # YIN typically provides good results
                'method': 'yin',
                'guitar_string': self._identify_guitar_string(fundamental_freq)
            }
            
        except Exception as e:
            print(f"⚠️  YIN detection error: {e}")
            return None
    
    def _yin_algorithm(self, audio_data: np.ndarray) -> Optional[float]:
        """Implementation of the YIN pitch detection algorithm"""
        try:
            # Normalize audio
            audio_norm = audio_data / np.max(np.abs(audio_data))
            
            # YIN parameters
            min_freq = self.MIN_FREQ
            max_freq = self.MAX_FREQ
            
            # Calculate minimum and maximum periods
            min_period = int(self.sample_rate / max_freq)
            max_period = int(self.sample_rate / min_freq)
            
            # Calculate difference function
            diff = np.zeros(max_period + 1)
            for tau in range(1, max_period + 1):
                diff[tau] = np.sum((audio_norm[tau:] - audio_norm[:-tau]) ** 2)
            
            # Calculate normalized difference function
            norm_diff = np.zeros(max_period + 1)
            norm_diff[0] = 1
            running_sum = 0
            
            for tau in range(1, max_period + 1):
                running_sum += diff[tau]
                norm_diff[tau] = diff[tau] / ((1/tau) * running_sum)
            
            # Find minimum below threshold
            threshold = 0.1
            min_tau = None
            
            for tau in range(min_period, max_period + 1):
                if norm_diff[tau] < threshold:
                    # Find local minimum
                    while (tau + 1 < len(norm_diff) and 
                           norm_diff[tau + 1] < norm_diff[tau]):
                        tau += 1
                    min_tau = tau
                    break
            
            if min_tau is None:
                return None
            
            # Calculate frequency
            fundamental_freq = self.sample_rate / min_tau
            
            return fundamental_freq
            
        except Exception as e:
            print(f"⚠️  YIN algorithm error: {e}")
            return None
    
    def _find_fundamental_frequency(self, frequencies: np.ndarray, magnitudes: np.ndarray) -> Optional[float]:
        """Find fundamental frequency by analyzing harmonic relationships"""
        if len(frequencies) < 2:
            return frequencies[0] if len(frequencies) == 1 else None
        
        # Sort by magnitude (strongest first)
        sorted_indices = np.argsort(magnitudes)[::-1]
        sorted_freqs = frequencies[sorted_indices]
        sorted_mags = magnitudes[sorted_indices]
        
        # Look for fundamental frequency (lowest strong frequency)
        fundamental_candidates = []
        
        for i, freq in enumerate(sorted_freqs):
            # Check if this frequency has harmonics
            harmonic_count = 0
            for j, other_freq in enumerate(sorted_freqs):
                if i != j:
                    # Check if other_freq is close to a harmonic of freq
                    ratio = other_freq / freq
                    # Allow some tolerance for harmonic ratios
                    if (abs(ratio - round(ratio)) < 0.1 and 
                        round(ratio) >= 2 and round(ratio) <= 8):
                        harmonic_count += 1
            
            # Calculate score based on magnitude and harmonic content
            score = sorted_mags[i] * (1 + harmonic_count * 0.2)
            fundamental_candidates.append((freq, score))
        
        # Return frequency with highest score
        if fundamental_candidates:
            best_candidate = max(fundamental_candidates, key=lambda x: x[1])
            return best_candidate[0]
        
        return sorted_freqs[0]  # Fallback to strongest frequency
    
    def _frequency_to_note(self, frequency: float) -> Optional[Dict]:
        """Convert frequency to note using equal temperament principles"""
        if frequency <= 0:
            return None
        
        # Find closest note
        closest_note = None
        smallest_cents = float('inf')
        
        for note_name, note_freq in self.note_frequencies.items():
            # Calculate cents difference
            cents_diff = 1200 * math.log2(frequency / note_freq)
            
            if abs(cents_diff) < abs(smallest_cents):
                smallest_cents = cents_diff
                closest_note = note_name
        
        if closest_note is None:
            return None
        
        # Extract note name and octave
        note_name = closest_note[:-1]  # Remove octave number
        octave = int(closest_note[-1])
        
        return {
            'note': note_name,
            'octave': octave,
            'cents_off': smallest_cents,
            'expected_frequency': self.note_frequencies[closest_note]
        }
    
    def _identify_guitar_string(self, frequency: float) -> Optional[Dict]:
        """Identify which guitar string could produce this frequency"""
        for string_name, string_freq in self.guitar_strings.items():
            # Check if frequency is close to this string (within 100 cents)
            cents_diff = 1200 * math.log2(frequency / string_freq)
            if abs(cents_diff) < 100:
                return {
                    'string': string_name,
                    'expected_freq': string_freq,
                    'difference': frequency - string_freq,
                    'cents_off': cents_diff
                }
        return None
    
    def _calculate_harmonic_confidence(self, frequencies: np.ndarray, magnitudes: np.ndarray, fundamental: float) -> float:
        """Calculate confidence based on harmonic content"""
        if len(frequencies) < 2:
            return 0.5
        
        # Count harmonics of the fundamental
        harmonic_count = 0
        total_magnitude = 0
        
        for freq, mag in zip(frequencies, magnitudes):
            ratio = freq / fundamental
            # Check if this is a harmonic (within tolerance)
            if abs(ratio - round(ratio)) < 0.1 and round(ratio) >= 1:
                harmonic_count += 1
                total_magnitude += mag
        
        # Calculate confidence based on harmonic content and magnitude
        harmonic_confidence = min(harmonic_count / 4.0, 1.0)  # Max 4 harmonics
        magnitude_confidence = min(total_magnitude / np.max(magnitudes), 1.0)
        
        return (harmonic_confidence + magnitude_confidence) / 2
    
    def _combine_detection_results(self, results: List[Dict]) -> Dict:
        """Combine multiple detection results for best accuracy"""
        if not results:
            return self._empty_note_result()
        
        if len(results) == 1:
            return results[0]
        
        # Weight results by confidence and method reliability
        method_weights = {
            'fft_harmonic': 1.0,
            'autocorrelation': 0.8,
            'yin': 0.9
        }
        
        weighted_results = []
        for result in results:
            weight = method_weights.get(result['method'], 0.5)
            weighted_score = result['confidence'] * weight
            weighted_results.append((result, weighted_score))
        
        # Sort by weighted score
        weighted_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return best result
        best_result = weighted_results[0][0]
        
        # Enhance confidence if multiple methods agree
        if len(results) > 1:
            # Check if top results are similar
            top_freq = best_result['frequency']
            agreeing_methods = 0
            
            for result in results:
                freq_diff = abs(result['frequency'] - top_freq)
                if freq_diff < 10:  # Within 10 Hz
                    agreeing_methods += 1
            
            # Boost confidence for agreement
            if agreeing_methods > 1:
                best_result['confidence'] = min(best_result['confidence'] * 1.2, 1.0)
                best_result['method'] = f"combined_{agreeing_methods}_methods"
        
        return best_result
    
    def _empty_note_result(self) -> Dict:
        """Return empty note result"""
        return {
            'frequency': 0.0,
            'note': 'Unknown',
            'octave': 0,
            'cents_off': 0.0,
            'confidence': 0.0,
            'method': 'none',
            'guitar_string': None
        }
    
    def get_tuning_feedback(self, cents_off: float) -> str:
        """Get tuning feedback based on cents off"""
        if abs(cents_off) < 10:
            return "🎯 Perfect!"
        elif abs(cents_off) < 25:
            return "✅ Very close"
        elif abs(cents_off) < 50:
            return "⚠️  Slightly off"
        elif abs(cents_off) < 100:
            return "❌ Out of tune"
        else:
            return "🚫 Way off"
    
    def test_detection(self, duration: float = 3.0) -> None:
        """Test the note detection with live audio"""
        try:
            import sounddevice as sd
            
            print(f"🎤 Testing enhanced note detection for {duration} seconds...")
            print("🎸 Play a single note on your guitar!")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            
            sd.wait()
            
            # Detect note
            note_result = self.detect_note_from_audio(audio_data.flatten())
            
            if note_result['note'] != 'Unknown':
                print(f"\n🎯 Note detected: {note_result['note']}{note_result['octave']}")
                print(f"   Frequency: {note_result['frequency']:.1f} Hz")
                print(f"   Cents off: {note_result['cents_off']:.1f}")
                print(f"   Tuning: {self.get_tuning_feedback(note_result['cents_off'])}")
                print(f"   Confidence: {note_result['confidence']:.2f}")
                print(f"   Method: {note_result['method']}")
                
                if note_result['guitar_string']:
                    string_info = note_result['guitar_string']
                    print(f"   Guitar string: {string_info['string']}")
            else:
                print("\n❌ No note detected")
                
        except ImportError:
            print("❌ sounddevice not available for testing")
        except Exception as e:
            print(f"❌ Test error: {e}")


def main():
    """Test the enhanced guitar detector"""
    detector = EnhancedGuitarDetector()
    print("🎸 Enhanced Guitar Detector ready!")
    print("💡 Based on piano key frequencies and equal temperament tuning")
    print("💡 Uses multiple detection algorithms for maximum accuracy")
    print("💡 Provides real-time tuning feedback")

if __name__ == "__main__":
    main()
