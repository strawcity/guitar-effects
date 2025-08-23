#!/usr/bin/env python3
"""
Optimized Audio Processor for Guitar Effects System

Fixes latency issues and provides proper audio passthrough when no effects are active.
Optimized for Raspberry Pi performance with minimal buffer sizes and low-latency settings.
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

from arpeggiator import ArpeggioEngine, SynthEngine, WorkingArpeggiatorSystem
from delay import (BasicDelay, TapeDelay, MultiTapDelay, 
                   TempoSyncedDelay, StereoDelay)
from guitar_synth import GuitarSynth


class OptimizedAudioProcessor:
    """Optimized audio processor with low latency and proper passthrough."""
    
    def __init__(self, config, sample_rate: int = None):
        if sample_rate is None:
            sample_rate = config.sample_rate
        self.config = config
        self.sample_rate = sample_rate
        
        # Core engines
        self.arpeggio_engine = ArpeggioEngine(config)
        self.synth_engine = SynthEngine(config)
        
        # Delay effects
        self.delay_effects = {
            "basic_delay": BasicDelay(sample_rate=sample_rate),
            "tape_delay": TapeDelay(sample_rate=sample_rate),
            "multi_delay": MultiTapDelay(sample_rate=sample_rate),
            "tempo_delay": TempoSyncedDelay(sample_rate=sample_rate),
            "stereo_delay": StereoDelay(sample_rate=sample_rate)
        }
        
        # Guitar synth effect
        self.guitar_synth = GuitarSynth(sample_rate=sample_rate)
        
        # Working arpeggiator system
        self.working_arpeggiator = WorkingArpeggiatorSystem(config, sample_rate)
        
        # Current effect state
        self.current_effect = "arpeggiator"
        self.active_effects = set()
        
        # Audio state
        self.is_running = False
        self.current_chord = None
        self.current_arpeggio = None
        self.arpeggio_audio = None
        self.arpeggio_position = 0
        self.arpeggio_length = 0
        self.arpeggio_start_time = 0
        
        # Settings
        self.tempo = 100
        self.pattern = config.default_pattern
        self.synth_type = config.default_synth
        self.duration = 2.4
        
        # OPTIMIZED: Platform-specific buffer sizes
        if config.is_pi:
            self.buffer_size = 1024  # Balanced buffer for Pi stability (~21ms latency)
            self.latency_setting = 'high'
        else:
            self.buffer_size = 256  # Smaller buffer for other systems (~5.8ms latency)
            self.latency_setting = 'low'
        
        # Threading
        self.audio_thread = None
        self.lock = threading.Lock()
        
        # Performance monitoring
        self.processing_times = []
        self.max_processing_time = 0.01  # 10ms max processing time
        
        print(f"🎵 Optimized Audio Processor initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🔧 Buffer size: {self.buffer_size} samples ({self.buffer_size/self.sample_rate*1000:.1f}ms latency)")
        
    def set_current_effect(self, effect_name: str):
        """Set the current effect to control."""
        if effect_name in self.delay_effects or effect_name == "arpeggiator" or effect_name == "guitar_synth":
            self.current_effect = effect_name
            print(f"Current effect set to: {effect_name}")
        else:
            print(f"Unknown effect: {effect_name}")
            
    def start_effect(self, effect_name: str):
        """Start a specific effect."""
        if effect_name == "arpeggiator":
            # Start the working arpeggiator system
            self.working_arpeggiator.start_arpeggiator()
            self.active_effects.add("arpeggiator")
            print("🎸 Working arpeggiator started with enhanced chord detection!")
        elif effect_name in self.delay_effects:
            self.active_effects.add(effect_name)
            print(f"{effect_name} started")
        elif effect_name == "guitar_synth":
            self.active_effects.add("guitar_synth")
            print("Guitar synth started")
        else:
            print(f"Unknown effect: {effect_name}")
            
    def stop_effect(self, effect_name: str):
        """Stop a specific effect."""
        if effect_name in self.active_effects:
            if effect_name == "arpeggiator":
                # Stop the working arpeggiator system
                self.working_arpeggiator.stop_arpeggiator()
            self.active_effects.remove(effect_name)
            print(f"{effect_name} stopped")
        else:
            print(f"{effect_name} is not active")
            
    def set_arpeggiator_parameter(self, param_name: str, value):
        """Set an arpeggiator parameter."""
        if param_name == "tempo":
            self.tempo = max(60, min(200, value))
            self.working_arpeggiator.set_tempo(value)
            print(f"Tempo set to {self.tempo} BPM")
        elif param_name == "pattern":
            self.pattern = value
            self.working_arpeggiator.set_pattern(value)
            print(f"Pattern set to {value}")
        elif param_name == "synth":
            self.synth_type = value
            self.working_arpeggiator.set_synth(value)
            print(f"Synth type set to {value}")
        elif param_name == "duration":
            self.duration = max(0.5, min(10.0, value))
            self.working_arpeggiator.set_duration(value)
            print(f"Duration set to {self.duration} seconds")
        else:
            print(f"Unknown arpeggiator parameter: {param_name}")
            
    def set_delay_parameter(self, effect_name: str, param_name: str, value):
        """Set a delay effect parameter."""
        if effect_name not in self.delay_effects:
            print(f"Unknown delay effect: {effect_name}")
            return
            
        effect = self.delay_effects[effect_name]
        
        if param_name == "delay_time":
            if hasattr(effect, 'set_delay_time'):
                effect.set_delay_time(value)
                print(f"{effect_name} delay time set to {value}s")
            else:
                print(f"{effect_name} doesn't support delay time setting")
        elif param_name == "feedback":
            if hasattr(effect, 'set_feedback'):
                effect.set_feedback(value)
                print(f"{effect_name} feedback set to {value}")
            else:
                print(f"{effect_name} doesn't support feedback setting")
        elif param_name == "wet_mix":
            if hasattr(effect, 'set_wet_mix'):
                effect.set_wet_mix(value)
                print(f"{effect_name} wet mix set to {value}")
            else:
                print(f"{effect_name} doesn't support wet mix setting")
        elif param_name == "sync_tempo":
            if hasattr(effect, 'sync_taps_to_tempo'):
                effect.sync_taps_to_tempo(value)
                print(f"{effect_name} synced to {value} BPM")
            else:
                print(f"{effect_name} doesn't support tempo sync")
        elif param_name == "left_delay" and hasattr(effect, 'set_left_delay'):
            effect.set_left_delay(value)
            print(f"{effect_name} left delay set to {value}s")
        elif param_name == "right_delay" and hasattr(effect, 'set_right_delay'):
            effect.set_right_delay(value)
            print(f"{effect_name} right delay set to {value}s")
        else:
            print(f"Unknown parameter '{param_name}' for {effect_name}")
                
    def process_audio(self, input_audio: np.ndarray) -> np.ndarray:
        """Process audio through active effects with performance monitoring."""
        if len(input_audio) == 0:
            return input_audio
            
        start_time = time.time()
        
        # OPTIMIZED: Check if any effects are active first
        if not self.active_effects:
            # No effects active - return input directly (passthrough)
            return input_audio
            
        output_audio = input_audio.copy()
        
        # Process through arpeggiator if active
        if "arpeggiator" in self.active_effects and self.current_arpeggio:
            # Generate arpeggio audio
            arpeggio_audio = self.synth_engine.render_arpeggio(
                self.current_arpeggio, self.synth_type
            )
            
            if len(arpeggio_audio) > 0:
                # Mix arpeggio with input
                arpeggio_gain = 0.7
                min_length = min(len(output_audio), len(arpeggio_audio))
                output_audio[:min_length] = np.clip(
                    output_audio[:min_length] + arpeggio_audio[:min_length] * arpeggio_gain,
                    -1.0, 1.0
                )
                
        # Process through guitar synth if active
        if "guitar_synth" in self.active_effects:
            output_audio = self.guitar_synth.process_audio(output_audio)
            
        # Process through active delay effects
        for effect_name in self.active_effects:
            if effect_name in self.delay_effects:
                effect = self.delay_effects[effect_name]
                
                # Process through delay effect
                if hasattr(effect, 'process_buffer'):
                    if hasattr(effect, 'process_mono_to_stereo'):
                        # Stereo delay
                        left_output, right_output = effect.process_mono_to_stereo(output_audio)
                        # Convert back to mono for now (mix L+R)
                        output_audio = (left_output + right_output) * 0.5
                    elif hasattr(effect, 'stereo_output') and effect.stereo_output:
                        # Multi-tap delay returns stereo output
                        left_output, right_output = effect.process_buffer(output_audio)
                        # Convert back to mono for now (mix L+R)
                        output_audio = (left_output + right_output) * 0.5
                    else:
                        # Mono delay
                        output_audio = effect.process_buffer(output_audio)
        
        # Performance monitoring
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        
        # Keep only last 100 measurements
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)
            
        # Warn if processing is too slow
        if processing_time > self.max_processing_time:
            print(f"⚠️  Slow audio processing: {processing_time*1000:.1f}ms")
                        
        return output_audio
        
    def update_chord(self, chord_data: Dict[str, Any]):
        """Update current chord and generate arpeggio if valid."""
        self.current_chord = chord_data
        
        if chord_data and chord_data.get('valid', False):
            # Generate new arpeggio
            self.current_arpeggio = self.arpeggio_engine.generate_arpeggio(
                chord_data, self.pattern, self.tempo, self.duration
            )
            
            # Store arpeggio audio for processing
            if self.current_arpeggio and self.current_arpeggio.get('notes'):
                arpeggio_audio = self.synth_engine.render_arpeggio(
                    self.current_arpeggio, self.synth_type
                )
                
                if len(arpeggio_audio) > 0:
                    self.arpeggio_audio = arpeggio_audio
                    self.arpeggio_position = 0
                    self.arpeggio_length = len(arpeggio_audio)
                    self.arpeggio_start_time = time.time()
                    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Optimized audio callback for real-time processing."""
        try:
            # OPTIMIZED: Minimize lock time
            input_audio = indata[:, 0] if indata.ndim > 1 else indata
            
            # Quick check if effects are active
            if not self.active_effects:
                # Passthrough mode - no processing needed
                if outdata.ndim > 1:
                    outdata[:, 0] = input_audio[:frames]
                else:
                    outdata[:frames] = input_audio[:frames]
                return
            
            # Effects are active - process audio
            with self.lock:
                processed_audio = self.process_audio(input_audio)
                
                # Output processed audio
                if outdata.ndim > 1:
                    outdata[:, 0] = processed_audio[:frames]
                else:
                    outdata[:frames] = processed_audio[:frames]
                    
        except Exception as e:
            print(f"Audio callback error: {e}")
            # On error, output silence instead of crashing
            outdata.fill(0)
            
    def start_audio(self, input_device=None, output_device=None):
        """Start audio processing with optimized settings."""
        if self.is_running:
            print("Audio already running")
            return
            
        try:
            self.is_running = True
            
            # OPTIMIZED: Platform-specific latency settings
            with sd.Stream(
                channels=(1, 1),
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32,
                latency=self.latency_setting,
                callback=self.audio_callback,
                device=(input_device, output_device)
            ) as stream:
                print("🎵 Optimized audio stream started successfully!")
                print(f"📊 Latency: {self.buffer_size/self.sample_rate*1000:.1f}ms")
                print(f"🔧 Buffer size: {self.buffer_size} samples")
                
                # Keep stream alive with minimal sleep
                while self.is_running:
                    time.sleep(0.01)  # Reduced from 0.1 to 0.01
                    
        except Exception as e:
            print(f"❌ Audio error: {e}")
            self.is_running = False
            
    def stop_audio(self):
        """Stop audio processing."""
        self.is_running = False
        print("Audio stopped")
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get audio processing performance statistics."""
        if not self.processing_times:
            return {"status": "No data available"}
            
        avg_time = np.mean(self.processing_times)
        max_time = np.max(self.processing_times)
        min_time = np.min(self.processing_times)
        
        return {
            "average_processing_time_ms": avg_time * 1000,
            "max_processing_time_ms": max_time * 1000,
            "min_processing_time_ms": min_time * 1000,
            "buffer_latency_ms": self.buffer_size / self.sample_rate * 1000,
            "total_latency_ms": (self.buffer_size / self.sample_rate + avg_time) * 1000,
            "samples_processed": len(self.processing_times)
        }
        
    def demo_mode(self):
        """Run demo mode with C major chord."""
        if "arpeggiator" in self.active_effects:
            # Use the working arpeggiator demo mode
            self.working_arpeggiator.demo_mode()
        else:
            print("Arpeggiator must be active for demo mode")
            
    def test_audio(self):
        """Test audio system with a simple tone."""
        # Generate test tone
        duration = 1.0  # 1 second
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)
        test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440Hz A note
        
        # Process through active effects
        processed_tone = self.process_audio(test_tone)
        
        # Play test tone
        try:
            sd.play(processed_tone, self.sample_rate)
            sd.wait()
            print("Audio test completed")
        except Exception as e:
            print(f"Audio test error: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        status = {
            "current_effect": self.current_effect,
            "active_effects": list(self.active_effects),
            "tempo": self.tempo,
            "pattern": self.pattern,
            "synth": self.synth_type,
            "duration": self.duration,
            "audio_running": self.is_running,
            "current_chord": self.current_chord,
            "buffer_size": self.buffer_size,
            "latency_ms": self.buffer_size / self.sample_rate * 1000
        }
        
        # Add working arpeggiator status if it's active
        if "arpeggiator" in self.active_effects:
            arpeggiator_status = self.working_arpeggiator.get_status()
            status.update({
                "arpeggiator_running": arpeggiator_status.get("running", False),
                "arpeggiator_chord": arpeggiator_status.get("current_chord"),
                "arpeggiator_tempo": arpeggiator_status.get("tempo"),
                "arpeggiator_pattern": arpeggiator_status.get("pattern"),
                "arpeggiator_synth": arpeggiator_status.get("synth")
            })
        
        return status
        
    def set_guitar_synth_parameter(self, param_name: str, value):
        """Set a guitar synth parameter."""
        if hasattr(self.guitar_synth, f"set_{param_name}"):
            getattr(self.guitar_synth, f"set_{param_name}")(value)
        elif hasattr(self.guitar_synth, param_name):
            setattr(self.guitar_synth, param_name, value)
        else:
            print(f"Unknown guitar synth parameter: {param_name}")
            
    def get_guitar_synth_parameters(self) -> Dict[str, Any]:
        """Get all guitar synth parameters."""
        return self.guitar_synth.get_parameters()


def main():
    """Test the optimized audio processor."""
    from config import Config
    
    config = Config()
    processor = OptimizedAudioProcessor(config)
    
    print("🎵 Optimized Audio Processor ready!")
    print("💡 Features:")
    print("   • Low latency (5.8ms buffer)")
    print("   • Audio passthrough when no effects active")
    print("   • Performance monitoring")
    print("   • Optimized for Raspberry Pi")

if __name__ == "__main__":
    main()
