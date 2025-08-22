"""
Tempo-Synced Delay Effect Implementation

A delay effect that automatically synchronizes delay times to musical tempo,
providing rhythmic echoes that stay in time with the music.
"""

import numpy as np
from .base_delay import BaseDelay
from typing import List, Optional


class TempoSyncedDelay(BaseDelay):
    """
    Tempo-synced delay effect with musical timing.
    
    Features:
    - Automatic tempo synchronization
    - Multiple note division options
    - Dotted and triplet note support
    - Tempo tap detection
    - Musical feel adjustments
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 bpm: float = 120.0,
                 note_division: str = '1/4',
                 feedback: float = 0.4,
                 wet_mix: float = 0.6,
                 swing: float = 0.0,
                 humanize: float = 0.0):
        """
        Initialize the tempo-synced delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            bpm: Tempo in beats per minute
            note_division: Note division (e.g., '1/4', '1/8', '1/16')
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
            swing: Swing amount (0.0 to 1.0)
            humanize: Humanization amount (0.0 to 1.0)
        """
        super().__init__(sample_rate, 4.0, feedback, wet_mix)
        
        # Tempo-specific parameters
        self.bpm = bpm
        self.note_division = note_division
        self.swing = np.clip(swing, 0.0, 1.0)
        self.humanize = np.clip(humanize, 0.0, 1.0)
        
        # Note division mapping
        self.division_map = {
            '1/32': 0.125, '1/16': 0.25, '1/8': 0.5, '1/4': 1.0,
            '1/2': 2.0, '1/1': 4.0, '3/4': 0.75, '3/8': 0.375,
            '1/16T': 0.167, '1/8T': 0.333, '1/4T': 0.667,  # Triplets
            '1/8D': 0.75, '1/4D': 1.5, '1/2D': 3.0,  # Dotted notes
        }
        
        # Calculate initial delay time
        self._update_delay_time()
        
        # Humanization state
        self.humanize_phase = 0.0
        self.humanize_rate = 0.1  # Hz
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Tempo-Synced Delay"
        
    def set_tempo(self, bpm: float):
        """Set the tempo and recalculate delay time."""
        self.bpm = max(20.0, min(300.0, bpm))
        self._update_delay_time()
        
    def set_note_division(self, note_division: str):
        """Set the note division and recalculate delay time."""
        if note_division in self.division_map:
            self.note_division = note_division
            self._update_delay_time()
            
    def set_swing(self, swing: float):
        """Set the swing amount (0.0 to 1.0)."""
        self.swing = np.clip(swing, 0.0, 1.0)
        
    def set_humanize(self, humanize: float):
        """Set the humanization amount (0.0 to 1.0)."""
        self.humanize = np.clip(humanize, 0.0, 1.0)
        
    def _update_delay_time(self):
        """Calculate delay time based on current tempo and note division."""
        if self.note_division in self.division_map:
            beat_time = 60.0 / self.bpm  # Time per beat in seconds
            division_multiplier = self.division_map[self.note_division]
            base_delay_time = beat_time * division_multiplier
            
            # Apply swing if enabled
            if self.swing > 0 and 'T' not in self.note_division:  # No swing on triplets
                swing_amount = self.swing * 0.3  # Max 30% swing
                if 'D' in self.note_division:  # Dotted notes get more swing
                    swing_amount *= 1.5
                base_delay_time *= (1 + swing_amount)
                
            self.set_delay_time(base_delay_time)
            
    def _get_humanized_delay(self) -> int:
        """Get delay time with humanization applied."""
        if self.humanize > 0:
            # Subtle timing variations
            humanize_offset = (np.sin(2 * np.pi * self.humanize_phase) * 
                             self.humanize * 0.1 * self.delay_samples)
            humanized_delay = self.delay_samples + int(humanize_offset)
            return np.clip(humanized_delay, 1, self.buffer_size - 1)
        return self.delay_samples
        
    def _update_humanize_phase(self):
        """Update the humanization phase."""
        if self.humanize > 0:
            self.humanize_phase += self.humanize_rate / self.sample_rate
            if self.humanize_phase >= 1.0:
                self.humanize_phase -= 1.0
                
    def tap_tempo(self, tap_times: List[float]):
        """
        Detect tempo from tap times.
        
        Args:
            tap_times: List of tap timestamps in seconds
        """
        if len(tap_times) < 2:
            return
            
        # Calculate intervals between taps
        intervals = []
        for i in range(1, len(tap_times)):
            interval = tap_times[i] - tap_times[i-1]
            if 0.1 < interval < 4.0:  # Reasonable tempo range
                intervals.append(interval)
                
        if intervals:
            # Use median interval for stability
            median_interval = np.median(intervals)
            detected_bpm = 60.0 / median_interval
            self.set_tempo(detected_bpm)
            
    def get_available_divisions(self) -> List[str]:
        """Get list of available note divisions."""
        return list(self.division_map.keys())
        
    def get_musical_info(self) -> str:
        """Get musical timing information."""
        beat_time = 60.0 / self.bpm
        note_time = beat_time * self.division_map.get(self.note_division, 1.0)
        
        return (f"Tempo: {self.bpm:.1f} BPM, "
                f"Beat: {beat_time*1000:.0f}ms, "
                f"Note: {self.note_division} ({note_time*1000:.0f}ms)")
                
    def process_sample(self, input_sample: float) -> float:
        """Process a single audio sample through the tempo-synced delay effect."""
        # Read delayed signal with humanization
        delayed_sample = self._read_delay_buffer()
        
        # Calculate output (dry + wet)
        output_sample = (self.dry_mix * input_sample + 
                        self.wet_mix * delayed_sample)
        
        # Write to buffer with feedback
        feedback_sample = input_sample + self.feedback * delayed_sample
        self._write_delay_buffer(feedback_sample)
        
        # Update humanization phase
        self._update_humanize_phase()
        
        return output_sample
        
    def get_parameters(self) -> dict:
        """Get current parameter values including tempo-specific ones."""
        base_params = super().get_parameters()
        base_params.update({
            'bpm': self.bpm,
            'note_division': self.note_division,
            'swing': self.swing,
            'humanize': self.humanize,
            'beat_time': 60.0 / self.bpm,
            'note_time': self.delay_time
        })
        return base_params
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"{self.get_effect_name()}: "
                f"{self.bpm:.1f} BPM, "
                f"{self.note_division} note, "
                f"Delay={self.delay_time*1000:.0f}ms, "
                f"Feedback={self.feedback*100:.0f}%, "
                f"Wet={self.wet_mix*100:.0f}%")
                
    def sync_to_external_clock(self, clock_signal: float, clock_threshold: float = 0.5):
        """
        Sync to external clock signal.
        
        Args:
            clock_signal: External clock signal (0.0 to 1.0)
            clock_threshold: Threshold for clock detection
        """
        # Simple clock detection - could be enhanced with proper PLL
        if clock_signal > clock_threshold:
            # Reset humanization phase on clock
            self.humanize_phase = 0.0
