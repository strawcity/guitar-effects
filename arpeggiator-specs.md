# =============================================================================

# COMPLETE GUITAR ARPEGGIATOR SYSTEM

# =============================================================================

# =============================================================================

# FILE 1: requirements.txt

# =============================================================================

""" numpy>=1.24.0 scipy>=1.10.0 sounddevice>=0.4.6 matplotlib>=3.5.0 """

# =============================================================================

# FILE 2: config.py - Configuration and Platform Detection

# =============================================================================

import platform import os

class Config: def **init**(self): self.platform = platform.system() self.is_mac
= self.platform == "Darwin" self.is_pi = self.platform == "Linux" and
os.path.exists("/sys/firmware/devicetree/base/model")

        # Audio settings
        self.sample_rate = 48000
        self.chunk_size = 4096
        self.input_device = None  # Will auto-detect Scarlett
        self.output_device = None

        # Detection settings
        self.min_chord_confidence = 0.6
        self.chord_hold_time = 0.5  # Seconds to hold chord detection

        # Arpeggio settings
        self.default_tempo = 120
        self.default_pattern = 'up'
        self.default_synth = 'saw'

        # GPIO settings (Pi only)
        self.gpio_available = self.is_pi
        self.led_pins = {'C': 12, 'E': 13, 'G': 16} if self.is_pi else {}

        print(f"Running on: {self.platform}")
        print(f"GPIO available: {self.gpio_available}")

# =============================================================================

# FILE 3: chord_detector.py - Polyphonic Chord Detection

# =============================================================================

import numpy as np from scipy import signal import math import time

class ChordDetector: def **init**(self, config): self.config = config
self.sample_rate = config.sample_rate self.chunk_size = config.chunk_size

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
        """Extract dominant frequencies using FFT"""
        # Convert to numpy array and normalize
        audio_array = np.array(audio_data, dtype=np.float32)
        if len(audio_array) == 0:
            return []

        # Apply Hann window to reduce spectral leakage
        window = signal.windows.hann(len(audio_array))
        windowed_audio = audio_array * window

        # Perform FFT
        fft_result = np.fft.fft(windowed_audio)
        magnitude = np.abs(fft_result)

        # Create frequency bins
        frequencies = np.fft.fftfreq(len(fft_result), 1/self.sample_rate)

        # Only keep positive frequencies up to guitar range (80-2000 Hz)
        mask = (frequencies > 80) & (frequencies < 2000)
        guitar_frequencies = frequencies[mask]
        guitar_magnitudes = magnitude[mask]

        if len(guitar_magnitudes) == 0:
            return []

        # Find peaks in the spectrum
        threshold = np.max(guitar_magnitudes) * 0.15  # 15% of maximum
        peaks, properties = signal.find_peaks(
            guitar_magnitudes,
            height=threshold,
            distance=20,  # Minimum separation between peaks
            prominence=threshold * 0.5
        )

        # Get peak frequencies and magnitudes
        peak_frequencies = guitar_frequencies[peaks]
        peak_magnitudes = guitar_magnitudes[peaks]

        # Sort by magnitude (strongest first)
        sorted_indices = np.argsort(peak_magnitudes)[::-1]

        # Return top 8 frequencies
        dominant_frequencies = []
        for i in sorted_indices[:8]:
            dominant_frequencies.append({
                'frequency': peak_frequencies[i],
                'magnitude': peak_magnitudes[i]
            })

        return dominant_frequencies

    def frequencies_to_notes(self, frequency_data):
        """Convert frequencies to musical note names"""
        detected_notes = []

        for freq_info in frequency_data:
            frequency = freq_info['frequency']
            magnitude = freq_info['magnitude']

            closest_note = self.find_closest_note(frequency)

            if closest_note and abs(closest_note['cents_off']) < 50:  # Within quarter-tone
                detected_notes.append({
                    'note': closest_note['note'],
                    'octave': closest_note['octave'],
                    'frequency': frequency,
                    'strength': magnitude,
                    'cents_off': closest_note['cents_off']
                })

        # Remove duplicate notes (keep strongest)
        unique_notes = {}
        for note in detected_notes:
            note_name = note['note']
            if note_name not in unique_notes or note['strength'] > unique_notes[note_name]['strength']:
                unique_notes[note_name] = note

        return list(unique_notes.values())

    def find_closest_note(self, target_frequency):
        """Find the closest musical note to a frequency"""
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

                    closest_match = {
                        'note': note_name,
                        'octave': octave_index + 2,
                        'cents_off': cents_off,
                        'frequency_difference': difference
                    }

        return closest_match

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

# =============================================================================

# FILE 4: arpeggio_engine.py - Pattern Generation

# =============================================================================

import random import math

class ArpeggioEngine: def **init**(self, config): self.config = config
self.chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A',
'A#', 'B']

        # Arpeggio pattern functions
        self.patterns = {
            'up': self.pattern_up,
            'down': self.pattern_down,
            'up_down': self.pattern_up_down,
            'down_up': self.pattern_down_up,
            'random': self.pattern_random,
            'octave_up': self.pattern_octave_up,
            'octave_down': self.pattern_octave_down,
            'trance_16th': self.pattern_trance_16th,
            'dubstep_chop': self.pattern_dubstep_chop,
            'ambient_flow': self.pattern_ambient_flow,
            'rock_eighth': self.pattern_rock_eighth
        }

    def generate_arpeggio(self, chord, pattern_name='up', tempo=120, duration=2.0):
        """Generate arpeggio sequence from chord"""
        if not chord or not chord.get('valid') or not chord.get('notes'):
            return self.empty_arpeggio()

        # Get pattern function
        pattern_func = self.patterns.get(pattern_name, self.pattern_up)

        # Generate note sequence
        note_sequence = pattern_func(chord['notes'], duration, tempo)

        # Add timing and velocity information
        arpeggio_data = {
            'chord': chord,
            'pattern': pattern_name,
            'tempo': tempo,
            'duration': duration,
            'notes': note_sequence,
            'total_notes': len(note_sequence),
            'timestamp': chord['timestamp']
        }

        return arpeggio_data

    def pattern_up(self, notes, duration, tempo):
        """Classic ascending arpeggio"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)  # Eighth notes
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)

        while current_time < duration:
            for note in sorted_notes:
                if current_time >= duration:
                    break
                sequence.append({
                    'note': note,
                    'octave': 4,  # Default octave
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': 0.8
                })
                current_time += note_duration

        return sequence

    def pattern_down(self, notes, duration, tempo):
        """Classic descending arpeggio"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)[::-1]  # Reverse

        while current_time < duration:
            for note in sorted_notes:
                if current_time >= duration:
                    break
                sequence.append({
                    'note': note,
                    'octave': 4,
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': 0.8
                })
                current_time += note_duration

        return sequence

    def pattern_up_down(self, notes, duration, tempo):
        """Up then down pattern"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)
        pattern_notes = sorted_notes + sorted_notes[1:-1][::-1]  # Up + down without repeating ends

        while current_time < duration:
            for note in pattern_notes:
                if current_time >= duration:
                    break
                sequence.append({
                    'note': note,
                    'octave': 4,
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': 0.8
                })
                current_time += note_duration

        return sequence

    def pattern_down_up(self, notes, duration, tempo):
        """Down then up pattern"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)
        pattern_notes = sorted_notes[::-1] + sorted_notes[1:-1]  # Down + up

        while current_time < duration:
            for note in pattern_notes:
                if current_time >= duration:
                    break
                sequence.append({
                    'note': note,
                    'octave': 4,
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': 0.8
                })
                current_time += note_duration

        return sequence

    def pattern_random(self, notes, duration, tempo):
        """Random note order"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)
        sequence = []
        current_time = 0

        while current_time < duration:
            note = random.choice(notes)
            sequence.append({
                'note': note,
                'octave': 4,
                'start_time': current_time,
                'duration': note_duration,
                'velocity': random.uniform(0.6, 0.9)
            })
            current_time += note_duration

        return sequence

    def pattern_octave_up(self, notes, duration, tempo):
        """Multi-octave ascending"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 4)  # 16th notes
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)

        while current_time < duration:
            for octave in [3, 4, 5]:
                for note in sorted_notes:
                    if current_time >= duration:
                        break
                    sequence.append({
                        'note': note,
                        'octave': octave,
                        'start_time': current_time,
                        'duration': note_duration,
                        'velocity': 0.7 + (octave - 3) * 0.1
                    })
                    current_time += note_duration

        return sequence

    def pattern_octave_down(self, notes, duration, tempo):
        """Multi-octave descending"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 4)
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)[::-1]

        while current_time < duration:
            for octave in [5, 4, 3]:
                for note in sorted_notes:
                    if current_time >= duration:
                        break
                    sequence.append({
                        'note': note,
                        'octave': octave,
                        'start_time': current_time,
                        'duration': note_duration,
                        'velocity': 0.9 - (5 - octave) * 0.1
                    })
                    current_time += note_duration

        return sequence

    def pattern_trance_16th(self, notes, duration, tempo):
        """Trance-style 16th note pattern"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 4)  # 16th notes
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)

        # Trance-style emphasis pattern
        emphasis_pattern = [1.0, 0.6, 0.8, 0.7]  # Strong, weak, medium, weak

        while current_time < duration:
            for i, note in enumerate(sorted_notes):
                if current_time >= duration:
                    break

                velocity = emphasis_pattern[i % len(emphasis_pattern)] * 0.8

                sequence.append({
                    'note': note,
                    'octave': 4,
                    'start_time': current_time,
                    'duration': note_duration,
                    'velocity': velocity
                })
                current_time += note_duration

        return sequence

    def pattern_dubstep_chop(self, notes, duration, tempo):
        """Dubstep-style chopped pattern"""
        if not notes:
            return []

        sequence = []
        current_time = 0

        # Dubstep rhythm: long-short-short-pause
        rhythm_pattern = [0.5, 0.25, 0.25, 0.5]  # Beat fractions

        while current_time < duration:
            for i, beat_fraction in enumerate(rhythm_pattern):
                if current_time >= duration:
                    break

                note_duration = (60 / tempo) * beat_fraction

                if i != 3:  # Skip the pause
                    note = random.choice(notes)
                    sequence.append({
                        'note': note,
                        'octave': random.choice([3, 4, 5]),
                        'start_time': current_time,
                        'duration': note_duration * 0.8,  # Slightly shorter for chop effect
                        'velocity': 0.9 if i == 0 else 0.7
                    })

                current_time += note_duration

        return sequence

    def pattern_ambient_flow(self, notes, duration, tempo):
        """Ambient flowing pattern"""
        if not notes:
            return []

        sequence = []
        current_time = 0

        # Longer, overlapping notes
        note_duration = 60 / (tempo * 0.5)  # Half notes

        while current_time < duration:
            for note in notes:
                if current_time >= duration:
                    break

                # Add some randomness to timing and octave
                time_offset = random.uniform(-0.1, 0.1)
                octave = random.choice([3, 4, 5])

                sequence.append({
                    'note': note,
                    'octave': octave,
                    'start_time': max(0, current_time + time_offset),
                    'duration': note_duration * random.uniform(0.8, 1.5),
                    'velocity': random.uniform(0.3, 0.6)
                })
                current_time += note_duration * 0.75  # Overlap notes

        return sequence

    def pattern_rock_eighth(self, notes, duration, tempo):
        """Rock-style eighth note pattern"""
        if not notes:
            return []

        note_duration = 60 / (tempo * 2)  # Eighth notes
        sequence = []
        current_time = 0

        sorted_notes = self.sort_notes_by_pitch(notes)

        # Rock emphasis: strong on 1 and 3, medium on 2 and 4
        beat_emphasis = [1.0, 0.7, 0.9, 0.7]

        while current_time < duration:
            for beat, note in enumerate(sorted_notes):
                if current_time >= duration:
                    break

                velocity = beat_emphasis[beat % len(beat_emphasis)] * 0.8

                sequence.append({
                    'note': note,
                    'octave': 4,
                    'start_time': current_time,
                    'duration': note_duration * 0.9,  # Slightly detached
                    'velocity': velocity
                })
                current_time += note_duration

        return sequence

    def sort_notes_by_pitch(self, notes):
        """Sort notes by pitch height"""
        def note_to_pitch(note):
            try:
                return self.chromatic_scale.index(note)
            except ValueError:
                return 0

        return sorted(notes, key=note_to_pitch)

    def empty_arpeggio(self):
        """Return empty arpeggio"""
        return {
            'chord': None,
            'pattern': None,
            'tempo': self.config.default_tempo,
            'duration': 0,
            'notes': [],
            'total_notes': 0,
            'timestamp': 0
        }

# =============================================================================

# FILE 5: synth_engine.py - Electronic Sound Synthesis

# =============================================================================

import numpy as np import math

class SynthEngine: def **init**(self, config): self.config = config
self.sample_rate = config.sample_rate

        # Note to frequency mapping
        self.note_frequencies = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }

        # Synthesizer types
        self.synth_types = {
            'saw': self.generate_sawtooth,
            'square': self.generate_square,
            'sine': self.generate_sine,
            'triangle': self.generate_triangle,
            'fm': self.generate_fm_synthesis,
            'pluck': self.generate_pluck,
            'pad': self.generate_pad,
            'lead': self.generate_lead,
            'bass': self.generate_bass
        }

    def render_arpeggio(self, arpeggio_data, synth_type='saw'):
        """Render complete arpeggio to audio"""
        if not arpeggio_data or not arpeggio_data.get('notes'):
            return np.array([])

        duration = arpeggio_data['duration']
        total_samples = int(duration * self.sample_rate)
        output_audio = np.zeros(total_samples)

        # Render each note
        for note_info in arpeggio_data['notes']:
            note_audio = self.render_note(note_info, synth_type)

            # Calculate sample positions
            start_sample = int(note_info['start_time'] * self.sample_rate)
            end_sample = start_sample + len(note_audio)

            # Add note to output (with bounds checking)
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                note_length = end_sample - start_sample

                if note_length > 0:
                    output_audio[start_sample:end_sample] += note_audio[:note_length]

        # Normalize to prevent clipping
        if np.max(np.abs(output_audio)) > 0:
            output_audio = output_audio / np.max(np.abs(output_audio)) * 0.8

        return output_audio

    def render_note(self, note_info, synth_type='saw'):
        """Render single note to audio"""
        note = note_info['note']
        octave = note_info.get('octave', 4)
        duration = note_info.get('duration', 0.5)
        velocity = note_info.get('velocity', 0.8)

        # Get base frequency and adjust for octave
        base_freq = self.note_frequencies.get(note, 440.0)
        frequency = base_freq * (2 ** (octave - 4))

        # Get synthesis function
        synth_func = self.synth_types.get(synth_type, self.generate_sawtooth)

        # Generate waveform
        waveform = synth_func(frequency, duration)

        # Apply ADSR envelope
        envelope = self.generate_adsr_envelope(duration, velocity)

        # Combine waveform and envelope
        synthesized = waveform * envelope

        return synthesized

    def generate_sawtooth(self, frequency, duration):
        """Generate sawtooth wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        # Sawtooth wave using modulo
        wave = 2 * (frequency * t - np.floor(frequency * t + 0.5))

        return wave

    def generate_square(self, frequency, duration):
        """Generate square wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        # Square wave
        wave = np.sign(np.sin(2 * np.pi * frequency * t))

        return wave

    def generate_sine(self, frequency, duration):
        """Generate sine wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        wave = np.sin(2 * np.pi * frequency * t)

        return wave

    def generate_triangle(self, frequency, duration):
        """Generate triangle wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        # Triangle wave using arcsin of sine
        wave = (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t))

        return wave

    def generate_fm_synthesis(self, frequency, duration):
        """Generate FM synthesized wave"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        # FM synthesis: carrier modulated by modulator
        carrier_freq = frequency
        modulator_freq = frequency * 2.1  # Slightly non-harmonic
        modulation_index = 3

        modulator = np.sin(2 * np.pi * modulator_freq * t
