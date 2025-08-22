#!/usr/bin/env python3
"""
Guitar Synth Effect

Transforms guitar input into synthesizer-like sounds using various synthesis techniques
including ring modulation, bit crushing, wave shaping, and filtering.
"""

import numpy as np
from typing import Optional, Dict, Any


class GuitarSynth:
    """
    Guitar synthesizer effect that transforms guitar input into synth-like sounds.
    
    Features:
    - Ring modulation for metallic/robotic sounds
    - Bit crushing for lo-fi digital effects
    - Wave shaping for harmonic distortion
    - Low-pass filtering for warmth
    - Envelope following for dynamic response
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 ring_freq: float = 100.0,
                 bit_depth: int = 8,
                 sample_rate_reduction: float = 1.0,
                 wave_shape_amount: float = 0.5,
                 filter_cutoff: float = 2000.0,
                 filter_resonance: float = 0.3,
                 envelope_sensitivity: float = 0.5,
                 wet_mix: float = 0.7):
        """
        Initialize the guitar synth effect.
        
        Args:
            sample_rate: Audio sample rate in Hz
            ring_freq: Ring modulation frequency in Hz
            bit_depth: Bit depth for bit crushing (1-16)
            sample_rate_reduction: Sample rate reduction factor (0.1-1.0)
            wave_shape_amount: Wave shaping intensity (0.0-1.0)
            filter_cutoff: Low-pass filter cutoff frequency in Hz
            filter_resonance: Filter resonance (0.0-1.0)
            envelope_sensitivity: Envelope follower sensitivity (0.0-1.0)
            wet_mix: Wet signal mix (0.0-1.0)
        """
        self.sample_rate = sample_rate
        self.ring_freq = np.clip(ring_freq, 20.0, 2000.0)
        self.bit_depth = np.clip(bit_depth, 1, 16)
        self.sample_rate_reduction = np.clip(sample_rate_reduction, 0.1, 1.0)
        self.wave_shape_amount = np.clip(wave_shape_amount, 0.0, 1.0)
        self.filter_cutoff = np.clip(filter_cutoff, 20.0, 20000.0)
        self.filter_resonance = np.clip(filter_resonance, 0.0, 1.0)
        self.envelope_sensitivity = np.clip(envelope_sensitivity, 0.0, 1.0)
        self.wet_mix = np.clip(wet_mix, 0.0, 1.0)
        self.dry_mix = 1.0 - self.wet_mix
        
        # Internal state
        self.ring_phase = 0.0
        self.filter_state = np.zeros(4)  # 2-pole filter state
        self.envelope = 0.0
        self.envelope_decay = 0.99
        
        # Modulation parameters
        self.lfo_freq = 2.0  # Hz
        self.lfo_phase = 0.0
        self.lfo_depth = 0.1
        
        # Ring modulation oscillator
        self.ring_oscillator = 0.0
        
        # Bit crushing state
        self.bit_accumulator = 0.0
        self.bit_counter = 0
        
        # Sample rate reduction state
        self.sr_accumulator = 0.0
        self.sr_counter = 0
        self.sr_hold_sample = 0.0
        
    def set_ring_frequency(self, freq: float):
        """Set ring modulation frequency in Hz."""
        self.ring_freq = np.clip(freq, 20.0, 2000.0)
        
    def set_bit_depth(self, depth: int):
        """Set bit depth for bit crushing (1-16)."""
        self.bit_depth = np.clip(depth, 1, 16)
        
    def set_sample_rate_reduction(self, factor: float):
        """Set sample rate reduction factor (0.1-1.0)."""
        self.sample_rate_reduction = np.clip(factor, 0.1, 1.0)
        
    def set_wave_shape_amount(self, amount: float):
        """Set wave shaping intensity (0.0-1.0)."""
        self.wave_shape_amount = np.clip(amount, 0.0, 1.0)
        
    def set_filter_cutoff(self, cutoff: float):
        """Set low-pass filter cutoff frequency in Hz."""
        self.filter_cutoff = np.clip(cutoff, 20.0, 20000.0)
        
    def set_filter_resonance(self, resonance: float):
        """Set filter resonance (0.0-1.0)."""
        self.filter_resonance = np.clip(resonance, 0.0, 1.0)
        
    def set_envelope_sensitivity(self, sensitivity: float):
        """Set envelope follower sensitivity (0.0-1.0)."""
        self.envelope_sensitivity = np.clip(sensitivity, 0.0, 1.0)
        
    def set_wet_mix(self, wet_mix: float):
        """Set wet signal mix (0.0-1.0)."""
        self.wet_mix = np.clip(wet_mix, 0.0, 1.0)
        self.dry_mix = 1.0 - self.wet_mix
        
    def set_lfo_frequency(self, freq: float):
        """Set LFO frequency in Hz."""
        self.lfo_freq = np.clip(freq, 0.1, 20.0)
        
    def set_lfo_depth(self, depth: float):
        """Set LFO depth (0.0-1.0)."""
        self.lfo_depth = np.clip(depth, 0.0, 1.0)
        
    def _update_ring_oscillator(self):
        """Update ring modulation oscillator."""
        self.ring_phase += 2 * np.pi * self.ring_freq / self.sample_rate
        if self.ring_phase >= 2 * np.pi:
            self.ring_phase -= 2 * np.pi
        self.ring_oscillator = np.sin(self.ring_phase)
        
    def _update_lfo(self):
        """Update LFO for modulation."""
        self.lfo_phase += 2 * np.pi * self.lfo_freq / self.sample_rate
        if self.lfo_phase >= 2 * np.pi:
            self.lfo_phase -= 2 * np.pi
            
    def _apply_ring_modulation(self, audio: np.ndarray) -> np.ndarray:
        """Apply ring modulation to the audio."""
        modulated = np.zeros_like(audio)
        for i in range(len(audio)):
            self._update_ring_oscillator()
            modulated[i] = audio[i] * self.ring_oscillator
        return modulated
        
    def _apply_bit_crushing(self, audio: np.ndarray) -> np.ndarray:
        """Apply bit crushing effect."""
        if self.bit_depth >= 16:
            return audio
            
        # Calculate quantization step
        max_val = np.max(np.abs(audio)) if len(audio) > 0 else 1.0
        if max_val == 0:
            max_val = 1.0
            
        # Quantize to bit depth
        quantized = np.round(audio / max_val * (2**(self.bit_depth - 1) - 1))
        quantized = quantized / (2**(self.bit_depth - 1) - 1) * max_val
        
        return quantized
        
    def _apply_sample_rate_reduction(self, audio: np.ndarray) -> np.ndarray:
        """Apply sample rate reduction effect."""
        if self.sample_rate_reduction >= 1.0:
            return audio
            
        reduced = np.zeros_like(audio)
        step = int(1.0 / self.sample_rate_reduction)
        
        for i in range(len(audio)):
            if i % step == 0:
                self.sr_hold_sample = audio[i]
            reduced[i] = self.sr_hold_sample
            
        return reduced
        
    def _apply_wave_shaping(self, audio: np.ndarray) -> np.ndarray:
        """Apply wave shaping distortion."""
        if self.wave_shape_amount <= 0.0:
            return audio
            
        # Soft clipping with adjustable curve
        shaped = np.tanh(audio * (1.0 + self.wave_shape_amount * 3.0))
        return shaped
        
    def _apply_low_pass_filter(self, audio: np.ndarray) -> np.ndarray:
        """Apply 2-pole low-pass filter."""
        filtered = np.zeros_like(audio)
        
        # Calculate filter coefficients
        freq = self.filter_cutoff / self.sample_rate
        q = 1.0 / (2.0 * self.filter_resonance + 0.5)
        
        # Normalize frequency
        w0 = 2 * np.pi * freq
        alpha = np.sin(w0) / (2 * q)
        
        # Calculate coefficients
        b0 = (1 - np.cos(w0)) / 2
        b1 = 1 - np.cos(w0)
        b2 = (1 - np.cos(w0)) / 2
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        
        # Normalize
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0
        
        # Apply filter
        for i in range(len(audio)):
            filtered[i] = (b0 * audio[i] + b1 * (audio[i-1] if i > 0 else 0) + b2 * (audio[i-2] if i > 1 else 0) 
                          - a1 * (filtered[i-1] if i > 0 else 0) - a2 * (filtered[i-2] if i > 1 else 0))
            
        return filtered
        
    def _update_envelope(self, audio: np.ndarray):
        """Update envelope follower."""
        if len(audio) == 0:
            return
            
        # Calculate RMS of current audio block
        rms = np.sqrt(np.mean(audio**2))
        
        # Update envelope with attack/release
        if rms > self.envelope:
            # Attack phase
            self.envelope = rms
        else:
            # Release phase
            self.envelope *= self.envelope_decay
            
    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio through the guitar synth effect.
        
        Args:
            audio: Input audio array
            
        Returns:
            Processed audio array
        """
        if len(audio) == 0:
            return audio
            
        # Update envelope follower
        self._update_envelope(audio)
        
        # Apply effects chain
        processed = audio.copy()
        
        # 1. Ring modulation
        if self.ring_freq > 0:
            processed = self._apply_ring_modulation(processed)
            
        # 2. Bit crushing
        if self.bit_depth < 16:
            processed = self._apply_bit_crushing(processed)
            
        # 3. Sample rate reduction
        if self.sample_rate_reduction < 1.0:
            processed = self._apply_sample_rate_reduction(processed)
            
        # 4. Wave shaping
        if self.wave_shape_amount > 0.0:
            processed = self._apply_wave_shaping(processed)
            
        # 5. Low-pass filter
        if self.filter_cutoff < 20000.0:
            processed = self._apply_low_pass_filter(processed)
            
        # 6. Envelope modulation
        if self.envelope_sensitivity > 0.0:
            envelope_mod = 1.0 + self.envelope * self.envelope_sensitivity
            processed *= envelope_mod
            
        # 7. LFO modulation
        if self.lfo_depth > 0.0:
            self._update_lfo()
            lfo_mod = 1.0 + self.lfo_depth * np.sin(self.lfo_phase)
            processed *= lfo_mod
            
        # Mix wet and dry signals
        output = self.dry_mix * audio + self.wet_mix * processed
        
        # Ensure output is within valid range
        output = np.clip(output, -1.0, 1.0)
        
        return output
        
    def get_parameters(self) -> Dict[str, Any]:
        """Get current effect parameters."""
        return {
            "ring_frequency": self.ring_freq,
            "bit_depth": self.bit_depth,
            "sample_rate_reduction": self.sample_rate_reduction,
            "wave_shape_amount": self.wave_shape_amount,
            "filter_cutoff": self.filter_cutoff,
            "filter_resonance": self.filter_resonance,
            "envelope_sensitivity": self.envelope_sensitivity,
            "wet_mix": self.wet_mix,
            "lfo_frequency": self.lfo_freq,
            "lfo_depth": self.lfo_depth
        }
        
    def set_parameters(self, **kwargs):
        """Set multiple parameters at once."""
        for param, value in kwargs.items():
            if hasattr(self, f"set_{param}"):
                getattr(self, f"set_{param}")(value)
            elif hasattr(self, param):
                setattr(self, param, value)
                
    def reset(self):
        """Reset internal state."""
        self.ring_phase = 0.0
        self.filter_state = np.zeros(4)
        self.envelope = 0.0
        self.lfo_phase = 0.0
        self.bit_accumulator = 0.0
        self.bit_counter = 0
        self.sr_accumulator = 0.0
        self.sr_counter = 0
        self.sr_hold_sample = 0.0
