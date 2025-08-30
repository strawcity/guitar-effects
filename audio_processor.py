#!/usr/bin/env python3
"""
Audio Processor for Guitar Effects System

Handles audio routing and processing for delay effects,
integrating them into a unified audio pipeline.
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Dict, Any


from delay import (BasicDelay, TapeDelay, MultiTapDelay, 
                   TempoSyncedDelay, StereoDelay)



class AudioProcessor:
    """Unified audio processor for guitar effects system."""
    
    def __init__(self, config, sample_rate: int = 44100):
        self.config = config
        self.sample_rate = sample_rate
        

        
        # Delay effects
        self.delay_effects = {
            "basic_delay": BasicDelay(sample_rate=sample_rate),
            "tape_delay": TapeDelay(sample_rate=sample_rate),
            "multi_delay": MultiTapDelay(sample_rate=sample_rate),
            "tempo_delay": TempoSyncedDelay(sample_rate=sample_rate),
            "stereo_delay": StereoDelay(sample_rate=sample_rate)
        }
        

        
        # Current effect state
        self.current_effect = "basic_delay"
        self.active_effects = set()
        
        # Audio state
        self.is_running = False
        
        # Audio buffer management
        self.input_buffer = np.array([])
        self.output_buffer = np.array([])
        self.buffer_size = 4096
        
        # Threading
        self.audio_thread = None
        self.lock = threading.Lock()
        
    def set_current_effect(self, effect_name: str):
        """Set the current effect to control."""
        if effect_name in self.delay_effects:
            self.current_effect = effect_name
            print(f"Current effect set to: {effect_name}")
        else:
            print(f"Unknown effect: {effect_name}")
            
    def start_effect(self, effect_name: str):
        """Start a specific effect."""
        if effect_name in self.delay_effects:
            self.active_effects.add(effect_name)
            print(f"{effect_name} started")
        else:
            print(f"Unknown effect: {effect_name}")
            
    def stop_effect(self, effect_name: str):
        """Stop a specific effect."""
        if effect_name in self.active_effects:
            self.active_effects.remove(effect_name)
            print(f"{effect_name} stopped")
        else:
            print(f"{effect_name} is not running")
            
    def get_effect_status(self, effect_name: str) -> Dict[str, Any]:
        """Get status of a specific effect."""
        if effect_name in self.delay_effects:
            effect = self.delay_effects[effect_name]
            status = effect.get_parameters()
            status["active"] = effect_name in self.active_effects
            return status
        else:
            return {"error": f"Unknown effect: {effect_name}"}
            

            
    def set_delay_parameter(self, effect_name: str, param: str, value):
        """Set delay effect parameter."""
        if effect_name in self.delay_effects:
            effect = self.delay_effects[effect_name]
            
            if param == "delay_time":
                effect.set_delay_time(value)
            elif param == "feedback":
                effect.set_feedback(value)
            elif param == "wet_mix":
                effect.set_wet_mix(value)
            elif param == "saturation" and hasattr(effect, 'set_tape_parameters'):
                effect.set_tape_parameters(saturation=value)
            elif param == "wow_rate" and hasattr(effect, 'set_tape_parameters'):
                effect.set_tape_parameters(wow_rate=value)
            elif param == "tempo" and hasattr(effect, 'set_tempo'):
                effect.set_tempo(value)
            elif param == "sync_tempo" and hasattr(effect, 'sync_taps_to_tempo'):
                effect.sync_taps_to_tempo(value)
            elif param == "left_delay" and hasattr(effect, 'set_left_delay'):
                effect.set_left_delay(value)
            elif param == "right_delay" and hasattr(effect, 'set_right_delay'):
                effect.set_right_delay(value)
            else:
                print(f"Unknown parameter '{param}' for {effect_name}")
                
    def process_audio(self, input_audio: np.ndarray) -> np.ndarray:
        """Process audio through active effects."""
        if len(input_audio) == 0:
            return input_audio
            
        output_audio = input_audio.copy()
        

                

            
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
                        
        return output_audio
        

                    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback for real-time processing."""
        try:
            with self.lock:
                # Get input audio
                input_audio = indata[:, 0] if indata.ndim > 1 else indata
                
                # Process audio through effects
                processed_audio = self.process_audio(input_audio)
                
                # Output processed audio
                if outdata.ndim > 1:
                    outdata[:, 0] = processed_audio[:frames]
                else:
                    outdata[:frames] = processed_audio[:frames]
                    
        except Exception as e:
            print(f"Audio callback error: {e}")
            outdata.fill(0)
            
    def start_audio(self, input_device=None, output_device=None):
        """Start audio processing."""
        if self.is_running:
            print("Audio already running")
            return
            
        try:
            self.is_running = True
            
            # Start audio stream
            with sd.Stream(
                channels=(1, 1),
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32,
                latency='high',
                callback=self.audio_callback,
                device=(input_device, output_device)
            ) as stream:
                print("Audio stream started successfully!")
                
                # Keep stream alive
                while self.is_running:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Audio error: {e}")
            self.is_running = False
            
    def stop_audio(self):
        """Stop audio processing."""
        self.is_running = False
        print("Audio stopped")
        
    def demo_mode(self):
        """Run demo mode with delay effects."""
        print("Demo mode: Testing delay effects")
            
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
        return {
            "current_effect": self.current_effect,
            "active_effects": list(self.active_effects),
            "audio_running": self.is_running
        }
        

