"""
Basic Delay Effect Implementation

A simple, clean delay effect with configurable delay time and feedback.
"""

import numpy as np
from .base_delay import BaseDelay


class BasicDelay(BaseDelay):
    """
    Basic delay effect providing clean echo functionality.
    
    Features:
    - Configurable delay time (1ms to 2 seconds)
    - Adjustable feedback (0% to 90%)
    - Wet/dry mix control
    - Clean, digital sound
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 delay_time: float = 0.5,
                 feedback: float = 0.3,
                 wet_mix: float = 0.5):
        """
        Initialize the basic delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            delay_time: Initial delay time in seconds
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
        """
        super().__init__(sample_rate, 2.0, feedback, wet_mix)
        self.set_delay_time(delay_time)
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Basic Delay"
        
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
