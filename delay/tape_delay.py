"""
Tape Delay Effect Implementation

A vintage tape-style delay effect with saturation, modulation, and tape-like characteristics.
"""

import numpy as np
from .base_delay import BaseDelay


class TapeDelay(BaseDelay):
    """
    Vintage tape-style delay effect with analog characteristics.
    
    Features:
    - Tape saturation and compression
    - Wow and flutter modulation
    - High-frequency rolloff
    - Tape noise simulation
    - Variable tape speed
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 delay_time: float = 0.5,
                 feedback: float = 0.4,
                 wet_mix: float = 0.6,
                 saturation: float = 0.3,
                 wow_rate: float = 0.5,
                 flutter_rate: float = 8.0,
                 tape_speed: float = 1.0):
        """
        Initialize the tape delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            delay_time: Initial delay time in seconds
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
            saturation: Tape saturation amount (0.0 to 1.0)
            wow_rate: Wow modulation rate in Hz
            flutter_rate: Flutter modulation rate in Hz
            tape_speed: Tape speed multiplier (0.5 to 2.0)
        """
        super().__init__(sample_rate, 3.0, feedback, wet_mix)
        
        # Tape-specific parameters
        self.saturation = np.clip(saturation, 0.0, 1.0)
        self.wow_rate = np.clip(wow_rate, 0.0, 2.0)
        self.flutter_rate = np.clip(flutter_rate, 0.0, 20.0)
        self.tape_speed = np.clip(tape_speed, 0.5, 2.0)
        
        # Modulation phases
        self.wow_phase = 0.0
        self.flutter_phase = 0.0
        
        # Tape characteristics
        self.tape_noise_level = 0.0001
        self.high_freq_rolloff = 0.95  # High frequency attenuation
        
        # Set initial delay time
        self.set_delay_time(delay_time)
        
        # Enable modulation for tape effect
        self.set_modulation(self.wow_rate, self.delay_samples * 0.1)
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Tape Delay"
        
    def set_tape_parameters(self, saturation: float = None,
                           wow_rate: float = None,
                           flutter_rate: float = None,
                           tape_speed: float = None):
        """
        Set tape-specific parameters.
        
        Args:
            saturation: Tape saturation amount (0.0 to 1.0)
            wow_rate: Wow modulation rate in Hz
            flutter_rate: Flutter modulation rate in Hz
            tape_speed: Tape speed multiplier (0.5 to 2.0)
        """
        if saturation is not None:
            self.saturation = np.clip(saturation, 0.0, 1.0)
        if wow_rate is not None:
            self.wow_rate = np.clip(wow_rate, 0.0, 2.0)
            self.set_modulation(self.wow_rate, self.delay_samples * 0.1)
        if flutter_rate is not None:
            self.flutter_rate = np.clip(flutter_rate, 0.0, 20.0)
        if tape_speed is not None:
            self.tape_speed = np.clip(tape_speed, 0.5, 2.0)
            # Adjust delay time based on tape speed
            self.set_delay_time(self.delay_time)
            
    def _apply_tape_saturation(self, sample: float) -> float:
        """Apply tape saturation and compression."""
        if self.saturation > 0:
            # Soft clipping saturation
            saturated = np.tanh(sample * (1 + self.saturation * 2))
            # Apply compression
            compressed = saturated * (1 - self.saturation * 0.3)
            return compressed
        return sample
        
    def _apply_tape_characteristics(self, sample: float) -> float:
        """Apply tape-like characteristics including noise and rolloff."""
        # Add tape noise
        if self.tape_noise_level > 0:
            noise = np.random.normal(0, self.tape_noise_level)
            sample += noise
            
        # High frequency rolloff (simplified)
        if self.high_freq_rolloff < 1.0:
            sample *= self.high_freq_rolloff
            
        return sample
        
    def _get_tape_modulated_delay(self) -> int:
        """Get delay time with tape wow and flutter modulation."""
        base_delay = self.delay_samples
        
        # Wow modulation (slow, large variations)
        if self.wow_rate > 0:
            wow_mod = 0.15 * np.sin(2 * np.pi * self.wow_phase)
            base_delay += int(wow_mod * self.delay_samples * 0.1)
            
        # Flutter modulation (fast, small variations)
        if self.flutter_rate > 0:
            flutter_mod = 0.05 * np.sin(2 * np.pi * self.flutter_phase)
            base_delay += int(flutter_mod * self.delay_samples * 0.05)
            
        return np.clip(base_delay, 1, self.buffer_size - 1)
        
    def _update_tape_modulation(self):
        """Update wow and flutter modulation phases."""
        if self.wow_rate > 0:
            self.wow_phase += self.wow_rate / self.sample_rate
            if self.wow_phase >= 1.0:
                self.wow_phase -= 1.0
                
        if self.flutter_rate > 0:
            self.flutter_rate += self.flutter_rate / self.sample_rate
            if self.flutter_rate >= 1.0:
                self.flutter_rate -= 1.0
                
    def set_delay_time(self, delay_time: float):
        """Set delay time, adjusted for tape speed."""
        adjusted_delay = delay_time / self.tape_speed
        super().set_delay_time(adjusted_delay)
        
    def process_sample(self, input_sample: float) -> float:
        """Process a single audio sample through the tape delay effect."""
        # Apply tape saturation to input
        saturated_input = self._apply_tape_saturation(input_sample)
        
        # Read delayed signal with tape modulation
        read_index = (self.write_index - self._get_tape_modulated_delay()) % self.buffer_size
        delayed_sample = self.delay_buffer[read_index]
        
        # Apply tape characteristics to delayed signal
        delayed_sample = self._apply_tape_characteristics(delayed_sample)
        
        # Calculate output (dry + wet)
        output_sample = (self.dry_mix * input_sample + 
                        self.wet_mix * delayed_sample)
        
        # Write to buffer with feedback
        feedback_sample = saturated_input + self.feedback * delayed_sample
        self._write_delay_buffer(feedback_sample)
        
        # Update tape modulation
        self._update_tape_modulation()
        
        return output_sample
        
    def get_parameters(self) -> dict:
        """Get current parameter values including tape-specific ones."""
        base_params = super().get_parameters()
        base_params.update({
            'saturation': self.saturation,
            'wow_rate': self.wow_rate,
            'flutter_rate': self.flutter_rate,
            'tape_speed': self.tape_speed,
            'tape_noise_level': self.tape_noise_level,
            'high_freq_rolloff': self.high_freq_rolloff
        })
        return base_params
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"{self.get_effect_name()}: "
                f"Delay={self.delay_time*1000:.0f}ms, "
                f"Feedback={self.feedback*100:.0f}%, "
                f"Wet={self.wet_mix*100:.0f}%, "
                f"Sat={self.saturation*100:.0f}%, "
                f"Speed={self.tape_speed:.1f}x")
