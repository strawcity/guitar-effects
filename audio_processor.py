#!/usr/bin/env python3
"""
Audio Processor for Guitar Stereo Delay Effects System

Handles audio routing and processing for stereo delay effects,
integrating them into a unified audio pipeline.
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Dict, Any

from delay import StereoDelay

class AudioProcessor:
    """Unified audio processor for guitar stereo delay effects system."""
    
    def __init__(self, config, sample_rate: int = 44100):
        self.config = config
        self.sample_rate = sample_rate
        
        # Stereo delay effect
        self.stereo_delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=0.3,
            right_delay=0.6,
            feedback=0.3,
            wet_mix=0.6,
            ping_pong=True,
            stereo_width=0.5,
            cross_feedback=0.2
        )
        
        # Audio state
        self.is_running = False
        
        # Audio buffer management
        self.input_buffer = np.array([])
        self.output_buffer = np.array([])
        self.buffer_size = 4096
        
        # Threading
        self.audio_thread = None
        self.lock = threading.Lock()
        
    def set_stereo_delay_parameter(self, param: str, value):
        """Set stereo delay effect parameter."""
        if param == "left_delay":
            self.stereo_delay.set_left_delay(value)
        elif param == "right_delay":
            self.stereo_delay.set_right_delay(value)
        elif param == "feedback":
            self.stereo_delay.set_parameters(feedback=value)
        elif param == "wet_mix":
            self.stereo_delay.set_parameters(wet_mix=value)
        elif param == "ping_pong":
            self.stereo_delay.set_stereo_parameters(ping_pong=value)
        elif param == "stereo_width":
            self.stereo_delay.set_stereo_parameters(stereo_width=value)
        elif param == "cross_feedback":
            self.stereo_delay.set_stereo_parameters(cross_feedback=value)
        else:
            print(f"Unknown parameter '{param}' for stereo delay")
                
    def process_audio(self, input_audio: np.ndarray) -> np.ndarray:
        """Process audio through stereo delay effect."""
        if len(input_audio) == 0:
            return input_audio
            
        # Process through stereo delay effect
        left_output, right_output = self.stereo_delay.process_mono_to_stereo(input_audio)
        
        # Convert back to mono for now (mix L+R)
        output_audio = (left_output + right_output) * 0.5
                        
        return output_audio
        
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback for real-time processing."""
        try:
            with self.lock:
                # Get input audio
                input_audio = indata[:, 0] if indata.ndim > 1 else indata
                
                # Process audio through stereo delay effect
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
        
    def test_audio(self):
        """Test audio system with a simple tone."""
        # Generate test tone
        duration = 1.0  # 1 second
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)
        test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440Hz A note
        
        # Process through stereo delay effect
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
            "stereo_delay_active": True,
            "audio_running": self.is_running,
            "stereo_delay_info": self.stereo_delay.get_info()
        }
        

