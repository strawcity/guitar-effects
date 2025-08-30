#!/usr/bin/env python3
"""
Interactive CLI for Guitar Stereo Delay Effects System

A menu-driven interface for controlling stereo delay effects with real-time
parameter adjustment.
"""

import threading
import time
import numpy as np
import sounddevice as sd
from typing import Optional, Dict, Any

from config import Config
from delay import StereoDelay
from gpio_interface import GPIOInterface

class StereoDelayController:
    """Controller for stereo delay effects."""
    
    def __init__(self):
        self.config = Config()
        self.gpio = GPIOInterface(self.config)
        
        # Stereo delay effect
        self.stereo_delay = None
        
        # Stereo delay parameters
        self.left_delay = 0.3
        self.right_delay = 0.6
        self.feedback = self.config.default_feedback
        self.wet_mix = self.config.default_wet_mix
        self.ping_pong = True
        self.stereo_width = 0.5
        self.cross_feedback = 0.2
        
        # Audio processing state
        self.is_running = False
        self.audio_thread = None
        
        # Audio device configuration
        self.input_device = None
        self.output_device = None
        
        # Auto-detect audio devices
        self.detect_audio_devices()
        
        # Initialize stereo delay
        self.initialize_stereo_delay()
        
        # Show default values
        self.show_default_values()
        
        print("🎛️ Stereo Delay Controller initialized")
    
    def detect_audio_devices(self):
        """Auto-detect and configure audio devices with platform-specific logic"""
        print("\n🔊 Auto-detecting audio devices...")
        
        try:
            devices = sd.query_devices()
            device_priorities = self.config.get_audio_devices()
            
            # Find input device based on platform priorities
            self.input_device = self._find_input_device(devices, device_priorities['input_priorities'])
            
            # Find output device based on platform priorities
            self.output_device = self._find_output_device(devices, device_priorities['output_priorities'])
            
            print(f"🎯 Final configuration:")
            print(f"   Input: {devices[self.input_device]['name']} (ID: {self.input_device})")
            print(f"   Output: {devices[self.output_device]['name']} (ID: {self.output_device})")
            
        except Exception as e:
            print(f"❌ Error detecting audio devices: {e}")
            # Fallback to defaults
            self.input_device = None
            self.output_device = None
            print("⚠️  Falling back to system default devices")
    
    def _find_input_device(self, devices, priorities):
        """Find the best input device based on platform priorities"""
        for priority in priorities:
            for i, device in enumerate(devices):
                # Check if device has input capability
                has_input = (device.get('max_inputs', 0) > 0 or 
                           device.get('hostapi', 0) >= 0)  # Fallback check
                if has_input and priority.lower() in device['name'].lower():
                    print(f"✅ Found input device: {device['name']}")
                    return i
        
        # Fallback to default input
        try:
            default_input = sd.default.device[0]
            print(f"⚠️  Using default input device: {devices[default_input]['name']}")
            return default_input
        except:
            # If no default device, use first available input device
            for i, device in enumerate(devices):
                if device.get('max_inputs', 0) > 0:
                    print(f"⚠️  Using first available input device: {device['name']}")
                    return i
            return None
    
    def _find_output_device(self, devices, priorities):
        """Find the best output device based on platform priorities"""
        for priority in priorities:
            for i, device in enumerate(devices):
                # Check if device has output capability
                has_output = (device.get('max_outputs', 0) > 0 or 
                            device.get('hostapi', 0) >= 0)  # Fallback check
                if has_output and priority.lower() in device['name'].lower():
                    print(f"✅ Found output device: {device['name']}")
                    return i
        
        # Fallback to default output
        try:
            default_output = sd.default.device[1]
            print(f"⚠️  Using default output device: {devices[default_output]['name']}")
            return default_output
        except:
            # If no default device, use first available output device
            for i, device in enumerate(devices):
                if device.get('max_outputs', 0) > 0:
                    print(f"⚠️  Using first available output device: {device['name']}")
                    return i
            return None
    
    def initialize_stereo_delay(self):
        """Initialize the stereo delay effect"""
        self.stereo_delay = StereoDelay(
            sample_rate=self.config.sample_rate,
            left_delay=self.left_delay,
            right_delay=self.right_delay,
            feedback=self.feedback,
            wet_mix=self.wet_mix,
            ping_pong=self.ping_pong,
            stereo_width=self.stereo_width,
            cross_feedback=self.cross_feedback
        )
        print(f"✅ Stereo delay initialized: {self.stereo_delay.get_info()}")
        
    def show_default_values(self):
        """Display the default parameter values."""
        print("\n🎛️ Default Parameter Values:")
        print("=" * 35)
        print(f"  Left Delay:     {self.left_delay:.2f}s")
        print(f"  Right Delay:    {self.right_delay:.2f}s")
        print(f"  Feedback:       {self.feedback:.2f} (0.0-0.9)")
        print(f"  Wet Mix:        {self.wet_mix:.2f} (0.0-1.0)")
        print(f"  Stereo Width:   {self.stereo_width:.2f} (0.0-1.0)")
        print(f"  Cross-feedback: {self.cross_feedback:.2f} (0.0-0.5)")
        print(f"  Ping-pong:      {'On' if self.ping_pong else 'Off'}")
        print("\n💡 Use 'help' to see available commands")
        print("💡 Use 'status' to see current values")
    
    def set_left_delay(self, time: float):
        """Set left channel delay time in seconds."""
        self.left_delay = max(self.config.min_delay_time, 
                             min(self.config.max_delay_time, time))
        if self.stereo_delay:
            self.stereo_delay.set_left_delay(self.left_delay)
        print(f"🎛️ Left delay time: {self.left_delay:.2f}s")
    
    def set_right_delay(self, time: float):
        """Set right channel delay time in seconds."""
        self.right_delay = max(self.config.min_delay_time, 
                              min(self.config.max_delay_time, time))
        if self.stereo_delay:
            self.stereo_delay.set_right_delay(self.right_delay)
        print(f"🎛️ Right delay time: {self.right_delay:.2f}s")
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0-0.9)."""
        self.feedback = max(0.0, min(0.9, feedback))
        if self.stereo_delay:
            self.stereo_delay.set_parameters(feedback=self.feedback)
        print(f"🎛️ Feedback: {self.feedback:.2f}")
    
    def set_wet_mix(self, wet_mix: float):
        """Set wet mix amount (0.0-1.0)."""
        self.wet_mix = max(0.0, min(1.0, wet_mix))
        if self.stereo_delay:
            self.stereo_delay.set_parameters(wet_mix=self.wet_mix)
        print(f"🎛️ Wet mix: {self.wet_mix:.2f}")
    
    def set_stereo_width(self, width: float):
        """Set stereo width (0.0-1.0)."""
        self.stereo_width = max(0.0, min(1.0, width))
        if self.stereo_delay:
            self.stereo_delay.set_stereo_parameters(stereo_width=self.stereo_width)
        print(f"🎛️ Stereo width: {self.stereo_width:.2f}")
    
    def set_cross_feedback(self, cross_feedback: float):
        """Set cross-feedback amount (0.0-0.5)."""
        self.cross_feedback = max(0.0, min(0.5, cross_feedback))
        if self.stereo_delay:
            self.stereo_delay.set_stereo_parameters(cross_feedback=self.cross_feedback)
        print(f"🎛️ Cross-feedback: {self.cross_feedback:.2f}")
    
    def toggle_ping_pong(self):
        """Toggle ping-pong mode."""
        self.ping_pong = not self.ping_pong
        if self.stereo_delay:
            self.stereo_delay.set_stereo_parameters(ping_pong=self.ping_pong)
        print(f"🎛️ Ping-pong: {'On' if self.ping_pong else 'Off'}")
    
    def get_status(self):
        """Get current status."""
        return {
            'running': self.is_running,
            'left_delay': self.left_delay,
            'right_delay': self.right_delay,
            'feedback': self.feedback,
            'wet_mix': self.wet_mix,
            'ping_pong': self.ping_pong,
            'stereo_width': self.stereo_width,
            'cross_feedback': self.cross_feedback
        }
    
    def start(self):
        """Start the stereo delay effects system."""
        if self.is_running:
            print("⚠️  System is already running")
            return
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        print("🎸 Stereo delay effects system started!")
    
    def stop(self):
        """Stop the stereo delay effects system."""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        print("🛑 Stereo delay effects system stopped")
    
    def audio_loop(self):
        """Main audio processing loop"""
        try:
            # Use None for device if no specific devices were found
            input_dev = self.input_device if self.input_device is not None else None
            output_dev = self.output_device if self.output_device is not None else None
            
            with sd.Stream(
                device=(input_dev, output_dev),
                channels=(1, 2),  # Mono input, stereo output
                samplerate=self.config.sample_rate,
                blocksize=self.config.chunk_size,
                dtype=np.float32
            ) as stream:
                print("🎵 Audio stream started (mono input → stereo output)")
                
                while self.is_running:
                    # Read audio input
                    audio_in, overflowed = stream.read(self.config.chunk_size)
                    
                    if overflowed:
                        print("⚠️  Audio buffer overflow")
                    
                    # Process through stereo delay effect
                    if self.stereo_delay:
                        # Get stereo output from delay
                        left_out, right_out = self.stereo_delay.process_mono_to_stereo(audio_in.flatten())
                        # Combine into stereo array
                        audio_out = np.column_stack((left_out, right_out))
                    else:
                        # No delay - duplicate mono to stereo
                        mono_out = audio_in.flatten()
                        audio_out = np.column_stack((mono_out, mono_out))
                    
                    # Write stereo audio output
                    stream.write(audio_out)
                    
        except Exception as e:
            print(f"❌ Audio processing error: {e}")
            self.is_running = False

class EnhancedInteractiveCLI:
    """Enhanced interactive CLI for guitar stereo delay effects."""
    
    def __init__(self):
        self.config = Config()
        self.delay_controller = StereoDelayController()
        
        print("🎸 Guitar Stereo Delay Effects Interactive CLI")
        print("=" * 50)
    
    def run(self):
        """Run the interactive CLI."""
        print("\n🎛️ Available commands:")
        print("  start             - Start the stereo delay effect")
        print("  stop              - Stop the stereo delay effect")
        print("  status            - Show current status")
        print("  help              - Show this help")
        print("  quit              - Exit the CLI")
        print("\n🎛️ Stereo delay commands:")
        print("  left <seconds>    - Set left channel delay time")
        print("  right <seconds>   - Set right channel delay time")
        print("  feedback <0-0.9> - Set feedback amount")
        print("  wet <0-1.0>       - Set wet mix amount")
        print("  width <0-1.0>     - Set stereo width")
        print("  cross <0-0.5>     - Set cross-feedback amount")
        print("  ping              - Toggle ping-pong mode")
        
        while True:
            try:
                command = input("\n🎸 > ").strip().lower()
                if not command:
                    continue
                
                if command == "quit" or command == "exit":
                    self.delay_controller.stop()
                    print("👋 Goodbye!")
                    break
                
                self.process_command(command)
                
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                self.delay_controller.stop()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def process_command(self, command: str):
        """Process a command."""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "help":
            self.show_help()
        elif cmd == "start":
            self.delay_controller.start()
        elif cmd == "stop":
            self.delay_controller.stop()
        elif cmd == "status":
            self.show_status()
        elif cmd == "left":
            if args:
                try:
                    time_val = float(args[0])
                    self.delay_controller.set_left_delay(time_val)
                except ValueError:
                    print("❌ Invalid time value")
            else:
                print("❌ Please specify left delay time in seconds")
        elif cmd == "right":
            if args:
                try:
                    time_val = float(args[0])
                    self.delay_controller.set_right_delay(time_val)
                except ValueError:
                    print("❌ Invalid time value")
            else:
                print("❌ Please specify right delay time in seconds")
        elif cmd == "feedback":
            if args:
                try:
                    feedback_val = float(args[0])
                    self.delay_controller.set_feedback(feedback_val)
                except ValueError:
                    print("❌ Invalid feedback value")
            else:
                print("❌ Please specify feedback amount (0.0-0.9)")
        elif cmd == "wet":
            if args:
                try:
                    wet_val = float(args[0])
                    self.delay_controller.set_wet_mix(wet_val)
                except ValueError:
                    print("❌ Invalid wet mix value")
            else:
                print("❌ Please specify wet mix amount (0.0-1.0)")
        elif cmd == "width":
            if args:
                try:
                    width_val = float(args[0])
                    self.delay_controller.set_stereo_width(width_val)
                except ValueError:
                    print("❌ Invalid stereo width value")
            else:
                print("❌ Please specify stereo width amount (0.0-1.0)")
        elif cmd == "cross":
            if args:
                try:
                    cross_val = float(args[0])
                    self.delay_controller.set_cross_feedback(cross_val)
                except ValueError:
                    print("❌ Invalid cross-feedback value")
            else:
                print("❌ Please specify cross-feedback amount (0.0-0.5)")
        elif cmd == "ping":
            self.delay_controller.toggle_ping_pong()
        elif cmd == "defaults":
            self.delay_controller.show_default_values()
        else:
            print(f"❌ Unknown command: {cmd}")
            print("💡 Type 'help' for available commands")
    
    def show_help(self):
        """Show help information."""
        print("\n🎸 Guitar Stereo Delay Effects CLI Help")
        print("=" * 40)
        print("🎛️ Basic Commands:")
        print("  start             - Start the stereo delay effects")
        print("  stop              - Stop the stereo delay effects")
        print("  status            - Show current status")
        print("  defaults          - Show default parameter values")
        print("  quit              - Exit the CLI")
        print("\n🎛️ Stereo Delay Control:")
        print("  left <seconds>    - Set left channel delay time")
        print("  right <seconds>   - Set right channel delay time")
        print("  feedback <0-0.9>  - Set feedback amount")
        print("  wet <0-1.0>       - Set wet mix amount")
        print("  width <0-1.0>     - Set stereo width enhancement")
        print("  cross <0-0.5>     - Set cross-feedback amount")
        print("  ping              - Toggle ping-pong mode")
        print("\n🎛️ Stereo Delay Features:")
        print("  • Independent left/right delay times")
        print("  • Ping-pong delay patterns")
        print("  • Stereo width enhancement")
        print("  • Cross-feedback between channels")
        print("  • Cross-feedback distortion (various types)")
    
    def show_status(self):
        """Show current status."""
        status = self.delay_controller.get_status()
        print("\n🎛️ Current Status:")
        print(f"  Running: {status['running']}")
        print(f"  Left Delay: {status['left_delay']:.2f}s")
        print(f"  Right Delay: {status['right_delay']:.2f}s")
        print(f"  Feedback: {status['feedback']:.2f}")
        print(f"  Wet Mix: {status['wet_mix']:.2f}")
        print(f"  Ping-pong: {'On' if status['ping_pong'] else 'Off'}")
        print(f"  Stereo Width: {status['stereo_width']:.2f}")
        print(f"  Cross-feedback: {status['cross_feedback']:.2f}")

def main():
    """Main entry point."""
    print("🎸 Guitar Stereo Delay Effects System")
    print("=" * 45)
    
    cli = EnhancedInteractiveCLI()
    
    # Start the stereo delay immediately
    cli.delay_controller.start()
    
    print("\n🎵 Ready to rock! Type 'help' for commands.")
    print("=" * 45)
    
    # Run the interactive CLI
    cli.run()

if __name__ == "__main__":
    main()
