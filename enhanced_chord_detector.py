#!/usr/bin/env python3
"""
Enhanced Chord Detection System

Builds upon the enhanced guitar note detector to provide accurate
chord recognition using advanced harmonic analysis and chord theory.

This system:
1. Uses the enhanced note detector for accurate individual note detection
2. Implements advanced chord analysis algorithms
3. Provides real-time chord recognition with confidence scoring
4. Supports extended chord types and voicings
5. Offers tuning feedback for each note in the chord
"""

import numpy as np
import math
import time
from typing import Dict, List, Optional, Tuple
from enhanced_guitar_detector import EnhancedGuitarDetector
import warnings
warnings.filterwarnings('ignore')

class EnhancedChordDetector:
    """
    Enhanced chord detector using advanced harmonic analysis
    and the enhanced guitar note detector.
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Initialize the enhanced guitar detector
        self.note_detector = EnhancedGuitarDetector(sample_rate)
        
        # Extended chord patterns with intervals
        self.chord_patterns = {
            # Basic triads
            'major': {'intervals': [0, 4, 7], 'symbols': ['', 'maj', 'M']},
            'minor': {'intervals': [0, 3, 7], 'symbols': ['m', 'min', '-']},
            'diminished': {'intervals': [0, 3, 6], 'symbols': ['dim', '°']},
            'augmented': {'intervals': [0, 4, 8], 'symbols': ['aug', '+', '+5']},
            
            # Suspended chords
            'sus2': {'intervals': [0, 2, 7], 'symbols': ['sus2', '2']},
            'sus4': {'intervals': [0, 5, 7], 'symbols': ['sus4', 'sus', '4']},
            
            # Seventh chords
            'major7': {'intervals': [0, 4, 7, 11], 'symbols': ['maj7', 'M7', 'Δ7']},
            'minor7': {'intervals': [0, 3, 7, 10], 'symbols': ['m7', 'min7', '-7']},
            'dominant7': {'intervals': [0, 4, 7, 10], 'symbols': ['7', 'dom7']},
            'diminished7': {'intervals': [0, 3, 6, 9], 'symbols': ['dim7', '°7']},
            'half_diminished7': {'intervals': [0, 3, 6, 10], 'symbols': ['m7b5', 'ø7', 'half-dim7']},
            'minor_major7': {'intervals': [0, 3, 7, 11], 'symbols': ['mMaj7', 'mM7']},
            
            # Extended chords
            'major9': {'intervals': [0, 4, 7, 11, 14], 'symbols': ['maj9', 'M9', 'Δ9']},
            'minor9': {'intervals': [0, 3, 7, 10, 14], 'symbols': ['m9', 'min9']},
            'dominant9': {'intervals': [0, 4, 7, 10, 14], 'symbols': ['9', 'dom9']},
            'major11': {'intervals': [0, 4, 7, 11, 14, 17], 'symbols': ['maj11', 'M11', 'Δ11']},
            'minor11': {'intervals': [0, 3, 7, 10, 14, 17], 'symbols': ['m11', 'min11']},
            
            # Power chords
            'power': {'intervals': [0, 7], 'symbols': ['5', 'power']},
            'power_octave': {'intervals': [0, 7, 12], 'symbols': ['5oct', 'power_oct']},
            
            # Add chords
            'add2': {'intervals': [0, 4, 7, 14], 'symbols': ['add2', 'add9']},
            'add4': {'intervals': [0, 4, 7, 17], 'symbols': ['add4', 'add11']},
            'add6': {'intervals': [0, 4, 7, 21], 'symbols': ['add6', 'add13']},
            
            # Altered chords
            'major7#5': {'intervals': [0, 4, 8, 11], 'symbols': ['maj7#5', 'M7#5', 'Δ7#5']},
            'major7b5': {'intervals': [0, 4, 6, 11], 'symbols': ['maj7b5', 'M7b5', 'Δ7b5']},
            'dominant7#5': {'intervals': [0, 4, 8, 10], 'symbols': ['7#5', 'dom7#5']},
            'dominant7b5': {'intervals': [0, 4, 6, 10], 'symbols': ['7b5', 'dom7b5']},
            'dominant7#9': {'intervals': [0, 4, 7, 10, 15], 'symbols': ['7#9', 'dom7#9']},
            'dominant7b9': {'intervals': [0, 4, 7, 10, 13], 'symbols': ['7b9', 'dom7b9']},
        }
        
        # Chromatic scale for interval calculations
        self.chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Chord voicing patterns (common guitar fingerings)
        self.voicing_patterns = {
            'open': 'Open position chords',
            'barre': 'Barre chord shapes',
            'power': 'Power chord shapes',
            'jazz': 'Jazz voicings',
            'drop2': 'Drop 2 voicings',
            'drop3': 'Drop 3 voicings'
        }
        
        print(f"🎸 Enhanced Chord Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎵 Supported chord types: {len(self.chord_patterns)}")
        print(f"🔧 Using enhanced note detection")
    
    def detect_chord_from_audio(self, audio_data: np.ndarray) -> Dict:
        """
        Detect chord from audio data using enhanced note detection
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dictionary with chord information
        """
        try:
            # Check audio level
            audio_level = np.max(np.abs(audio_data))
            if audio_level < 0.005:
                return self._empty_chord_result()
            
            # Detect individual notes
            detected_notes = self._detect_multiple_notes(audio_data)
            
            if len(detected_notes) < 2:
                return self._empty_chord_result()
            
            # Analyze chord structure
            chord_analysis = self._analyze_chord_structure(detected_notes)
            
            # Calculate overall confidence
            confidence = self._calculate_chord_confidence(detected_notes, chord_analysis)
            
            # Determine chord voicing
            voicing = self._determine_chord_voicing(detected_notes)
            
            return {
                'root': chord_analysis['root'],
                'quality': chord_analysis['quality'],
                'symbol': chord_analysis['symbol'],
                'notes': chord_analysis['notes'],
                'note_details': detected_notes,
                'intervals': chord_analysis['intervals'],
                'confidence': confidence,
                'voicing': voicing,
                'tuning_status': self._get_overall_tuning_status(detected_notes),
                'valid': confidence > 0.4,
                'timestamp': time.time(),
                'detection_method': 'enhanced_harmonic_analysis'
            }
            
        except Exception as e:
            print(f"❌ Chord detection error: {e}")
            return self._empty_chord_result()
    
    def _detect_multiple_notes(self, audio_data: np.ndarray) -> List[Dict]:
        """Detect multiple notes from audio using sliding windows"""
        detected_notes = []
        
        # Use different window positions to catch different notes
        window_positions = [0, len(audio_data)//4, len(audio_data)//2, 3*len(audio_data)//4]
        
        for pos in window_positions:
            # Extract window of audio
            window_start = max(0, pos - self.note_detector.window_size//2)
            window_end = min(len(audio_data), window_start + self.note_detector.window_size)
            
            if window_end - window_start < self.note_detector.window_size//2:
                continue
            
            window_audio = audio_data[window_start:window_end]
            
            # Detect note in this window
            note_result = self.note_detector.detect_note_from_audio(window_audio)
            
            if (note_result and note_result['note'] != 'Unknown' and 
                note_result['confidence'] > 0.3):
                
                # Check if we already have this note
                note_exists = False
                for existing_note in detected_notes:
                    if (existing_note['note'] == note_result['note'] and 
                        existing_note['octave'] == note_result['octave']):
                        # Keep the stronger detection
                        if note_result['confidence'] > existing_note['confidence']:
                            existing_note.update(note_result)
                        note_exists = True
                        break
                
                if not note_exists:
                    detected_notes.append(note_result)
        
        # Sort notes by frequency (lowest first)
        detected_notes.sort(key=lambda x: x['frequency'])
        
        return detected_notes
    
    def _analyze_chord_structure(self, detected_notes: List[Dict]) -> Dict:
        """Analyze detected notes to determine chord structure"""
        if not detected_notes:
            return {'root': 'Unknown', 'quality': 'unknown', 'notes': [], 'symbol': 'N'}
        
        # Get note names and frequencies
        note_names = [note['note'] for note in detected_notes]
        note_frequencies = [note['frequency'] for note in detected_notes]
        
        # Find potential roots (try each note as root)
        best_chord = {'root': 'Unknown', 'quality': 'unknown', 'notes': [], 'symbol': 'N', 'score': 0}
        
        for i, potential_root in enumerate(detected_notes):
            root_note = potential_root['note']
            root_freq = potential_root['frequency']
            
            # Calculate intervals from this root
            intervals = []
            for j, note in enumerate(detected_notes):
                if i != j:
                    # Calculate semitones from root
                    semitones = 12 * math.log2(note['frequency'] / root_freq)
                    intervals.append(round(semitones))
            
            # Sort intervals for comparison
            intervals.sort()
            
            # Check against chord patterns
            for quality, pattern_info in self.chord_patterns.items():
                expected_intervals = pattern_info['intervals'][1:]  # Skip root (0)
                
                # Check if intervals match (with tolerance)
                if self._intervals_match(intervals, expected_intervals):
                    # Calculate score based on how well it matches
                    score = self._calculate_interval_match_score(intervals, expected_intervals)
                    
                    if score > best_chord['score']:
                        # Generate chord symbol
                        symbol = self._generate_chord_symbol(root_note, quality)
                        
                        best_chord = {
                            'root': root_note,
                            'quality': quality,
                            'notes': note_names,
                            'symbol': symbol,
                            'intervals': intervals,
                            'score': score
                        }
        
        return best_chord
    
    def _intervals_match(self, detected_intervals: List[int], expected_intervals: List[int]) -> bool:
        """Check if detected intervals match expected intervals with tolerance"""
        if len(detected_intervals) != len(expected_intervals):
            return False
        
        # Sort both lists for comparison
        detected_sorted = sorted(detected_intervals)
        expected_sorted = sorted(expected_intervals)
        
        # Check if intervals are close (within 1 semitone tolerance)
        for detected, expected in zip(detected_sorted, expected_sorted):
            if abs(detected - expected) > 1:
                return False
        
        return True
    
    def _calculate_interval_match_score(self, detected_intervals: List[int], expected_intervals: List[int]) -> float:
        """Calculate how well detected intervals match expected intervals"""
        if len(detected_intervals) != len(expected_intervals):
            return 0.0
        
        # Sort both lists
        detected_sorted = sorted(detected_intervals)
        expected_sorted = sorted(expected_intervals)
        
        # Calculate average difference
        total_diff = 0
        for detected, expected in zip(detected_sorted, expected_sorted):
            total_diff += abs(detected - expected)
        
        avg_diff = total_diff / len(detected_intervals)
        
        # Convert to score (0 = perfect match, 1 = poor match)
        score = max(0, 1 - avg_diff / 2)
        
        return score
    
    def _generate_chord_symbol(self, root: str, quality: str) -> str:
        """Generate chord symbol from root and quality"""
        if quality == 'unknown':
            return root
        
        pattern_info = self.chord_patterns.get(quality, {})
        symbols = pattern_info.get('symbols', [quality])
        
        # Use the first symbol (most common)
        return f"{root}{symbols[0]}"
    
    def _calculate_chord_confidence(self, detected_notes: List[Dict], chord_analysis: Dict) -> float:
        """Calculate overall chord confidence"""
        if not detected_notes or chord_analysis['root'] == 'Unknown':
            return 0.0
        
        # Base confidence from chord analysis score
        chord_score = chord_analysis.get('score', 0)
        
        # Note detection confidence
        note_confidence = np.mean([note['confidence'] for note in detected_notes])
        
        # Tuning accuracy (lower cents = higher confidence)
        tuning_penalty = 0
        for note in detected_notes:
            cents_off = abs(note['cents_off'])
            if cents_off > 50:
                tuning_penalty += (cents_off - 50) / 100
        
        tuning_confidence = max(0, 1 - tuning_penalty)
        
        # Note count bonus (more notes = higher confidence, up to a point)
        note_count_bonus = min(len(detected_notes) / 6.0, 1.0)
        
        # Combine factors
        final_confidence = (
            chord_score * 0.4 +
            note_confidence * 0.3 +
            tuning_confidence * 0.2 +
            note_count_bonus * 0.1
        )
        
        return min(final_confidence, 1.0)
    
    def _determine_chord_voicing(self, detected_notes: List[Dict]) -> str:
        """Determine the type of chord voicing based on note distribution"""
        if len(detected_notes) < 2:
            return 'unknown'
        
        # Check for power chord (root + fifth)
        if len(detected_notes) == 2:
            root_freq = detected_notes[0]['frequency']
            second_freq = detected_notes[1]['frequency']
            ratio = second_freq / root_freq
            
            if abs(ratio - 1.5) < 0.1:  # Perfect fifth ratio
                return 'power'
        
        # Check for open position (contains open strings)
        open_strings = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
        has_open_strings = any(
            abs(note['frequency'] - self.note_detector.guitar_strings.get(f"{note['note']}{note['octave']}", 0)) < 5
            for note in detected_notes
        )
        
        if has_open_strings:
            return 'open'
        
        # Check for barre chord (notes spread across multiple octaves)
        frequencies = [note['frequency'] for note in detected_notes]
        freq_range = max(frequencies) - min(frequencies)
        
        if freq_range > 400:  # Wide frequency range
            return 'barre'
        
        # Default to standard voicing
        return 'standard'
    
    def _get_overall_tuning_status(self, detected_notes: List[Dict]) -> Dict:
        """Get overall tuning status for the chord"""
        if not detected_notes:
            return {'status': 'unknown', 'average_cents_off': 0, 'worst_note': None}
        
        # Calculate average cents off
        cents_offs = [abs(note['cents_off']) for note in detected_notes]
        avg_cents_off = np.mean(cents_offs)
        
        # Find worst tuned note
        worst_note = max(detected_notes, key=lambda x: abs(x['cents_off']))
        
        # Determine overall status
        if avg_cents_off < 15:
            status = 'excellent'
        elif avg_cents_off < 30:
            status = 'good'
        elif avg_cents_off < 50:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'average_cents_off': avg_cents_off,
            'worst_note': worst_note['note'],
            'worst_cents_off': worst_note['cents_off']
        }
    
    def get_chord_suggestions(self, detected_notes: List[Dict]) -> List[Dict]:
        """Get alternative chord interpretations"""
        if not detected_notes:
            return []
        
        suggestions = []
        
        # Try different note combinations
        for i in range(len(detected_notes)):
            # Remove one note and analyze
            remaining_notes = detected_notes[:i] + detected_notes[i+1:]
            if len(remaining_notes) >= 2:
                analysis = self._analyze_chord_structure(remaining_notes)
                if analysis['root'] != 'Unknown':
                    suggestions.append({
                        'notes': [note['note'] for note in remaining_notes],
                        'chord': analysis,
                        'removed_note': detected_notes[i]['note']
                    })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['chord'].get('score', 0), reverse=True)
        
        return suggestions[:3]  # Top 3 suggestions
    
    def _empty_chord_result(self) -> Dict:
        """Return empty chord result"""
        return {
            'root': 'Unknown',
            'quality': 'unknown',
            'symbol': 'N',
            'notes': [],
            'note_details': [],
            'intervals': [],
            'confidence': 0.0,
            'voicing': 'unknown',
            'tuning_status': {'status': 'unknown', 'average_cents_off': 0, 'worst_note': None},
            'valid': False,
            'timestamp': 0,
            'detection_method': 'none'
        }
    
    def test_chord_detection(self, duration: float = 5.0) -> None:
        """Test the chord detection with live audio"""
        try:
            import sounddevice as sd
            
            print(f"🎤 Testing enhanced chord detection for {duration} seconds...")
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
                print(f"\n🎯 Chord detected: {chord_result['symbol']}")
                print(f"   Root: {chord_result['root']}")
                print(f"   Quality: {chord_result['quality']}")
                print(f"   Notes: {chord_result['notes']}")
                print(f"   Voicing: {chord_result['voicing']}")
                print(f"   Confidence: {chord_result['confidence']:.2f}")
                
                # Show tuning status
                tuning = chord_result['tuning_status']
                print(f"   Tuning: {tuning['status']} (avg: {tuning['average_cents_off']:.1f} cents)")
                
                # Show note details
                print(f"\n📝 Note details:")
                for note in chord_result['note_details']:
                    tuning_feedback = self.note_detector.get_tuning_feedback(note['cents_off'])
                    print(f"   {note['note']}{note['octave']}: {note['frequency']:.1f} Hz, {tuning_feedback}")
                
                # Show suggestions
                suggestions = self.get_chord_suggestions(chord_result['note_details'])
                if suggestions:
                    print(f"\n💡 Alternative interpretations:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion['chord']['symbol']} (without {suggestion['removed_note']})")
            else:
                print("\n❌ No chord detected")
                
        except ImportError:
            print("❌ sounddevice not available for testing")
        except Exception as e:
            print(f"❌ Test error: {e}")


def main():
    """Test the enhanced chord detector"""
    detector = EnhancedChordDetector()
    print("🎸 Enhanced Chord Detector ready!")
    print("💡 Built on piano key frequency principles")
    print("💡 Advanced harmonic analysis for accurate chord recognition")
    print("💡 Real-time tuning feedback and chord suggestions")

if __name__ == "__main__":
    main()
