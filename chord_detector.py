import numpy as np
from scipy import signal
import math
import time
from polyphonic_chord_detector import PolyphonicChordDetector

class ChordDetector:
    def __init__(self, config):
        self.config = config
        self.sample_rate = config.sample_rate
        self.chunk_size = config.chunk_size
        
        # Initialize the polyphonic chord detector for accurate chord detection
        # Use optimized sample rate for better frequency resolution
        optimal_sample_rate = min(self.sample_rate, 44100)
        self.chord_detector = PolyphonicChordDetector(optimal_sample_rate)
        
        # Note frequencies for all 12 chromatic notes across guitar range
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
        
        # Common chord patterns (intervals from root)
        self.chord_patterns = {
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'major7': [0, 4, 7, 11],
            'minor7': [0, 3, 7, 10],
            'dominant7': [0, 4, 7, 10],
            'sus2': [0, 2, 7],
            'sus4': [0, 5, 7],
            'dim': [0, 3, 6],
            'aug': [0, 4, 8],
            'add9': [0, 4, 7, 14],
            'power': [0, 7]  # Power chord (root + fifth)
        }
        
        self.chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Standard guitar tuning for string identification
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
    
    def detect_chord(self, audio_data):
        """Main chord detection function"""
        try:
            # Find dominant frequencies in the audio
            frequencies = self.find_frequencies_in_audio(audio_data)
            
            # Convert frequencies to musical notes
            detected_notes = self.frequencies_to_notes(frequencies)
            
            # Analyze what chord these notes form
            chord_analysis = self.analyze_chord_from_notes(detected_notes)
            
            return {
                'root': chord_analysis.get('root'),
                'quality': chord_analysis.get('quality'),
                'notes': [note['note'] for note in detected_notes],
                'note_details': detected_notes,
                'confidence': chord_analysis.get('confidence', 0),
                'timestamp': time.time(),
                'valid': chord_analysis.get('confidence', 0) > self.config.min_chord_confidence
            }
            
        except Exception as e:
            print(f"Chord detection error: {e}")
            return self.empty_chord_result()
    
    def find_frequencies_in_audio(self, audio_data):
        """Extract dominant frequencies using polyphonic chord detector"""
        # Convert to numpy array and normalize
        audio_array = np.array(audio_data, dtype=np.float32)
        if len(audio_array) == 0:
            return []
        
        try:
            # Use the polyphonic chord detector for accurate chord detection
            chord_result = self.chord_detector.detect_chord_polyphonic(audio_array)
            
            if chord_result and chord_result.get('valid'):
                # Convert chord result to frequency data format
                frequency_data = []
                for note in chord_result.get('note_details', []):
                    frequency_data.append({
                        'frequency': note['frequency'],
                        'magnitude': note['magnitude'],
                        'note_info': note
                    })
                return frequency_data
            
        except Exception as e:
            print(f"⚠️  Polyphonic chord detector failed: {e}")
        
        # Fallback to basic FFT if detector fails
        return self._fallback_fft_analysis(audio_array)
    
    def _fallback_fft_analysis(self, audio_array):
        """Fallback to basic FFT if guitar tuner fails"""
        # Apply Hann window to reduce spectral leakage
        window = signal.windows.hann(len(audio_array))
        windowed_audio = audio_array * window
        
        # Perform FFT
        fft_result = np.fft.fft(windowed_audio)
        magnitude = np.abs(fft_result)
        
        # Create frequency bins
        frequencies = np.fft.fftfreq(len(fft_result), 1/self.sample_rate)
        
        # Only keep positive frequencies in guitar range (80-1200 Hz)
        mask = (frequencies > 80) & (frequencies < 1200)
        guitar_frequencies = frequencies[mask]
        guitar_magnitudes = magnitude[mask]
        
        if len(guitar_magnitudes) == 0:
            return []
        
        # Find peaks with basic filtering
        threshold = np.max(guitar_magnitudes) * 0.05
        peaks, properties = signal.find_peaks(
            guitar_magnitudes,
            height=threshold,
            distance=8,
            prominence=threshold * 0.4
        )
        
        # Get peak frequencies and magnitudes
        peak_frequencies = guitar_frequencies[peaks]
        peak_magnitudes = guitar_magnitudes[peaks]
        
        # Sort by magnitude
        sorted_indices = np.argsort(peak_magnitudes)[::-1]
        
        # Return top 6 frequencies
        dominant_frequencies = []
        for i in sorted_indices[:6]:
            dominant_frequencies.append({
                'frequency': peak_frequencies[i],
                'magnitude': peak_magnitudes[i]
            })
        
        return dominant_frequencies
    
    def frequencies_to_notes(self, frequency_data):
        """Convert frequencies to musical note names using professional detector when available"""
        detected_notes = []
        
        for freq_info in frequency_data:
            frequency = freq_info['frequency']
            magnitude = freq_info['magnitude']
            
            # Check if we have professional detector results
            if 'note_info' in freq_info and freq_info['note_info']:
                detector_result = freq_info['note_info']
                detected_notes.append({
                    'note': detector_result['note'],
                    'octave': detector_result['octave'],
                    'frequency': frequency,
                    'strength': magnitude,
                    'cents_off': detector_result['cents_off'],
                    'confidence': 0.8,  # Professional detector confidence
                    'harmonic_count': 1,  # Simplified for now
                    'guitar_string': detector_result.get('guitar_string', self.identify_guitar_string(frequency))
                })
            else:
                # Fall back to basic note detection
                closest_note = self.find_closest_note(frequency)
                
                if closest_note and abs(closest_note['cents_off']) < 100:
                    detected_notes.append({
                        'note': closest_note['note'],
                        'octave': closest_note['octave'],
                        'frequency': frequency,
                        'strength': magnitude,
                        'cents_off': closest_note['cents_off'],
                        'confidence': 0.5,  # Lower confidence for basic detection
                        'harmonic_count': 1,
                        'guitar_string': closest_note.get('guitar_string')
                    })
        
        # Remove duplicate notes (keep strongest)
        unique_notes = {}
        for note in detected_notes:
            note_name = note['note']
            if note_name not in unique_notes or note['strength'] > unique_notes[note_name]['strength']:
                unique_notes[note_name] = note
        
        return list(unique_notes.values())
    
    def find_closest_note(self, target_frequency):
        """Find the closest musical note to a frequency with guitar string info"""
        closest_match = None
        smallest_difference = float('inf')
        
        for note_name, octave_frequencies in self.note_frequencies.items():
            for octave_index, note_freq in enumerate(octave_frequencies):
                difference = abs(target_frequency - note_freq)
                
                if difference < smallest_difference:
                    smallest_difference = difference
                    
                    # Calculate cents (musical pitch difference measure)
                    if target_frequency > 0 and note_freq > 0:
                        cents_off = 1200 * math.log2(target_frequency / note_freq)
                    else:
                        cents_off = 0
                    
                    # Identify which guitar string could produce this frequency
                    string_info = self.identify_guitar_string(target_frequency)
                    
                    closest_match = {
                        'note': note_name,
                        'octave': octave_index + 2,
                        'cents_off': cents_off,
                        'frequency_difference': difference,
                        'guitar_string': string_info
                    }
        
        return closest_match
    
    def identify_guitar_string(self, target_frequency):
        """Identify which guitar string could produce this frequency"""
        if target_frequency < 80 or target_frequency > 1200:
            return None
        
        # Find closest string
        closest_string = None
        min_diff = float('inf')
        
        for string, string_freq in self.guitar_strings.items():
            diff = abs(target_frequency - string_freq)
            if diff < min_diff:
                min_diff = diff
                closest_string = string
        
        # Only return if within reasonable range (50 Hz)
        if min_diff < 50:
            return {
                'string': closest_string,
                'expected_freq': self.guitar_strings[closest_string],
                'difference': min_diff
            }
        
        return None
    
    def analyze_chord_from_notes(self, detected_notes):
        """Determine chord type from detected notes"""
        if len(detected_notes) < 2:
            return {'root': None, 'quality': None, 'confidence': 0}
        
        note_names = [note['note'] for note in detected_notes]
        unique_notes = list(set(note_names))
        
        best_match = {'root': None, 'quality': None, 'confidence': 0}
        
        # Try each note as potential root
        for potential_root in unique_notes:
            for chord_quality, intervals in self.chord_patterns.items():
                expected_notes = self.get_chord_notes(potential_root, intervals)
                confidence = self.calculate_chord_confidence(unique_notes, expected_notes)
                
                if confidence > best_match['confidence']:
                    best_match = {
                        'root': potential_root,
                        'quality': chord_quality,
                        'confidence': confidence,
                        'expected_notes': expected_notes
                    }
        
        return best_match
    
    def get_chord_notes(self, root_note, intervals):
        """Calculate notes in a chord from root and intervals"""
        try:
            root_index = self.chromatic_scale.index(root_note)
        except ValueError:
            return []
        
        chord_notes = []
        for interval in intervals:
            note_index = (root_index + interval) % 12
            chord_notes.append(self.chromatic_scale[note_index])
        
        return chord_notes
    
    def calculate_chord_confidence(self, detected_notes, expected_notes):
        """Calculate how well detected notes match expected chord"""
        if not expected_notes or not detected_notes:
            return 0
        
        matches = len(set(detected_notes) & set(expected_notes))
        expected_count = len(expected_notes)
        detected_count = len(detected_notes)
        
        # Base confidence from matches
        match_ratio = matches / expected_count
        
        # Penalty for extra notes (reduces confidence)
        if detected_count > expected_count:
            extra_notes_penalty = (detected_count - expected_count) * 0.1
            match_ratio -= extra_notes_penalty
        
        # Bonus for perfect matches
        if matches == expected_count and detected_count == expected_count:
            match_ratio = 1.0
        
        return max(0, min(1, match_ratio))
    
    def empty_chord_result(self):
        """Return empty chord result"""
        return {
            'root': None,
            'quality': None,
            'notes': [],
            'note_details': [],
            'confidence': 0,
            'timestamp': time.time(),
            'valid': False
        }
