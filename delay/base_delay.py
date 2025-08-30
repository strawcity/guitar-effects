"""
Base Delay Effect Implementation

This module provides the core delay functionality that all other delay effects inherit from.
"""

import numpy as np
from typing import Optional, Tuple
from abc import ABC, abstractmethod


class BaseDelay(ABC):
    """
    Base class for all delay effects.
    
    Provides core delay line functionality with configurable buffer sizes,
    delay times, and feedback control.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 max_delay_time: float = 2.0,
                 feedback: float = 0.3,
                 wet_mix: float = 0.5):
        """
        Initialize the base delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_time: Maximum delay time in seconds
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
        """
        self.sample_rate = sample_rate
        self.max_delay_time = max_delay_time
        self.feedback = np.clip(feedback, 0.0, 0.9)
        self.wet_mix = np.clip(wet_mix, 0.0, 1.0)
        self.dry_mix = 1.0 - self.wet_mix
        
        # Calculate buffer size
        self.buffer_size = int(max_delay_time * sample_rate)
        self.delay_buffer = np.zeros(self.buffer_size)
        self.write_index = 0
        
        # Current delay time
        self.delay_time = 0.5  # Default 500ms
        self.delay_samples = int(self.delay_time * sample_rate)
        
        # Modulation parameters
        self.modulation_rate = 0.0  # Hz
        self.modulation_depth = 0.0  # samples
        self.modulation_phase = 0.0
        
    def set_delay_time(self, delay_time: float):
        """Set the delay time in seconds."""
        self.delay_time = np.clip(delay_time, 0.001, self.max_delay_time)
        self.delay_samples = int(self.delay_time * self.sample_rate)
        
    def set_feedback(self, feedback: float):
        """Set the feedback amount (0.0 to 0.9)."""
        self.feedback = np.clip(feedback, 0.0, 0.9)
        
    def set_wet_mix(self, wet_mix: float):
        """Set the wet signal mix (0.0 to 1.0)."""
        self.wet_mix = np.clip(wet_mix, 0.0, 1.0)
        self.dry_mix = 1.0 - self.wet_mix
        
    def set_modulation(self, rate: float, depth: float):
        """
        Set modulation parameters for the delay time.
        
        Args:
            rate: Modulation rate in Hz
            depth: Modulation depth in samples
        """
        self.modulation_rate = max(0.0, rate)
        self.modulation_depth = max(0.0, depth)
        
    def _get_modulated_delay(self) -> int:
        """Get the current delay time with modulation applied."""
        if self.modulation_rate > 0 and self.modulation_depth > 0:
            # Calculate modulation offset
            mod_offset = self.modulation_depth * np.sin(2 * np.pi * self.modulation_phase)
            modulated_delay = self.delay_samples + int(mod_offset)
            return np.clip(modulated_delay, 1, self.buffer_size - 1)
        return self.delay_samples
        
    def _update_modulation_phase(self):
        """Update the modulation phase."""
        if self.modulation_rate > 0:
            self.modulation_phase += self.modulation_rate / self.sample_rate
            if self.modulation_phase >= 1.0:
                self.modulation_phase -= 1.0
                
    def _read_delay_buffer(self) -> float:
        """Read from the delay buffer at the current read position."""
        read_index = (self.write_index - self._get_modulated_delay()) % self.buffer_size
        return self.delay_buffer[read_index]
        
    def _write_delay_buffer(self, sample: float):
        """Write to the delay buffer at the current write position."""
        self.delay_buffer[self.write_index] = sample
        self.write_index = (self.write_index + 1) % self.buffer_size
        
    def process_sample(self, input_sample: float) -> Tuple[float, float]:
        """
        Process a single audio sample through the delay effect.
        
        Args:
            input_sample: Input audio sample
            
        Returns:
            Tuple of (left_channel, right_channel) processed audio samples
        """
        # Read delayed signal
        delayed_sample = self._read_delay_buffer()
        
        # Calculate output (dry + wet)
        output_sample = (self.dry_mix * input_sample + 
                        self.wet_mix * delayed_sample)
        
        # Write to buffer with feedback
        feedback_sample = input_sample + self.feedback * delayed_sample
        self._write_delay_buffer(feedback_sample)
        
        # Update modulation phase
        self._update_modulation_phase()
        
        # Return stereo output (same signal on both channels for now)
        return output_sample, output_sample
        
    def process_buffer(self, input_buffer: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process an entire audio buffer through the delay effect.
        
        Args:
            input_buffer: Input audio buffer
            
        Returns:
            Tuple of (left_channel, right_channel) processed audio buffers
        """
        left_buffer = np.zeros_like(input_buffer)
        right_buffer = np.zeros_like(input_buffer)
        
        for i in range(len(input_buffer)):
            left_sample, right_sample = self.process_sample(input_buffer[i])
            left_buffer[i] = left_sample
            right_buffer[i] = right_sample
            
        return left_buffer, right_buffer
        
    def reset(self):
        """Reset the delay buffer and internal state."""
        self.delay_buffer.fill(0.0)
        self.write_index = 0
        self.modulation_phase = 0.0
        
    @abstractmethod
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        pass
