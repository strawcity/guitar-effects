"""
Distortion Effects for Cross-Feedback Enhancement

This module provides various distortion algorithms that can be applied to
cross-feedback signals in stereo delay effects to create more interesting
and musical feedback patterns.
"""

import numpy as np
from typing import Optional, Callable
from enum import Enum


class DistortionType(Enum):
    """Types of distortion available."""
    SOFT_CLIP = "soft_clip"
    HARD_CLIP = "hard_clip"
    TUBE = "tube"
    FUZZ = "fuzz"
    BIT_CRUSH = "bit_crush"
    WAVESHAPER = "waveshaper"
    NONE = "none"


class DistortionEffect:
    """
    Distortion effect that can be applied to cross-feedback signals.
    
    Provides various distortion algorithms including soft clipping, hard clipping,
    tube simulation, fuzz, bit crushing, and waveshaping.
    """
    
    def __init__(self, 
                 distortion_type: DistortionType = DistortionType.SOFT_CLIP,
                 drive: float = 0.5,
                 mix: float = 1.0,
                 sample_rate: int = 44100):
        """
        Initialize the distortion effect.
        
        Args:
            distortion_type: Type of distortion to apply
            drive: Drive amount (0.0 to 1.0)
            mix: Wet/dry mix (0.0 to 1.0)
            sample_rate: Audio sample rate in Hz
        """
        self.distortion_type = distortion_type
        self.drive = np.clip(drive, 0.0, 1.0)
        self.mix = np.clip(mix, 0.0, 1.0)
        self.sample_rate = sample_rate
        
        # Distortion-specific parameters
        self.bit_depth = 8  # For bit crushing
        self.sample_rate_reduction = 0.5  # For bit crushing
        self.last_sample = 0.0  # For sample rate reduction
        
        # Waveshaper curve (cubic polynomial)
        self.waveshaper_curve = self._create_waveshaper_curve()
        
    def _create_waveshaper_curve(self) -> Callable[[float], float]:
        """Create a waveshaper curve for musical distortion."""
        def waveshaper(x: float) -> float:
            # Cubic polynomial waveshaper
            return x - (x**3) / 3.0
        return waveshaper
        
    def set_distortion_type(self, distortion_type: DistortionType):
        """Set the type of distortion."""
        self.distortion_type = distortion_type
        
    def set_drive(self, drive: float):
        """Set the drive amount (0.0 to 1.0)."""
        self.drive = np.clip(drive, 0.0, 1.0)
        
    def set_mix(self, mix: float):
        """Set the wet/dry mix (0.0 to 1.0)."""
        self.mix = np.clip(mix, 0.0, 1.0)
        
    def set_bit_crush_parameters(self, bit_depth: int, sample_rate_reduction: float):
        """
        Set bit crushing parameters.
        
        Args:
            bit_depth: Bit depth (1-16)
            sample_rate_reduction: Sample rate reduction factor (0.0 to 1.0)
        """
        self.bit_depth = max(1, min(16, bit_depth))
        self.sample_rate_reduction = np.clip(sample_rate_reduction, 0.0, 1.0)
        
    def _soft_clip(self, sample: float) -> float:
        """Apply soft clipping distortion."""
        # Tanh-based soft clipping
        drive_factor = 1.0 + self.drive * 10.0
        return np.tanh(sample * drive_factor) / drive_factor
        
    def _hard_clip(self, sample: float) -> float:
        """Apply hard clipping distortion."""
        threshold = 1.0 - self.drive
        if abs(sample) > threshold:
            return np.sign(sample) * threshold
        return sample
        
    def _tube_distortion(self, sample: float) -> float:
        """Apply tube-style distortion."""
        # Asymmetric tube-like distortion
        drive_factor = 1.0 + self.drive * 5.0
        if sample > 0:
            return np.tanh(sample * drive_factor) / drive_factor
        else:
            return -np.tanh(-sample * drive_factor * 0.7) / (drive_factor * 0.7)
            
    def _fuzz_distortion(self, sample: float) -> float:
        """Apply fuzz-style distortion."""
        # Aggressive fuzz with hard clipping
        drive_factor = 1.0 + self.drive * 20.0
        distorted = sample * drive_factor
        
        # Hard clip with some soft clipping
        if abs(distorted) > 0.8:
            return np.sign(distorted) * (0.8 + 0.2 * np.tanh((abs(distorted) - 0.8) * 5.0))
        return distorted
        
    def _bit_crush(self, sample: float) -> float:
        """Apply bit crushing distortion."""
        # Quantize to bit depth
        max_value = 2**(self.bit_depth - 1) - 1
        quantized = np.round(sample * max_value) / max_value
        
        # Sample rate reduction
        if np.random.random() < self.sample_rate_reduction:
            return quantized
        else:
            return self.last_sample
            
    def _waveshaper(self, sample: float) -> float:
        """Apply waveshaper distortion."""
        return self.waveshaper_curve(sample * (1.0 + self.drive * 3.0))
        
    def process_sample(self, sample: float) -> float:
        """
        Process a single sample through the distortion effect.
        
        Args:
            sample: Input sample
            
        Returns:
            Distorted output sample
        """
        if self.distortion_type == DistortionType.NONE:
            return sample
            
        # Apply drive
        driven_sample = sample * (1.0 + self.drive * 5.0)
        
        # Apply distortion based on type
        if self.distortion_type == DistortionType.SOFT_CLIP:
            distorted = self._soft_clip(driven_sample)
        elif self.distortion_type == DistortionType.HARD_CLIP:
            distorted = self._hard_clip(driven_sample)
        elif self.distortion_type == DistortionType.TUBE:
            distorted = self._tube_distortion(driven_sample)
        elif self.distortion_type == DistortionType.FUZZ:
            distorted = self._fuzz_distortion(driven_sample)
        elif self.distortion_type == DistortionType.BIT_CRUSH:
            distorted = self._bit_crush(driven_sample)
        elif self.distortion_type == DistortionType.WAVESHAPER:
            distorted = self._waveshaper(driven_sample)
        else:
            distorted = driven_sample
            
        # Update last sample for bit crushing
        self.last_sample = distorted
        
        # Apply mix
        return sample * (1.0 - self.mix) + distorted * self.mix
        
    def process_buffer(self, buffer: np.ndarray) -> np.ndarray:
        """
        Process an entire buffer through the distortion effect.
        
        Args:
            buffer: Input buffer
            
        Returns:
            Distorted output buffer
        """
        output = np.zeros_like(buffer)
        for i in range(len(buffer)):
            output[i] = self.process_sample(buffer[i])
        return output
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        return (f"Distortion: {self.distortion_type.value}, "
                f"Drive: {self.drive*100:.0f}%, "
                f"Mix: {self.mix*100:.0f}%")


class CrossFeedbackDistortion:
    """
    Specialized distortion for cross-feedback signals in stereo delay.
    
    This class provides distortion that's specifically designed to work well
    with cross-feedback signals, creating musical and interesting feedback
    patterns.
    """
    
    def __init__(self, 
                 enabled: bool = True,
                 distortion_type: DistortionType = DistortionType.SOFT_CLIP,
                 drive: float = 0.3,
                 mix: float = 0.7,
                 sample_rate: int = 44100):
        """
        Initialize cross-feedback distortion.
        
        Args:
            enabled: Whether distortion is enabled
            distortion_type: Type of distortion to apply
            drive: Drive amount (0.0 to 1.0)
            mix: Wet/dry mix (0.0 to 1.0)
            sample_rate: Audio sample rate in Hz
        """
        self.enabled = enabled
        self.distortion = DistortionEffect(distortion_type, drive, mix, sample_rate)
        
        # Cross-feedback specific parameters
        self.feedback_intensity = 0.5  # How much the distortion affects feedback
        self.frequency_dependent = True  # Apply different distortion based on frequency
        
    def set_enabled(self, enabled: bool):
        """Enable or disable cross-feedback distortion."""
        self.enabled = enabled
        
    def set_distortion_type(self, distortion_type: DistortionType):
        """Set the type of distortion."""
        self.distortion.set_distortion_type(distortion_type)
        
    def set_drive(self, drive: float):
        """Set the drive amount."""
        self.distortion.set_drive(drive)
        
    def set_mix(self, mix: float):
        """Set the wet/dry mix."""
        self.distortion.set_mix(mix)
        
    def set_feedback_intensity(self, intensity: float):
        """Set how much the distortion affects feedback (0.0 to 1.0)."""
        self.feedback_intensity = np.clip(intensity, 0.0, 1.0)
        
    def process_cross_feedback(self, left_sample: float, right_sample: float) -> tuple[float, float]:
        """
        Process cross-feedback signals with distortion.
        
        Args:
            left_sample: Left channel feedback sample
            right_sample: Right channel feedback sample
            
        Returns:
            Tuple of (distorted_left, distorted_right) samples
        """
        if not self.enabled:
            return left_sample, right_sample
            
        # Apply distortion to cross-feedback signals
        distorted_left = self.distortion.process_sample(left_sample)
        distorted_right = self.distortion.process_sample(right_sample)
        
        # Blend with original based on feedback intensity
        left_output = left_sample * (1.0 - self.feedback_intensity) + distorted_left * self.feedback_intensity
        right_output = right_sample * (1.0 - self.feedback_intensity) + distorted_right * self.feedback_intensity
        
        return left_output, right_output
        
    def get_info(self) -> str:
        """Get a human-readable description of current settings."""
        if not self.enabled:
            return "Cross-feedback Distortion: Disabled"
        return f"Cross-feedback Distortion: {self.distortion.get_info()}"
