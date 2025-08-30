"""
Basic Delay Effect Implementation

A simple, clean delay effect with configurable delay time and feedback.
"""

import numpy as np
from typing import Tuple
from .base_delay import BaseDelay


class BasicDelay(BaseDelay):
    """
    Basic delay effect providing clean echo functionality with stereo separation.
    
    Features:
    - Configurable delay time (1ms to 2 seconds)
    - Adjustable feedback (0% to 90%)
    - Wet/dry mix control
    - Stereo separation for spatial effect
    - Clean, digital sound
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 delay_time: float = 0.5,
                 feedback: float = 0.3,
                 wet_mix: float = 0.5,
                 stereo_width: float = 0.3):
        """
        Initialize the basic delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            delay_time: Initial delay time in seconds
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
            stereo_width: Stereo separation width (0.0 to 1.0)
        """
        super().__init__(sample_rate, 2.0, feedback, wet_mix)
        self.set_delay_time(delay_time)
        self.stereo_width = np.clip(stereo_width, 0.0, 1.0)
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Basic Delay"
        
    def process_sample(self, input_sample: float) -> Tuple[float, float]:
        """
        Process a single audio sample with stereo separation.
        
        Args:
            input_sample: Input audio sample
            
        Returns:
            Tuple of (left_channel, right_channel) processed audio samples
        """
        # Read delayed signal
        delayed_sample = self._read_delay_buffer()
        
        # Calculate base output (dry + wet)
        output_sample = (self.dry_mix * input_sample + 
                        self.wet_mix * delayed_sample)
        
        # Apply stereo separation
        left_sample = output_sample * (1.0 - self.stereo_width * 0.5)
        right_sample = output_sample * (1.0 + self.stereo_width * 0.5)
        
        # Write to buffer with feedback
        feedback_sample = input_sample + self.feedback * delayed_sample
        self._write_delay_buffer(feedback_sample)
        
        # Update modulation phase
        self._update_modulation_phase()
        
        return left_sample, right_sample
        
    def set_parameters(self, delay_time: float = None, 
                      feedback: float = None, 
                      wet_mix: float = None):
        """
        Set multiple parameters at once.
        
        Args:
            delay_time: New delay time in seconds
            feedback: New feedback amount (0.0 to 0.9)
            wet_mix: New wet signal mix (0.0 to 1.0)
        """
        if delay_time is not None:
            self.set_delay_time(delay_time)
        if feedback is not None:
            self.set_feedback(feedback)
        if wet_mix is not None:
            self.set_wet_mix(wet_mix)
            
    def get_parameters(self) -> dict:
        """Get current parameter values."""
        return {
            'delay_time': self.delay_time,
            'feedback': self.feedback,
            'wet_mix': self.wet_mix,
            'dry_mix': self.dry_mix
        }
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"{self.get_effect_name()}: "
                f"Delay={self.delay_time*1000:.0f}ms, "
                f"Feedback={self.feedback*100:.0f}%, "
                f"Wet={self.wet_mix*100:.0f}%")
