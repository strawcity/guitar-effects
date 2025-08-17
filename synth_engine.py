import numpy as np
import math

class SynthEngine:
    def __init__(self, config):
        self.config = config
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
        
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        carrier = np.sin(2 * np.pi * carrier_freq * t + modulation_index * modulator)
        
        return carrier
    
    def generate_pluck(self, frequency, duration):
        """Generate plucked string sound"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Karplus-Strong algorithm for plucked string
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply decay envelope
        decay = np.exp(-t * 3)  # Exponential decay
        wave = wave * decay
        
        return wave
    
    def generate_pad(self, frequency, duration):
        """Generate pad sound"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Rich harmonic content
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)  # Second harmonic
        wave += 0.25 * np.sin(2 * np.pi * frequency * 3 * t)  # Third harmonic
        
        # Soft attack and release
        envelope = self.generate_adsr_envelope(duration, 0.7, attack=0.1, release=0.3)
        wave = wave * envelope
        
        return wave
    
    def generate_lead(self, frequency, duration):
        """Generate lead sound"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Bright, cutting sound
        wave = self.generate_sawtooth(frequency, duration)
        wave += 0.3 * self.generate_square(frequency, duration)
        
        # Sharp attack
        envelope = self.generate_adsr_envelope(duration, 0.9, attack=0.01, release=0.1)
        wave = wave * envelope
        
        return wave
    
    def generate_bass(self, frequency, duration):
        """Generate bass sound"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Deep, warm bass
        wave = self.generate_sine(frequency, duration)
        wave += 0.3 * self.generate_square(frequency, duration)
        
        # Long attack and release
        envelope = self.generate_adsr_envelope(duration, 0.8, attack=0.05, release=0.4)
        wave = wave * envelope
        
        return wave
    
    def generate_adsr_envelope(self, duration, velocity, attack=0.05, decay=0.1, sustain=0.7, release=0.2):
        """Generate ADSR envelope"""
        samples = int(duration * self.sample_rate)
        envelope = np.zeros(samples)
        
        # Calculate sample positions for each phase
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = samples - attack_samples - decay_samples - release_samples
        
        # Ensure we don't exceed total samples
        if sustain_samples < 0:
            sustain_samples = 0
            release_samples = max(0, samples - attack_samples - decay_samples)
        
        # Attack phase (linear rise)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, velocity, attack_samples)
        
        # Decay phase (linear fall to sustain level)
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            envelope[start_idx:end_idx] = np.linspace(velocity, velocity * sustain, decay_samples)
        
        # Sustain phase (constant level)
        if sustain_samples > 0:
            start_idx = attack_samples + decay_samples
            end_idx = start_idx + sustain_samples
            envelope[start_idx:end_idx] = velocity * sustain
        
        # Release phase (linear fall to zero)
        if release_samples > 0:
            start_idx = samples - release_samples
            end_idx = samples
            envelope[start_idx:end_idx] = np.linspace(velocity * sustain, 0, release_samples)
        
        return envelope
