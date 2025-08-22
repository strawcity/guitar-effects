#!/usr/bin/env python3
"""
Guitar Synth Effect Controller

Controller class for the guitar synth effect that integrates with the interactive CLI system.
"""

from typing import Dict, Any
from .guitar_synth import GuitarSynth
from effect_controller import EffectController


class GuitarSynthController(EffectController):
    """Controller for the guitar synth effect."""
    
    def __init__(self, audio_processor):
        super().__init__("guitar_synth", audio_processor)
        self.guitar_synth = GuitarSynth()
        
    def set_ring_frequency(self, freq: float):
        """Set ring modulation frequency in Hz."""
        self.audio_processor.set_guitar_synth_parameter("ring_frequency", freq)
        print(f"Ring frequency set to {freq} Hz")
        
    def set_bit_depth(self, depth: int):
        """Set bit depth for bit crushing (1-16)."""
        self.audio_processor.set_guitar_synth_parameter("bit_depth", depth)
        print(f"Bit depth set to {depth} bits")
        
    def set_sample_rate_reduction(self, factor: float):
        """Set sample rate reduction factor (0.1-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("sample_rate_reduction", factor)
        print(f"Sample rate reduction set to {factor:.2f}")
        
    def set_wave_shape_amount(self, amount: float):
        """Set wave shaping intensity (0.0-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("wave_shape_amount", amount)
        print(f"Wave shaping amount set to {amount:.2f}")
        
    def set_filter_cutoff(self, cutoff: float):
        """Set low-pass filter cutoff frequency in Hz."""
        self.audio_processor.set_guitar_synth_parameter("filter_cutoff", cutoff)
        print(f"Filter cutoff set to {cutoff} Hz")
        
    def set_filter_resonance(self, resonance: float):
        """Set filter resonance (0.0-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("filter_resonance", resonance)
        print(f"Filter resonance set to {resonance:.2f}")
        
    def set_envelope_sensitivity(self, sensitivity: float):
        """Set envelope follower sensitivity (0.0-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("envelope_sensitivity", sensitivity)
        print(f"Envelope sensitivity set to {sensitivity:.2f}")
        
    def set_wet_mix(self, wet_mix: float):
        """Set wet signal mix (0.0-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("wet_mix", wet_mix)
        print(f"Wet mix set to {wet_mix:.2f}")
        
    def set_lfo_frequency(self, freq: float):
        """Set LFO frequency in Hz."""
        self.audio_processor.set_guitar_synth_parameter("lfo_frequency", freq)
        print(f"LFO frequency set to {freq} Hz")
        
    def set_lfo_depth(self, depth: float):
        """Set LFO depth (0.0-1.0)."""
        self.audio_processor.set_guitar_synth_parameter("lfo_depth", depth)
        print(f"LFO depth set to {depth:.2f}")
        
    def set_preset(self, preset_name: str):
        """Set effect to a predefined preset."""
        presets = {
            "robotic": {
                "ring_frequency": 200.0,
                "bit_depth": 4,
                "sample_rate_reduction": 0.3,
                "wave_shape_amount": 0.8,
                "filter_cutoff": 1500.0,
                "filter_resonance": 0.7,
                "envelope_sensitivity": 0.6,
                "wet_mix": 0.8,
                "lfo_frequency": 3.0,
                "lfo_depth": 0.3
            },
            "warm": {
                "ring_frequency": 50.0,
                "bit_depth": 12,
                "sample_rate_reduction": 0.8,
                "wave_shape_amount": 0.3,
                "filter_cutoff": 800.0,
                "filter_resonance": 0.2,
                "envelope_sensitivity": 0.4,
                "wet_mix": 0.6,
                "lfo_frequency": 1.5,
                "lfo_depth": 0.1
            },
            "digital": {
                "ring_frequency": 0.0,
                "bit_depth": 6,
                "sample_rate_reduction": 0.4,
                "wave_shape_amount": 0.9,
                "filter_cutoff": 3000.0,
                "filter_resonance": 0.5,
                "envelope_sensitivity": 0.8,
                "wet_mix": 0.9,
                "lfo_frequency": 5.0,
                "lfo_depth": 0.4
            },
            "metallic": {
                "ring_frequency": 150.0,
                "bit_depth": 8,
                "sample_rate_reduction": 0.6,
                "wave_shape_amount": 0.6,
                "filter_cutoff": 2500.0,
                "filter_resonance": 0.6,
                "envelope_sensitivity": 0.5,
                "wet_mix": 0.7,
                "lfo_frequency": 2.0,
                "lfo_depth": 0.2
            }
        }
        
        if preset_name in presets:
            for param, value in presets[preset_name].items():
                self.audio_processor.set_guitar_synth_parameter(param, value)
            print(f"Preset '{preset_name}' applied")
        else:
            print(f"Unknown preset: {preset_name}")
            print("Available presets:", ", ".join(presets.keys()))
            
    def list_presets(self):
        """List available presets."""
        presets = ["robotic", "warm", "digital", "metallic"]
        print("Available presets:", ", ".join(presets))
        
    def get_status(self) -> Dict[str, Any]:
        """Get effect status."""
        base_status = super().get_status()
        synth_status = self.audio_processor.get_guitar_synth_parameters()
        base_status.update(synth_status)
        return base_status
        
    def get_help(self) -> str:
        """Get guitar synth help."""
        return """
Guitar Synth Commands:
  start                      Start the guitar synth effect
  stop                       Stop the guitar synth effect
  status                     Show current status
  
  ring_freq <hz>             Set ring modulation frequency (20-2000 Hz)
  bit_depth <bits>           Set bit depth for crushing (1-16 bits)
  sample_rate <factor>       Set sample rate reduction (0.1-1.0)
  wave_shape <amount>        Set wave shaping intensity (0.0-1.0)
  filter_cutoff <hz>         Set filter cutoff frequency (20-20000 Hz)
  filter_resonance <amount>  Set filter resonance (0.0-1.0)
  envelope <sensitivity>     Set envelope sensitivity (0.0-1.0)
  wet_mix <amount>           Set wet/dry mix (0.0-1.0)
  lfo_freq <hz>              Set LFO frequency (0.1-20 Hz)
  lfo_depth <amount>         Set LFO depth (0.0-1.0)
  
  preset <name>               Apply preset (type 'presets' to list)
  presets                     List available presets
  
  reset                      Reset all parameters to defaults
        """.strip()
        
    def reset(self):
        """Reset effect to default parameters."""
        # Reset to default values
        defaults = {
            "ring_frequency": 100.0,
            "bit_depth": 8,
            "sample_rate_reduction": 1.0,
            "wave_shape_amount": 0.5,
            "filter_cutoff": 2000.0,
            "filter_resonance": 0.3,
            "envelope_sensitivity": 0.5,
            "wet_mix": 0.7,
            "lfo_frequency": 2.0,
            "lfo_depth": 0.1
        }
        for param, value in defaults.items():
            self.audio_processor.set_guitar_synth_parameter(param, value)
        print("Guitar synth reset to defaults")
