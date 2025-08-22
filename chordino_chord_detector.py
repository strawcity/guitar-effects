#!/usr/bin/env python3
"""
Chordino-based Chord Detector using chord-extractor package
Professional-grade chord detection using the Chordino algorithm
"""

import numpy as np
import sounddevice as sd
import tempfile
import os
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from chord_extractor.extractors import Chordino
    from chord_extractor import ChordChange
    CHORD_EXTRACTOR_AVAILABLE = True
except ImportError:
    CHORD_EXTRACTOR_AVAILABLE = False
    print("⚠️  chord-extractor not available. Install with: pip install chord-extractor")

class ChordinoChordDetector:
    """Professional chord detector using Chordino algorithm"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        if not CHORD_EXTRACTOR_AVAILABLE:
            print("❌ chord-extractor package not available")
            return
        
        # Initialize Chordino with optimized parameters for guitar
        self.chordino = Chordino(
            roll_on=1,           # Minimum duration for chord detection
            roll_off=0.1,        # Minimum gap between chords
            min_chord_length=0.1, # Minimum chord duration
            chord_change_threshold=0.1  # Sensitivity to chord changes
        )
        
        # Guitar string frequencies for reference
        self.guitar_strings = {
            'E2': 82.41,   # 6th string (thickest)
            'A2': 110.00,  # 5th string
            'D3': 146.83,  # 4th string
            'G3': 196.00,  # 3rd string
            'B3': 246.94,  # 2nd string
            'E4': 329.63   # 1st string (thinnest)
        }
        
        print(f"🎸 Chordino Chord Detector initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🎯 Using professional Chordino algorithm")
        print(f"⚙️  Parameters: roll_on={self.chordino.roll_on}s, min_length={self.chordino.min_chord_length}s")
    
    def detect_chord_from_audio(self, audio_data: np.ndarray) -> Dict:
        """
        Detect chord from audio data using Chordino
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dictionary with chord information
        """
        if not CHORD_EXTRACTOR_AVAILABLE:
            return self._empty_chord_result()
        
        try:
            # Check audio level before processing
            audio_level = np.max(np.abs(audio_data))
            if audio_level < 0.005:  # Too weak for meaningful detection
                return self._empty_chord_result()
            
            # Save audio to temporary WAV file (Chordino requires file input)
            temp_file = self._save_audio_to_temp(audio_data)
            if not temp_file:
                return self._empty_chord_result()
            
            try:
                # Extract chords using Chordino
                chord_changes = self.chordino.extract(temp_file)
                
                if not chord_changes:
                    return self._empty_chord_result()
                
                # Get the most recent chord (last in the sequence)
                latest_chord = chord_changes[-1]
                
                # Analyze the chord
                chord_info = self._analyze_chordino_result(latest_chord, audio_data)
                
                return chord_info
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except Exception as e:
            print(f"❌ Chordino detection error: {e}")
            return self._empty_chord_result()
    
    def _save_audio_to_temp(self, audio_data: np.ndarray) -> Optional[str]:
        """Save audio data to temporary WAV file"""
        try:
            import soundfile as sf
            
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            
            # Save as WAV file
            sf.write(temp_path, audio_data, self.sample_rate)
            
            return temp_path
            
        except ImportError:
            print("⚠️  soundfile not available. Install with: pip install soundfile")
            return None
        except Exception as e:
            print(f"❌ Error saving temp file: {e}")
            return None
    
    def _analyze_chordino_result(self, chord_change: ChordChange, audio_data: np.ndarray) -> Dict:
        """Analyze Chordino result and convert to our format"""
        try:
            # Parse chord notation (e.g., "C", "Am", "F#m7")
            chord_info = self._parse_chord_notation(chord_change.chord)
            
            # Get audio level for confidence calculation
            audio_level = np.max(np.abs(audio_data))
            
            # Calculate confidence based on audio level and chord stability
            confidence = self._calculate_confidence(audio_level, chord_change)
            
            # Create note details (simplified for now)
            note_details = self._create_note_details(chord_info, audio_level)
            
            return {
                'root': chord_info['root'],
                'quality': chord_info['quality'],
                'notes': chord_info['notes'],
                'note_details': note_details,
                'confidence': confidence,
                'valid': True,
                'timestamp': chord_change.timestamp,
                'chord_notation': chord_change.chord,
                'detection_method': 'chordino'
            }
            
        except Exception as e:
            print(f"❌ Error analyzing Chordino result: {e}")
            return self._empty_chord_result()
    
    def _parse_chord_notation(self, chord_notation: str) -> Dict:
        """Parse Chordino chord notation (e.g., 'C', 'Am', 'F#m7')"""
        if not chord_notation or chord_notation == 'N':
            return {'root': 'Unknown', 'quality': 'unknown', 'notes': []}
        
        # Handle special cases
        if chord_notation == 'N':
            return {'root': 'Unknown', 'quality': 'unknown', 'notes': []}
        
        # Parse root note
        root = chord_notation[0]
        if len(chord_notation) > 1 and chord_notation[1] in ['#', 'b']:
            root += chord_notation[1]
        
        # Parse quality
        quality = 'major'  # Default
        if 'm' in chord_notation:
            quality = 'minor'
        elif 'dim' in chord_notation:
            quality = 'diminished'
        elif 'aug' in chord_notation:
            quality = 'augmented'
        elif '7' in chord_notation:
            quality = 'dominant7'
        
        # Generate notes based on root and quality
        notes = self._generate_chord_notes(root, quality)
        
        return {
            'root': root,
            'quality': quality,
            'notes': notes
        }
    
    def _generate_chord_notes(self, root: str, quality: str) -> List[str]:
        """Generate notes for a chord based on root and quality"""
        # Chromatic scale
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Find root index
        try:
            root_idx = notes.index(root)
        except ValueError:
            return [root]
        
        # Generate notes based on quality
        if quality == 'major':
            intervals = [0, 4, 7]  # Root, major third, perfect fifth
        elif quality == 'minor':
            intervals = [0, 3, 7]  # Root, minor third, perfect fifth
        elif quality == 'diminished':
            intervals = [0, 3, 6]  # Root, minor third, diminished fifth
        elif quality == 'augmented':
            intervals = [0, 4, 8]  # Root, major third, augmented fifth
        elif quality == 'dominant7':
            intervals = [0, 4, 7, 10]  # Root, major third, perfect fifth, minor seventh
        else:
            intervals = [0]  # Just root
        
        chord_notes = []
        for interval in intervals:
            note_idx = (root_idx + interval) % 12
            chord_notes.append(notes[note_idx])
        
        return chord_notes
    
    def _create_note_details(self, chord_info: Dict, audio_level: float) -> List[Dict]:
        """Create note details for the detected chord"""
        note_details = []
        
        for i, note in enumerate(chord_info['notes']):
            # Estimate frequency based on note and octave
            # This is simplified - in practice you'd want more sophisticated frequency calculation
            base_freq = self._note_to_frequency(note, 3)  # Assume middle octave
            
            note_details.append({
                'note': note,
                'octave': 3,  # Default octave
                'frequency': base_freq,
                'strength': audio_level * (1.0 - i * 0.1),  # Decreasing strength
                'cents_off': 0,  # Chordino doesn't provide tuning info
                'tuning_status': 'unknown',
                'guitar_string': self._identify_guitar_string(base_freq),
                'detection_method': 'chordino'
            })
        
        return note_details
    
    def _note_to_frequency(self, note: str, octave: int) -> float:
        """Convert note name to frequency"""
        # Base frequencies for octave 4
        base_freqs = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }
        
        if note in base_freqs:
            # Adjust for octave
            octave_diff = octave - 4
            return base_freqs[note] * (2 ** octave_diff)
        
        return 0.0
    
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
    
    def _calculate_confidence(self, audio_level: float, chord_change: ChordChange) -> float:
        """Calculate confidence based on audio level and chord stability"""
        # Base confidence from audio level
        level_confidence = min(audio_level * 100, 1.0)
        
        # Chordino provides stable results, so high base confidence
        base_confidence = 0.8
        
        # Combine factors
        final_confidence = (level_confidence + base_confidence) / 2
        
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
        if not CHORD_EXTRACTOR_AVAILABLE:
            print("❌ chord-extractor not available for testing")
            return
        
        print(f"🎤 Testing Chordino detection for {duration} seconds...")
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

def main():
    """Test the Chordino chord detector"""
    detector = ChordinoChordDetector()
    
    if CHORD_EXTRACTOR_AVAILABLE:
        print("🎸 Chordino Chord Detector ready!")
        print("💡 This detector uses the professional Chordino algorithm")
        print("💡 It should provide much better chord recognition!")
    else:
        print("❌ chord-extractor package not available")
        print("💡 Install with: pip install chord-extractor")

if __name__ == "__main__":
    main()
