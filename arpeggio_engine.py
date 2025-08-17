import random
import math

class ArpeggioEngine:
    def __init__(self, config):
        self.config = config
        self.chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
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
