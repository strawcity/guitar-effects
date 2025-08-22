"""
Multi-Tap Delay Effect Implementation

A complex delay effect with multiple delay lines, each with individual control over
delay time, level, and panning for stereo effects.
"""

import numpy as np
from .base_delay import BaseDelay
from typing import List, Tuple


class DelayTap:
    """Individual delay tap with its own parameters."""
    
    def __init__(self, delay_time: float, level: float = 1.0, pan: float = 0.0):
        """
        Initialize a delay tap.
        
        Args:
            delay_time: Delay time in seconds
            level: Output level (0.0 to 1.0)
            pan: Stereo panning (-1.0 = left, 0.0 = center, 1.0 = right)
        """
        self.delay_time = delay_time
        self.level = np.clip(level, 0.0, 1.0)
        self.pan = np.clip(pan, -1.0, 1.0)
        
        # Calculate stereo gains
        self.left_gain = np.sqrt(2) / 2 * (1 - self.pan)
        self.right_gain = np.sqrt(2) / 2 * (1 + self.pan)
        
    def set_parameters(self, delay_time: float = None, 
                      level: float = None, 
                      pan: float = None):
        """Set tap parameters."""
        if delay_time is not None:
            self.delay_time = delay_time
        if level is not None:
            self.level = np.clip(level, 0.0, 1.0)
        if pan is not None:
            self.pan = np.clip(pan, -1.0, 1.0)
            self.left_gain = np.sqrt(2) / 2 * (1 - self.pan)
            self.right_gain = np.sqrt(2) / 2 * (1 + self.pan)


class MultiTapDelay(BaseDelay):
    """
    Multi-tap delay effect with complex delay patterns.
    
    Features:
    - Multiple delay taps with individual control
    - Stereo panning for each tap
    - Rhythmic delay patterns
    - Individual feedback control
    - Tap synchronization
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 max_delay_time: float = 4.0,
                 feedback: float = 0.3,
                 wet_mix: float = 0.7):
        """
        Initialize the multi-tap delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_time: Maximum delay time in seconds
            feedback: Global feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
        """
        super().__init__(sample_rate, max_delay_time, feedback, wet_mix)
        
        # Multi-tap specific
        self.taps: List[DelayTap] = []
        self.tap_buffers: List[np.ndarray] = []
        self.tap_write_indices: List[int] = []
        self.tap_read_indices: List[int] = []
        
        # Stereo output
        self.stereo_output = True
        
        # Initialize with some default taps
        self._add_default_taps()
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Multi-Tap Delay"
        
    def _add_default_taps(self):
        """Add some default taps for immediate use."""
        default_taps = [
            (0.25, 0.8, 0.0),    # 250ms, 80%, center
            (0.5, 0.6, -0.3),    # 500ms, 60%, left
            (0.75, 0.4, 0.3),    # 750ms, 40%, right
        ]
        
        for delay_time, level, pan in default_taps:
            self.add_tap(delay_time, level, pan)
            
    def add_tap(self, delay_time: float, level: float = 1.0, pan: float = 0.0):
        """
        Add a new delay tap.
        
        Args:
            delay_time: Delay time in seconds
            level: Output level (0.0 to 1.0)
            pan: Stereo panning (-1.0 = left, 0.0 = center, 1.0 = right)
        """
        tap = DelayTap(delay_time, level, pan)
        self.taps.append(tap)
        
        # Create buffer for this tap
        tap_buffer_size = int(delay_time * self.sample_rate)
        tap_buffer = np.zeros(tap_buffer_size)
        self.tap_buffers.append(tap_buffer)
        
        # Initialize indices
        self.tap_write_indices.append(0)
        self.tap_read_indices.append(0)
        
    def remove_tap(self, tap_index: int):
        """Remove a delay tap by index."""
        if 0 <= tap_index < len(self.taps):
            del self.taps[tap_index]
            del self.tap_buffers[tap_index]
            del self.tap_write_indices[tap_index]
            del self.tap_read_indices[tap_index]
            
    def clear_taps(self):
        """Remove all delay taps."""
        self.taps.clear()
        self.tap_buffers.clear()
        self.tap_write_indices.clear()
        self.tap_read_indices.clear()
        
    def set_tap_parameters(self, tap_index: int, 
                          delay_time: float = None,
                          level: float = None, 
                          pan: float = None):
        """
        Set parameters for a specific tap.
        
        Args:
            tap_index: Index of the tap to modify
            delay_time: New delay time in seconds
            level: New output level (0.0 to 1.0)
            pan: New stereo panning (-1.0 to 1.0)
        """
        if 0 <= tap_index < len(self.taps):
            tap = self.taps[tap_index]
            tap.set_parameters(delay_time, level, pan)
            
            # If delay time changed, resize buffer
            if delay_time is not None:
                new_buffer_size = int(delay_time * self.sample_rate)
                if new_buffer_size != len(self.tap_buffers[tap_index]):
                    self.tap_buffers[tap_index] = np.zeros(new_buffer_size)
                    self.tap_write_indices[tap_index] = 0
                    self.tap_read_indices[tap_index] = 0
                    
    def sync_taps_to_tempo(self, bpm: float, note_divisions: List[str] = None):
        """
        Synchronize delay taps to musical tempo.
        
        Args:
            bpm: Tempo in beats per minute
            note_divisions: List of note divisions (e.g., ['1/4', '1/2', '3/4'])
        """
        if note_divisions is None:
            note_divisions = ['1/4', '1/2', '3/4']
            
        # Clear existing taps
        self.clear_taps()
        
        # Calculate delay times based on tempo
        beat_time = 60.0 / bpm
        
        # Note division multipliers
        division_map = {
            '1/16': 0.25, '1/8': 0.5, '1/4': 1.0, '1/2': 2.0,
            '3/4': 0.75, '3/8': 0.375, '1/1': 4.0
        }
        
        # Add synchronized taps
        for i, division in enumerate(note_divisions):
            if division in division_map:
                delay_time = beat_time * division_map[division]
                level = 1.0 - (i * 0.2)  # Decreasing levels
                pan = (i % 2) * 0.6 - 0.3  # Alternating pan
                self.add_tap(delay_time, level, pan)
                
    def process_sample(self, input_sample: float) -> Tuple[float, float]:
        """
        Process a single audio sample through the multi-tap delay effect.
        
        Returns:
            Tuple of (left_channel, right_channel) samples
        """
        # Initialize stereo output
        left_output = 0.0
        right_output = 0.0
        
        # Process each tap
        for i, (tap, buffer, write_idx, read_idx) in enumerate(
            zip(self.taps, self.tap_buffers, self.tap_write_indices, self.tap_read_indices)):
            
            # Read delayed signal from this tap
            delayed_sample = buffer[read_idx]
            
            # Apply tap level and panning
            left_sample = delayed_sample * tap.level * tap.left_gain
            right_sample = delayed_sample * tap.level * tap.right_gain
            
            # Add to output
            left_output += left_sample
            right_output += right_sample
            
            # Update read index
            tap_delay_samples = int(tap.delay_time * self.sample_rate)
            new_read_idx = (write_idx - tap_delay_samples) % len(buffer)
            self.tap_read_indices[i] = new_read_idx
            
        # Apply global feedback and write to all tap buffers
        feedback_sample = input_sample + self.feedback * (left_output + right_output) * 0.5
        
        for i, (buffer, write_idx) in enumerate(zip(self.tap_buffers, self.tap_write_indices)):
            buffer[write_idx] = feedback_sample
            self.tap_write_indices[i] = (write_idx + 1) % len(buffer)
            
        # Calculate final output (dry + wet)
        dry_left = input_sample * self.dry_mix
        dry_right = input_sample * self.dry_mix
        wet_left = left_output * self.wet_mix
        wet_right = right_output * self.wet_mix
        
        final_left = dry_left + wet_left
        final_right = dry_right + wet_right
        
        return final_left, final_right
        
    def process_buffer(self, input_buffer: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process an entire audio buffer through the multi-tap delay effect.
        
        Args:
            input_buffer: Input audio buffer (mono)
            
        Returns:
            Tuple of (left_channel, right_channel) buffers
        """
        left_buffer = np.zeros_like(input_buffer)
        right_buffer = np.zeros_like(input_buffer)
        
        for i in range(len(input_buffer)):
            left_sample, right_sample = self.process_sample(input_buffer[i])
            left_buffer[i] = left_sample
            right_buffer[i] = right_sample
            
        return left_buffer, right_buffer
        
    def get_tap_info(self) -> List[str]:
        """Get information about all taps."""
        tap_info = []
        for i, tap in enumerate(self.taps):
            info = (f"Tap {i+1}: {tap.delay_time*1000:.0f}ms, "
                   f"Level={tap.level*100:.0f}%, Pan={tap.pan:.1f}")
            tap_info.append(info)
        return tap_info
        
    def get_parameters(self) -> dict:
        """Get current parameter values including tap information."""
        base_params = super().get_parameters()
        base_params.update({
            'num_taps': len(self.taps),
            'stereo_output': self.stereo_output,
            'taps': [tap.get_parameters() for tap in self.taps]
        })
        return base_params
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"{self.get_effect_name()}: "
                f"{len(self.taps)} taps, "
                f"Feedback={self.feedback*100:.0f}%, "
                f"Wet={self.wet_mix*100:.0f}%")
