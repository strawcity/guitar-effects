"""
Stereo Delay Effect Implementation

A stereo delay effect with ping-pong delays, independent channel control,
and stereo width enhancement.
"""

import numpy as np
from .base_delay import BaseDelay
from typing import Tuple, Optional


class StereoDelay(BaseDelay):
    """
    Stereo delay effect with ping-pong and stereo enhancement.
    
    Features:
    - Independent left/right delay times
    - Ping-pong delay patterns
    - Stereo width control
    - Cross-feedback between channels
    - Stereo image enhancement
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 left_delay: float = 0.3,
                 right_delay: float = 0.6,
                 feedback: float = 0.4,
                 wet_mix: float = 0.7,
                 ping_pong: bool = True,
                 stereo_width: float = 0.5,
                 cross_feedback: float = 0.2):
        """
        Initialize the stereo delay effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            left_delay: Left channel delay time in seconds
            right_delay: Right channel delay time in seconds
            feedback: Feedback amount (0.0 to 0.9)
            wet_mix: Wet signal mix (0.0 to 1.0)
            ping_pong: Enable ping-pong delay pattern
            stereo_width: Stereo width enhancement (0.0 to 1.0)
            cross_feedback: Cross-feedback between channels (0.0 to 0.5)
        """
        super().__init__(sample_rate, 4.0, feedback, wet_mix)
        
        # Stereo-specific parameters
        self.left_delay = left_delay
        self.right_delay = right_delay
        self.ping_pong = ping_pong
        self.stereo_width = np.clip(stereo_width, 0.0, 1.0)
        self.cross_feedback = np.clip(cross_feedback, 0.0, 0.5)
        
        # Separate buffers for left and right channels
        self.left_buffer_size = int(left_delay * sample_rate)
        self.right_buffer_size = int(right_delay * sample_rate)
        
        self.left_buffer = np.zeros(self.left_buffer_size)
        self.right_buffer = np.zeros(self.right_buffer_size)
        
        self.left_write_index = 0
        self.right_write_index = 0
        
        # Stereo enhancement
        self.mid_side_enabled = stereo_width > 0.0
        
    def get_effect_name(self) -> str:
        """Return the name of this delay effect."""
        return "Stereo Delay"
        
    def set_left_delay(self, delay_time: float):
        """Set the left channel delay time."""
        self.left_delay = np.clip(delay_time, 0.001, self.max_delay_time)
        new_buffer_size = int(self.left_delay * self.sample_rate)
        
        if new_buffer_size != len(self.left_buffer):
            self.left_buffer = np.zeros(new_buffer_size)
            self.left_write_index = 0
            
    def set_right_delay(self, delay_time: float):
        """Set the right channel delay time."""
        self.right_delay = np.clip(delay_time, 0.001, self.max_delay_time)
        new_buffer_size = int(self.right_delay * self.sample_rate)
        
        if new_buffer_size != len(self.right_buffer):
            self.right_buffer = np.zeros(new_buffer_size)
            self.right_write_index = 0
            
    def set_stereo_parameters(self, ping_pong: bool = None,
                             stereo_width: float = None,
                             cross_feedback: float = None):
        """
        Set stereo-specific parameters.
        
        Args:
            ping_pong: Enable ping-pong delay pattern
            stereo_width: Stereo width enhancement (0.0 to 1.0)
            cross_feedback: Cross-feedback between channels (0.0 to 0.5)
        """
        if ping_pong is not None:
            self.ping_pong = ping_pong
        if stereo_width is not None:
            self.stereo_width = np.clip(stereo_width, 0.0, 1.0)
            self.mid_side_enabled = self.stereo_width > 0.0
        if cross_feedback is not None:
            self.cross_feedback = np.clip(cross_feedback, 0.0, 0.5)
            
    def _read_stereo_delays(self) -> Tuple[float, float]:
        """Read delayed signals from both channels."""
        # Left channel delay
        left_read_idx = (self.left_write_index - int(self.left_delay * self.sample_rate)) % len(self.left_buffer)
        left_delayed = self.left_buffer[left_read_idx]
        
        # Right channel delay
        right_read_idx = (self.right_write_index - int(self.right_delay * self.sample_rate)) % len(self.right_buffer)
        right_delayed = self.right_buffer[right_read_idx]
        
        return left_delayed, right_delayed
        
    def _apply_ping_pong(self, left_delayed: float, right_delayed: float) -> Tuple[float, float]:
        """Apply ping-pong delay pattern."""
        if self.ping_pong:
            # Swap delays for ping-pong effect
            return right_delayed, left_delayed
        return left_delayed, right_delayed
        
    def _apply_stereo_enhancement(self, left_sample: float, right_sample: float) -> Tuple[float, float]:
        """Apply stereo width enhancement using mid-side processing."""
        if not self.mid_side_enabled:
            return left_sample, right_sample
            
        # Convert to mid-side
        mid = (left_sample + right_sample) * 0.5
        side = (left_sample - right_sample) * 0.5
        
        # Enhance side signal
        enhanced_side = side * (1 + self.stereo_width)
        
        # Convert back to left-right
        enhanced_left = mid + enhanced_side
        enhanced_right = mid - enhanced_side
        
        return enhanced_left, enhanced_right
        
    def _write_stereo_buffers(self, left_sample: float, right_sample: float):
        """Write to both stereo buffers with cross-feedback."""
        # Calculate cross-feedback
        left_feedback = left_sample + self.cross_feedback * right_sample
        right_feedback = right_sample + self.cross_feedback * left_sample
        
        # Write to buffers
        self.left_buffer[self.left_write_index] = left_feedback
        self.right_buffer[self.right_write_index] = right_feedback
        
        # Update write indices
        self.left_write_index = (self.left_write_index + 1) % len(self.left_buffer)
        self.right_write_index = (self.right_write_index + 1) % len(self.right_buffer)
        
    def process_sample(self, left_input: float, right_input: float) -> Tuple[float, float]:
        """
        Process stereo audio samples through the stereo delay effect.
        
        Args:
            left_input: Left channel input sample
            right_input: Right channel input sample
            
        Returns:
            Tuple of (left_output, right_output) samples
        """
        # Read delayed signals
        left_delayed, right_delayed = self._read_stereo_delays()
        
        # Apply ping-pong if enabled
        left_delayed, right_delayed = self._apply_ping_pong(left_delayed, right_delayed)
        
        # Apply stereo enhancement
        left_delayed, right_delayed = self._apply_stereo_enhancement(left_delayed, right_delayed)
        
        # Calculate outputs (dry + wet)
        left_output = (self.dry_mix * left_input + 
                      self.wet_mix * left_delayed)
        right_output = (self.dry_mix * right_input + 
                       self.wet_mix * right_delayed)
        
        # Write to buffers with feedback
        left_feedback_sample = left_input + self.feedback * left_delayed
        right_feedback_sample = right_input + self.feedback * right_delayed
        
        self._write_stereo_buffers(left_feedback_sample, right_feedback_sample)
        
        return left_output, right_output
        
    def process_buffer(self, left_input: np.ndarray, right_input: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process stereo audio buffers through the stereo delay effect.
        
        Args:
            left_input: Left channel input buffer
            right_input: Right channel input buffer
            
        Returns:
            Tuple of (left_output, right_output) buffers
        """
        if len(left_input) != len(right_input):
            raise ValueError("Input buffers must have the same length")
            
        left_output = np.zeros_like(left_input)
        right_output = np.zeros_like(right_input)
        
        for i in range(len(left_input)):
            left_output[i], right_output[i] = self.process_sample(left_input[i], right_input[i])
            
        return left_output, right_output
        
    def process_mono_to_stereo(self, input_buffer: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process mono input to stereo output with stereo delay effect.
        
        Args:
            input_buffer: Mono input buffer
            
        Returns:
            Tuple of (left_output, right_output) buffers
        """
        left_output = np.zeros_like(input_buffer)
        right_output = np.zeros_like(input_buffer)
        
        for i in range(len(input_buffer)):
            left_output[i], right_output[i] = self.process_sample(input_buffer[i], input_buffer[i])
            
        return left_output, right_output
        
    def reset(self):
        """Reset all buffers and internal state."""
        super().reset()
        self.left_buffer.fill(0.0)
        self.right_buffer.fill(0.0)
        self.left_write_index = 0
        self.right_write_index = 0
        
    def get_stereo_info(self) -> str:
        """Get stereo-specific information."""
        return (f"Left: {self.left_delay*1000:.0f}ms, "
                f"Right: {self.right_delay*1000:.0f}ms, "
                f"Ping-pong: {'On' if self.ping_pong else 'Off'}, "
                f"Width: {self.stereo_width*100:.0f}%")
                
    def get_parameters(self) -> dict:
        """Get current parameter values including stereo-specific ones."""
        base_params = super().get_parameters()
        base_params.update({
            'left_delay': self.left_delay,
            'right_delay': self.right_delay,
            'ping_pong': self.ping_pong,
            'stereo_width': self.stereo_width,
            'cross_feedback': self.cross_feedback,
            'mid_side_enabled': self.mid_side_enabled
        })
        return base_params
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"{self.get_effect_name()}: "
                f"L={self.left_delay*1000:.0f}ms, "
                f"R={self.right_delay*1000:.0f}ms, "
                f"Feedback={self.feedback*100:.0f}%, "
                f"Wet={self.wet_mix*100:.0f}%")
