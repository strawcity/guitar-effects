#!/usr/bin/env python3
"""
Professional Guitar Note Detector using librosa
Provides accurate note detection specifically optimized for guitar frequencies
"""

import numpy as np
import librosa
import librosa.display
from typing import Dict, List, Tuple, Optional

class ProfessionalGuitarDetector:
    """Professional-grade guitar note detector using librosa"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Standard guitar string frequencies (open strings)
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        # Chromatic scale frequencies (C0 to B8)
        # These are the mathematically correct frequencies
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
        
        # Guitar-specific frequency range
        self.guitar_range = (80, 1200)  # Hz
        
        print(f"🎸 Professional Guitar Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎯 Guitar range: {self.guitar_range[0]}-{self.guitar_range[1]} Hz")
    
    def detect_notes(self, audio_data: np.ndarray) -> List[Dict]:
        """
        Detect multiple notes in guitar audio using professional algorithms
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            List of detected notes with frequency, note name, and confidence
        """
        try:
            # Method 1: librosa's pitch detection (most accurate)
            pitches, magnitudes = librosa.piptrack(
                y=audio_data, 
                sr=self.sample_rate,
                fmin=librosa.note_to_hz('E2'),  # 82.41 Hz (lowest guitar string)
                fmax=librosa.note_to_hz('E6'),  # 1318.51 Hz (highest practical guitar note)
                threshold=0.1
            )
            
            # Extract the most prominent pitches
            detected_notes = []
            
            # Find peaks in the pitch track
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                if magnitudes[index, t] > 0.1:  # Threshold for significance
                    freq = pitches[index, t]
                    if freq > 0:  # Valid frequency
                        note_info = self._frequency_to_note(freq)
                        if note_info:
                            note_info['magnitude'] = magnitudes[index, t]
                            note_info['time_frame'] = t
                            detected_notes.append(note_info)
            
            # Method 2: Harmonic analysis for guitar-specific detection
            harmonic_notes = self._harmonic_analysis(audio_data)
            detected_notes.extend(harmonic_notes)
            
            # Remove duplicates and sort by magnitude
            unique_notes = self._deduplicate_notes(detected_notes)
            
            # Return top notes (limit to 6 for chord detection)
            return sorted(unique_notes, key=lambda x: x['magnitude'], reverse=True)[:6]
            
        except Exception as e:
            print(f"❌ Note detection error: {e}")
            return []
    
    def _harmonic_analysis(self, audio_data: np.ndarray) -> List[Dict]:
        """Perform harmonic analysis specifically for guitar frequencies"""
        try:
            # Use librosa's harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Analyze harmonic component (more useful for note detection)
            pitches, magnitudes = librosa.piptrack(
                y=harmonic,
                sr=self.sample_rate,
                fmin=80,  # Guitar low E
                fmax=1200,  # Guitar high range
                threshold=0.05
            )
            
            harmonic_notes = []
            
            # Look for fundamental frequencies and harmonics
            for t in range(pitches.shape[1]):
                # Find the strongest frequency in this time frame
                frame_pitches = pitches[:, t]
                frame_magnitudes = magnitudes[:, t]
                
                # Find peaks in this frame
                peaks = librosa.util.peak_pick(
                    frame_magnitudes,
                    pre_max=3, post_max=3,
                    pre_avg=3, post_avg=3,
                    delta=0.1, wait=10
                )
                
                for peak_idx in peaks:
                    freq = frame_pitches[peak_idx]
                    mag = frame_magnitudes[peak_idx]
                    
                    if freq > 0 and mag > 0.05:
                        note_info = self._frequency_to_note(freq)
                        if note_info:
                            note_info['magnitude'] = mag
                            note_info['time_frame'] = t
                            note_info['detection_method'] = 'harmonic'
                            harmonic_notes.append(note_info)
            
            return harmonic_notes
            
        except Exception as e:
            print(f"❌ Harmonic analysis error: {e}")
            return []
    
    def _frequency_to_note(self, frequency: float) -> Optional[Dict]:
        """
        Convert frequency to note name with octave and cents accuracy
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Dictionary with note information
        """
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
        
        # Calculate tuning status
        if abs(min_cents_off) < 10:
            tuning_status = "in_tune"
        elif abs(min_cents_off) < 25:
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
            'detection_method': 'pitch_track'
        }
    
    def _identify_guitar_string(self, frequency: float) -> Optional[Dict]:
        """Identify which guitar string could produce this frequency"""
        for string_name, string_freq in self.guitar_strings.items():
            # Check if frequency is close to this string (within 50 cents)
            cents_diff = 1200 * np.log2(frequency / string_freq)
            if abs(cents_diff) < 50:
                return {
                    'string': string_name,
                    'expected_freq': string_freq,
                    'difference': frequency - string_freq,
                    'cents_off': cents_diff
                }
        return None
    
    def _deduplicate_notes(self, notes: List[Dict]) -> List[Dict]:
        """Remove duplicate notes and merge similar frequencies"""
        if not notes:
            return []
        
        # Sort by frequency
        sorted_notes = sorted(notes, key=lambda x: x['frequency'])
        
        # Group similar frequencies (within 10 cents)
        grouped_notes = []
        current_group = [sorted_notes[0]]
        
        for note in sorted_notes[1:]:
            # Check if this note is close to the current group
            freq_diff = abs(note['frequency'] - current_group[0]['frequency'])
            cents_diff = 1200 * np.log2(note['frequency'] / current_group[0]['frequency'])
            
            if cents_diff < 10:  # Within 10 cents
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
    
    def test_detection(self, duration: float = 3.0) -> None:
        """Test the note detection with live audio"""
        import sounddevice as sd
        
        print(f"🎤 Testing note detection for {duration} seconds...")
        print("🎸 Play a chord on your guitar!")
        
        # Record audio
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        
        sd.wait()
        
        # Detect notes
        detected_notes = self.detect_notes(audio_data.flatten())
        
        print(f"\n🎯 Detected {len(detected_notes)} notes:")
        for i, note in enumerate(detected_notes):
            print(f"  {i+1}. {note['note']}{note['octave']}: {note['frequency']:.2f} Hz")
            print(f"     Cents off: {note['cents_off']:+.1f} ({note['tuning_status']})")
            if note['guitar_string']:
                string_info = note['guitar_string']
                print(f"     Guitar string: {string_info['string']} (expected: {string_info['expected_freq']:.2f} Hz)")
            print(f"     Magnitude: {note['magnitude']:.3f}")
            print()

def main():
    """Test the professional guitar detector"""
    detector = ProfessionalGuitarDetector()
    detector.test_detection()

if __name__ == "__main__":
    main()
