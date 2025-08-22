#!/usr/bin/env python3
"""
Polyphonic Chord Detector for Guitar
Uses advanced algorithms specifically designed for polyphonic music detection
"""

import numpy as np
import librosa
import librosa.display
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PolyphonicChordDetector:
    """Advanced polyphonic chord detector optimized for guitar"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Guitar string frequencies (open strings)
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        # Chromatic scale for note identification
        self.chromatic_scale = {
            'C': [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.01],
            'C#': [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            'D': [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32, 4698.64],
            'D#': [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            'E': [20.60, 41.20, 82.41, 164.81, 329.63, 659.25, 1318.51, 2637.02, 5274.04],
            'F': [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83, 5587.65],
            'F#': [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            'G': [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96, 6271.93],
            'G#': [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            'A': [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00, 7040.00],
            'A#': [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            'B': [30.87, 61.74, 123.47, 246.94, 493.88, 987.77, 1975.53, 3951.07, 7902.13]
        }
        
        print(f"🎸 Polyphonic Chord Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎯 Optimized for guitar polyphonic detection")
    
    def detect_chord_polyphonic(self, audio_data: np.ndarray) -> Dict:
        """
        Detect chord using advanced polyphonic analysis
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dictionary with chord information
        """
        try:
            # Method 1: Constant-Q Transform (better for polyphonic)
            CQT = librosa.cqt(
                y=audio_data, 
                sr=self.sample_rate,
                hop_length=512,
                n_bins=84,  # 7 octaves
                bins_per_octave=12  # 12 semitones per octave
            )
            
            # Convert to magnitude spectrum
            CQT_mag = np.abs(CQT)
            
            # Method 2: Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Analyze harmonic component for polyphonic detection
            harmonic_CQT = librosa.cqt(
                y=harmonic,
                sr=self.sample_rate,
                hop_length=512,
                n_bins=84,
                bins_per_octave=12
            )
            harmonic_mag = np.abs(harmonic_CQT)
            
            # Combine both analyses
            combined_mag = (CQT_mag + harmonic_mag) / 2
            
            # Find peaks in the combined spectrum
            detected_notes = self._extract_polyphonic_notes(combined_mag)
            
            # Analyze chord structure
            chord_info = self._analyze_chord_structure(detected_notes)
            
            return chord_info
            
        except Exception as e:
            print(f"❌ Polyphonic detection error: {e}")
            return self._fallback_detection(audio_data)
    
    def _extract_polyphonic_notes(self, magnitude_spectrum: np.ndarray) -> List[Dict]:
        """Extract multiple notes from polyphonic spectrum"""
        detected_notes = []
        
        # Find peaks across all time frames
        for frame in range(magnitude_spectrum.shape[1]):
            frame_magnitudes = magnitude_spectrum[:, frame]
            
            # Find peaks in this frame
            peaks = librosa.util.peak_pick(
                frame_magnitudes,
                pre_max=3, post_max=3,
                pre_avg=3, post_avg=3,
                delta=0.1, wait=10
            )
            
            for peak_idx in peaks:
                # Convert bin index to frequency
                freq = librosa.cqt_frequencies(
                    n_bins=84, 
                    fmin=librosa.note_to_hz('C1'),  # Start from C1
                    bins_per_octave=12
                )[peak_idx]
                
                magnitude = frame_magnitudes[peak_idx]
                
                if freq > 80 and freq < 1200:  # Guitar range
                    note_info = self._frequency_to_note_enhanced(freq)
                    if note_info:
                        note_info['magnitude'] = magnitude
                        note_info['time_frame'] = frame
                        detected_notes.append(note_info)
        
        # Remove duplicates and sort by magnitude
        unique_notes = self._deduplicate_notes_enhanced(detected_notes)
        
        return sorted(unique_notes, key=lambda x: x['magnitude'], reverse=True)[:6]
    
    def _frequency_to_note_enhanced(self, frequency: float) -> Optional[Dict]:
        """Enhanced frequency to note conversion with better accuracy"""
        if frequency <= 0:
            return None
        
        # Find the closest note in the chromatic scale
        best_note = None
        best_octave = None
        min_cents_off = float('inf')
        
        for note_name, octaves in self.chromatic_scale.items():
            for octave, note_freq in enumerate(octaves):
                if note_freq > 0:
                    # Calculate cents difference
                    cents_off = 1200 * np.log2(frequency / note_freq)
                    
                    if abs(cents_off) < abs(min_cents_off):
                        min_cents_off = cents_off
                        best_note = note_name
                        best_octave = octave
        
        if best_note is None:
            return None
        
        # Determine if this could be a guitar string
        guitar_string = self._identify_guitar_string(frequency)
        
        # Calculate tuning status with more lenient thresholds
        if abs(min_cents_off) < 15:  # More lenient for polyphonic
            tuning_status = "in_tune"
        elif abs(min_cents_off) < 35:  # More lenient
            tuning_status = "slightly_off"
        else:
            tuning_status = "out_of_tune"
        
        return {
            'frequency': frequency,
            'note': best_note,
            'octave': best_octave,
            'cents_off': min_cents_off,
            'tuning_status': tuning_status,
            'guitar_string': guitar_string,
            'detection_method': 'polyphonic_cqt'
        }
    
    def _identify_guitar_string(self, frequency: float) -> Optional[Dict]:
        """Identify which guitar string could produce this frequency"""
        for string_name, string_freq in self.guitar_strings.items():
            # More lenient matching for polyphonic detection
            cents_diff = 1200 * np.log2(frequency / string_freq)
            if abs(cents_diff) < 75:  # More lenient (75 cents)
                return {
                    'string': string_name,
                    'expected_freq': string_freq,
                    'difference': frequency - string_freq,
                    'cents_off': cents_diff
                }
        return None
    
    def _deduplicate_notes_enhanced(self, notes: List[Dict]) -> List[Dict]:
        """Enhanced deduplication for polyphonic detection"""
        if not notes:
            return []
        
        # Sort by frequency
        sorted_notes = sorted(notes, key=lambda x: x['frequency'])
        
        # Group similar frequencies (more lenient for polyphonic)
        grouped_notes = []
        current_group = [sorted_notes[0]]
        
        for note in sorted_notes[1:]:
            # More lenient grouping for polyphonic (25 cents)
            cents_diff = 1200 * np.log2(note['frequency'] / current_group[0]['frequency'])
            
            if cents_diff < 25:  # More lenient grouping
                current_group.append(note)
            else:
                # Save the strongest note from the current group
                best_note = max(current_group, key=lambda x: x['magnitude'])
                grouped_notes.append(best_note)
                current_group = [note]
        
        # Don't forget the last group
        if current_group:
            best_note = max(current_group, key=lambda x: x['magnitude'])
            grouped_notes.append(best_note)
        
        return grouped_notes
    
    def _analyze_chord_structure(self, detected_notes: List[Dict]) -> Dict:
        """Analyze the structure of detected notes to determine chord"""
        if not detected_notes:
            return self._empty_chord_result()
        
        # Sort by frequency (lowest = root)
        sorted_notes = sorted(detected_notes, key=lambda x: x['frequency'])
        
        # Get the root note (lowest frequency)
        root_note = sorted_notes[0]
        
        # Extract note names
        note_names = [note['note'] for note in sorted_notes]
        
        # Basic chord quality detection
        chord_quality = self._determine_chord_quality(note_names)
        
        # Calculate confidence based on note clarity
        confidence = self._calculate_chord_confidence(detected_notes)
        
        return {
            'root': root_note['note'],
            'quality': chord_quality,
            'notes': note_names,
            'note_details': detected_notes,
            'confidence': confidence,
            'valid': True,
            'timestamp': time.time()
        }
    
    def _determine_chord_quality(self, note_names: List[str]) -> str:
        """Determine basic chord quality from note names"""
        if len(note_names) < 3:
            return 'power'
        
        # Simple interval analysis
        root = note_names[0]
        
        # Check for major third (4 semitones up)
        major_third = self._get_note_at_interval(root, 4)
        minor_third = self._get_note_at_interval(root, 3)
        
        # Check for perfect fifth (7 semitones up)
        perfect_fifth = self._get_note_at_interval(root, 7)
        
        if major_third in note_names and perfect_fifth in note_names:
            return 'major'
        elif minor_third in note_names and perfect_fifth in note_names:
            return 'minor'
        elif perfect_fifth in note_names:
            return 'power'
        else:
            return 'unknown'
    
    def _get_note_at_interval(self, root: str, semitones: int) -> str:
        """Get note at specified interval from root"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_idx = notes.index(root)
        target_idx = (root_idx + semitones) % 12
        return notes[target_idx]
    
    def _calculate_chord_confidence(self, detected_notes: List[Dict]) -> float:
        """Calculate confidence based on note clarity and tuning"""
        if not detected_notes:
            return 0.0
        
        # Base confidence from number of notes
        base_confidence = min(len(detected_notes) / 4.0, 1.0)
        
        # Adjust based on tuning accuracy
        tuning_penalty = 0.0
        for note in detected_notes:
            cents_off = abs(note.get('cents_off', 0))
            if cents_off > 50:
                tuning_penalty += 0.1
            elif cents_off > 25:
                tuning_penalty += 0.05
        
        final_confidence = max(base_confidence - tuning_penalty, 0.1)
        return min(final_confidence, 1.0)
    
    def _fallback_detection(self, audio_data: np.ndarray) -> Dict:
        """Fallback to simpler detection if polyphonic fails"""
        return {
            'root': 'Unknown',
            'quality': 'unknown',
            'notes': [],
            'note_details': [],
            'confidence': 0.0,
            'valid': False,
            'timestamp': time.time()
        }
    
    def _empty_chord_result(self) -> Dict:
        """Return empty chord result"""
        return {
            'root': 'Unknown',
            'quality': 'unknown',
            'notes': [],
            'note_details': [],
            'confidence': 0.0,
            'valid': False,
            'timestamp': time.time()
        }

def main():
    """Test the polyphonic chord detector"""
    detector = PolyphonicChordDetector()
    print("🎸 Polyphonic Chord Detector ready!")
    print("💡 This detector is specifically designed for polyphonic guitar chords")

if __name__ == "__main__":
    main()
