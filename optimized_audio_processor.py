#!/usr/bin/env python3
"""
Optimized Audio Processor for Guitar Stereo Delay Effects System

A high-performance audio processor optimized for real-time stereo delay effects
with minimal latency and maximum stability.
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Dict, Any

from config import Config
from delay import StereoDelay

class OptimizedAudioProcessor:
    """High-performance audio processor for stereo delay effects."""
    
    def __init__(self, config: Config, sample_rate: int = 48000):
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
        self.audio_thread = None
        
        # Optimized buffer settings
        self.buffer_size = self._get_optimal_buffer_size()
        self.latency_setting = 'low' if config.is_pi else 'high'
        
        # Performance monitoring
        self.underrun_count = 0
        self.overflow_count = 0
        self.processing_times = []
        
        print(f"🎛️ Optimized Audio Processor initialized")
        print(f"📊 Buffer size: {self.buffer_size} samples")
        print(f"⚡ Latency: {self.buffer_size/self.sample_rate*1000:.1f}ms")
    
    def _get_optimal_buffer_size(self) -> int:
        """Get optimal buffer size based on platform."""
        if self.config.is_pi:
            return 512  # Smaller for Pi performance
        else:
            return 256  # Larger for desktop stability
    
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
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Optimized audio callback for real-time processing."""
        start_time = time.time()
        
        # Handle audio status
        if status.input_underflow:
            self.underrun_count += 1
        if status.input_overflow:
            self.overflow_count += 1
        if status.output_underflow:
            self.underrun_count += 1
        
        try:
            # Get input audio
            input_audio = indata[:, 0] if indata.ndim > 1 else indata
            
            # Process through stereo delay effect
            left_out, right_out = self.stereo_delay.process_mono_to_stereo(input_audio)
            
            # Output stereo audio
            if outdata.ndim > 1:
                outdata[:, 0] = left_out[:frames]
                outdata[:, 1] = right_out[:frames]
            else:
                # Mono output - mix L+R
                outdata[:frames] = (left_out[:frames] + right_out[:frames]) * 0.5
                
        except Exception as e:
            print(f"Audio callback error: {e}")
            outdata.fill(0)
        
        # Track processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        self.processing_times.append(processing_time)
        
        # Keep only last 100 measurements
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)
    
    def start_audio(self, input_device=None, output_device=None):
        """Start optimized audio processing."""
        if self.is_running:
            print("Audio already running")
            return
        
        try:
            self.is_running = True
            
            # Start audio stream with optimized settings
            with sd.Stream(
                channels=(1, 2),  # Mono input, stereo output
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32,
                latency=self.latency_setting,
                callback=self.audio_callback,
                device=(input_device, output_device)
            ) as stream:
                print("🎵 Optimized audio stream started!")
                print(f"🎛️ Stereo delay active: {self.stereo_delay.get_info()}")
                
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
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "underruns": self.underrun_count,
            "overflows": self.overflow_count,
            "avg_processing_time_ms": avg_processing_time,
            "buffer_size": self.buffer_size,
            "latency_ms": self.buffer_size / self.sample_rate * 1000,
            "stereo_delay_info": self.stereo_delay.get_info()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "audio_running": self.is_running,
            "stereo_delay_active": True,
            "performance_stats": self.get_performance_stats()
        }
