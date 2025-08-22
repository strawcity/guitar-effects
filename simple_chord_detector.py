#!/usr/bin/env python3
"""
Simple but Effective Chord Detector
Uses FFT analysis with optimized parameters for guitar chord detection
"""

import numpy as np
import time
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class SimpleChordDetector:
    """Simple but effective chord detector optimized for guitar"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Optimized FFT parameters for guitar
        self.window_size = 4096
        self.hop_length = 1024
        self.overlap = 75  # 75% overlap for better frequency resolution
        
        # Guitar frequency range (E2 to E6)
        self.min_freq = 80   # Hz
        self.max_freq = 1320 # Hz
        
        # Note frequencies for guitar range
        self.note_frequencies = {
            'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00,
            'A#2': 116.54, 'B2': 123.47, 'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56,
            'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00,
            'A#3': 233.08, 'B3': 246.94, 'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
            'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
            'A#4': 466.16, 'B4': 493.88, 'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
            'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00,
            'A#5': 932.33, 'B5': 987.77, 'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51,
            'E6': 1318.51
        }
        
        # Guitar string frequencies
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        # Common chord patterns
        self.chord_patterns = {
            'major': [0, 4, 7],      # Root, major third, perfect fifth
            'minor': [0, 3, 7],      # Root, minor third, perfect fifth
            'major7': [0, 4, 7, 11], # Root, major third, perfect fifth, major seventh
            'minor7': [0, 3, 7, 10], # Root, minor third, perfect fifth, minor seventh
            'dominant7': [0, 4, 7, 10], # Root, major third, perfect fifth, minor seventh
            'sus2': [0, 2, 7],      # Root, major second, perfect fifth
            'sus4': [0, 5, 7],      # Root, perfect fourth, perfect fifth
            'dim': [0, 3, 6],       # Root, minor third, diminished fifth
            'aug': [0, 4, 8],       # Root, major third, augmented fifth
            'power': [0, 7]         # Power chord (root + fifth)
        }
        
        print(f"🎸 Simple Chord Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎯 Window size: {self.window_size}, Overlap: {self.overlap}%")
        print(f"🎵 Frequency range: {self.min_freq}-{self.max_freq} Hz")
    
    def detect_chord_from_audio(self, audio_data: np.ndarray) -> Dict:
        """
        Detect chord from audio data using optimized FFT analysis
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dictionary with chord information
        """
        try:
            # Check audio level threshold
            audio_level = np.max(np.abs(audio_data))
            if audio_level < 0.005:  # Too weak for meaningful detection
                return self._empty_chord_result()
            
            # Find dominant frequencies
            frequencies = self._extract_frequencies(audio_data)
            
            if not frequencies:
                return self._empty_chord_result()
            
            # Convert frequencies to notes
            detected_notes = self._frequencies_to_notes(frequencies)
            
            if len(detected_notes) < 3:
                return self._empty_chord_result()
            
            # Analyze chord structure
            chord_info = self._analyze_chord_structure(detected_notes)
            
            # Calculate confidence
            confidence = self._calculate_confidence(audio_level, detected_notes)
            
            return {
                'root': chord_info['root'],
                'quality': chord_info['quality'],
                'notes': chord_info['notes'],
                'note_details': detected_notes,
                'confidence': confidence,
                'valid': True,
                'timestamp': time.time(),
                'chord_notation': chord_info['notation'],
                'detection_method': 'simple_fft'
            }
            
        except Exception as e:
            print(f"❌ Simple chord detection error: {e}")
            return self._empty_chord_result()
    
    def _extract_frequencies(self, audio_data: np.ndarray) -> List[Dict]:
        """Extract dominant frequencies using FFT"""
        try:
            # Ensure audio data is the right length
            if len(audio_data) < self.window_size:
                # Pad with zeros if too short
                padded_audio = np.pad(audio_data, (0, self.window_size - len(audio_data)))
            else:
                # Use the first window_size samples
                padded_audio = audio_data[:self.window_size]
            
            # Apply Hann window to reduce spectral leakage
            window = np.hanning(self.window_size)
            windowed_audio = padded_audio * window
            
            # Perform FFT
            fft_result = np.fft.fft(windowed_audio)
            magnitude = np.abs(fft_result)
            
            # Convert to frequency domain
            freqs = np.fft.fftfreq(self.window_size, 1.0 / self.sample_rate)
            
            # Filter to guitar frequency range
            guitar_mask = (freqs >= self.min_freq) & (freqs <= self.max_freq)
            guitar_freqs = freqs[guitar_mask]
            guitar_magnitudes = magnitude[guitar_mask]
            
            # Find peaks (dominant frequencies)
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(
                guitar_magnitudes,
                height=np.max(guitar_magnitudes) * 0.1,  # 10% of max
                distance=10,  # Minimum distance between peaks
                prominence=np.max(guitar_magnitudes) * 0.05  # 5% prominence
            )
            
            # Sort peaks by magnitude
            if len(peaks) > 0:
                peak_freqs = guitar_freqs[peaks]
                peak_magnitudes = guitar_magnitudes[peaks]
                
                # Sort by magnitude (strongest first)
                sorted_indices = np.argsort(peak_magnitudes)[::-1]
                
                # Return top frequencies
                frequencies = []
                for i in sorted_indices[:8]:  # Top 8 frequencies
                    frequencies.append({
                        'frequency': peak_freqs[i],
                        'magnitude': peak_magnitudes[i]
                    })
                
                return frequencies
            
            return []
            
        except Exception as e:
            print(f"⚠️  Frequency extraction error: {e}")
            return []
    
    def _frequencies_to_notes(self, frequencies: List[Dict]) -> List[Dict]:
        """Convert frequencies to musical notes"""
        notes = []
        
        for freq_info in frequencies:
            frequency = freq_info['frequency']
            magnitude = freq_info['magnitude']
            
            # Find closest note
            closest_note = self._find_closest_note(frequency)
            
            if closest_note and abs(closest_note['cents_off']) < 100:  # Within 100 cents
                # Identify guitar string
                string_info = self._identify_guitar_string(frequency)
                
                notes.append({
                    'note': closest_note['note'],
                    'octave': closest_note['octave'],
                    'frequency': frequency,
                    'strength': magnitude,
                    'cents_off': closest_note['cents_off'],
                    'tuning_status': self._get_tuning_status(closest_note['cents_off']),
                    'guitar_string': string_info,
                    'detection_method': 'simple_fft'
                })
        
        # Remove duplicate notes (keep strongest)
        unique_notes = {}
        for note in notes:
            note_name = note['note']
            if note_name not in unique_notes or note['strength'] > unique_notes[note_name]['strength']:
                unique_notes[note_name] = note
        
        return list(unique_notes.values())
    
    def _find_closest_note(self, frequency: float) -> Optional[Dict]:
        """Find the closest musical note to a frequency"""
        if frequency <= 0:
            return None
        
        closest_match = None
        smallest_difference = float('inf')
        
        for note_name, note_freq in self.note_frequencies.items():
            difference = abs(frequency - note_freq)
            
            if difference < smallest_difference:
                smallest_difference = difference
                
                # Calculate cents (musical pitch difference)
                cents_off = 1200 * np.log2(frequency / note_freq)
                
                # Extract octave from note name
                octave = int(note_name[-1])
                
                closest_match = {
                    'note': note_name[:-1],  # Remove octave number
                    'octave': octave,
                    'frequency': note_freq,
                    'cents_off': cents_off,
                    'difference': difference
                }
        
        return closest_match
    
    def _identify_guitar_string(self, frequency: float) -> Optional[Dict]:
        """Identify which guitar string could produce this frequency"""
        for string_name, string_freq in self.guitar_strings.items():
            # Check if frequency is close to this string (within 100 cents)
            cents_diff = 1200 * np.log2(frequency / string_freq)
            if abs(cents_diff) < 100:
                return {
                    'string': string_name,
                    'expected_freq': string_freq,
                    'difference': frequency - string_freq,
                    'cents_off': cents_diff
                }
        return None
    
    def _get_tuning_status(self, cents_off: float) -> str:
        """Get tuning status based on cents off"""
        if abs(cents_off) < 20:
            return 'in tune'
        elif abs(cents_off) < 50:
            return 'slightly off'
        else:
            return 'out of tune'
    
    def _analyze_chord_structure(self, notes: List[Dict]) -> Dict:
        """Analyze detected notes to determine chord structure"""
        if not notes:
            return {'root': 'Unknown', 'quality': 'unknown', 'notes': [], 'notation': 'N'}
        
        # Sort notes by frequency (lowest first)
        sorted_notes = sorted(notes, key=lambda x: x['frequency'])
        
        # Get note names
        note_names = [note['note'] for note in sorted_notes]
        
        # Find root (lowest frequency)
        root = note_names[0] if note_names else 'Unknown'
        
        # Analyze intervals from root
        intervals = []
        root_freq = sorted_notes[0]['frequency']
        
        for note in sorted_notes[1:]:
            # Calculate semitones from root
            semitones = 12 * np.log2(note['frequency'] / root_freq)
            intervals.append(round(semitones))
        
        # Determine chord quality based on intervals
        quality = self._determine_chord_quality(intervals)
        
        # Generate chord notation
        notation = self._generate_chord_notation(root, quality)
        
        return {
            'root': root,
            'quality': quality,
            'notes': note_names,
            'notation': notation
        }
    
    def _determine_chord_quality(self, intervals: List[int]) -> str:
        """Determine chord quality from intervals"""
        if not intervals:
            return 'unknown'
        
        # Sort intervals for comparison
        sorted_intervals = sorted(intervals)
        
        # Check common chord patterns
        if sorted_intervals == [4, 7]:
            return 'major'
        elif sorted_intervals == [3, 7]:
            return 'minor'
        elif sorted_intervals == [4, 7, 11]:
            return 'major7'
        elif sorted_intervals == [3, 7, 10]:
            return 'minor7'
        elif sorted_intervals == [4, 7, 10]:
            return 'dominant7'
        elif sorted_intervals == [2, 7]:
            return 'sus2'
        elif sorted_intervals == [5, 7]:
            return 'sus4'
        elif sorted_intervals == [3, 6]:
            return 'diminished'
        elif sorted_intervals == [4, 8]:
            return 'augmented'
        elif sorted_intervals == [7]:
            return 'power'
        else:
            return 'unknown'
    
    def _generate_chord_notation(self, root: str, quality: str) -> str:
        """Generate chord notation string"""
        if quality == 'unknown':
            return root
        
        if quality == 'major':
            return root
        elif quality == 'minor':
            return f"{root}m"
        elif quality == 'major7':
            return f"{root}maj7"
        elif quality == 'minor7':
            return f"{root}m7"
        elif quality == 'dominant7':
            return f"{root}7"
        elif quality == 'sus2':
            return f"{root}sus2"
        elif quality == 'sus4':
            return f"{root}sus4"
        elif quality == 'diminished':
            return f"{root}dim"
        elif quality == 'augmented':
            return f"{root}aug"
        elif quality == 'power':
            return f"{root}5"
        else:
            return root
    
    def _calculate_confidence(self, audio_level: float, notes: List[Dict]) -> float:
        """Calculate confidence based on audio level and note count"""
        # Base confidence from audio level
        level_confidence = min(audio_level * 50, 1.0)
        
        # Note count confidence (more notes = higher confidence)
        note_confidence = min(len(notes) / 6.0, 1.0)
        
        # Average note strength confidence
        if notes:
            avg_strength = np.mean([note['strength'] for note in notes])
            strength_confidence = min(avg_strength / 0.5, 1.0)
        else:
            strength_confidence = 0
        
        # Combine factors
        final_confidence = (level_confidence + note_confidence + strength_confidence) / 3
        
        return min(final_confidence, 1.0)
    
    def _empty_chord_result(self) -> Dict:
        """Return empty chord result"""
        return {
            'root': 'Unknown',
            'quality': 'unknown',
            'notes': [],
            'note_details': [],
            'confidence': 0.0,
            'valid': False,
            'timestamp': 0,
            'chord_notation': 'N',
            'detection_method': 'none'
        }
    
    def test_detection(self, duration: float = 3.0) -> None:
        """Test the chord detection with live audio"""
        try:
            import sounddevice as sd
            
            print(f"🎤 Testing simple chord detection for {duration} seconds...")
            print("🎸 Play a chord on your guitar!")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            
            sd.wait()
            
            # Detect chord
            chord_result = self.detect_chord_from_audio(audio_data.flatten())
            
            if chord_result['valid']:
                print(f"\n🎯 Chord detected: {chord_result['root']} {chord_result['quality']}")
                print(f"   Notes: {chord_result['notes']}")
                print(f"   Confidence: {chord_result['confidence']:.2f}")
                print(f"   Notation: {chord_result['chord_notation']}")
            else:
                print("\n❌ No chord detected")
                
        except ImportError:
            print("❌ sounddevice not available for testing")
        except Exception as e:
            print(f"❌ Test error: {e}")

def main():
    """Test the simple chord detector"""
    detector = SimpleChordDetector()
    print("🎸 Simple Chord Detector ready!")
    print("💡 This detector uses optimized FFT analysis for reliable chord recognition")
    print("💡 No external dependencies required!")

if __name__ == "__main__":
    main()
