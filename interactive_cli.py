#!/usr/bin/env python3
"""
Interactive CLI for Guitar Delay Effects System

A menu-driven interface for controlling delay effects with real-time
parameter adjustment and effect switching.
"""

import threading
import time
import numpy as np
import sounddevice as sd
from typing import Optional, Dict, Any

from config import Config
from delay import BasicDelay, TapeDelay, MultiTapDelay, TempoSyncedDelay, StereoDelay
from gpio_interface import GPIOInterface

class DelayController:
    """Controller for delay effects."""
    
    def __init__(self):
        self.config = Config()
        self.gpio = GPIOInterface(self.config)
        
        # Current delay effect
        self.current_delay = None
        self.current_effect_type = 'basic'
        
        # Delay parameters
        self.delay_time = self.config.default_delay_time
        self.feedback = self.config.default_feedback
        self.wet_mix = self.config.default_wet_mix
        
        # Audio processing state
        self.is_running = False
        self.audio_thread = None
        
        # Audio device configuration
        self.input_device = None
        self.output_device = None
        
        # Auto-detect audio devices
        self.detect_audio_devices()
        
        # Initialize default delay
        self.set_delay_effect('basic')
        
        print("🎛️ Delay Controller initialized")
    
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
    
    def set_delay_effect(self, effect_type: str):
        """Set the current delay effect type."""
        if effect_type == 'basic':
            self.current_delay = BasicDelay(
                delay_time=self.delay_time,
                feedback=self.feedback,
                wet_mix=self.wet_mix
            )
        elif effect_type == 'tape':
            self.current_delay = TapeDelay(
                delay_time=self.delay_time,
                feedback=self.feedback,
                wet_mix=self.wet_mix
            )
        elif effect_type == 'multi':
            self.current_delay = MultiTapDelay()
            self.current_delay.sync_taps_to_tempo(120.0, ['1/4', '1/2', '3/4'])
        elif effect_type == 'tempo':
            self.current_delay = TempoSyncedDelay(
                bpm=120.0,
                note_division='1/4',
                feedback=self.feedback,
                wet_mix=self.wet_mix
            )
        elif effect_type == 'stereo':
            self.current_delay = StereoDelay(
                left_delay=self.delay_time * 0.5,
                right_delay=self.delay_time,
                feedback=self.feedback,
                wet_mix=self.wet_mix
            )
        else:
            print(f"❌ Unknown delay effect type: {effect_type}")
            return
        
        self.current_effect_type = effect_type
        print(f"✅ Set delay effect to: {effect_type}")
    
    def set_delay_time(self, time: float):
        """Set delay time in seconds."""
        self.delay_time = max(self.config.min_delay_time, 
                             min(self.config.max_delay_time, time))
        if self.current_delay:
            self.current_delay.set_parameters(delay_time=self.delay_time)
        print(f"🎛️ Delay time: {self.delay_time:.2f}s")
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0-0.9)."""
        self.feedback = max(0.0, min(0.9, feedback))
        if self.current_delay:
            self.current_delay.set_parameters(feedback=self.feedback)
        print(f"🎛️ Feedback: {self.feedback:.2f}")
    
    def set_wet_mix(self, wet_mix: float):
        """Set wet mix amount (0.0-1.0)."""
        self.wet_mix = max(0.0, min(1.0, wet_mix))
        if self.current_delay:
            self.current_delay.set_parameters(wet_mix=self.wet_mix)
        print(f"🎛️ Wet mix: {self.wet_mix:.2f}")
    
    def list_effects(self):
        """List available delay effects."""
        effects = ['basic', 'tape', 'multi', 'tempo', 'stereo']
        print("Available delay effects:", ", ".join(effects))
    
    def get_status(self):
        """Get current status."""
        return {
            'running': self.is_running,
            'effect_type': self.current_effect_type,
            'delay_time': self.delay_time,
            'feedback': self.feedback,
            'wet_mix': self.wet_mix
        }
    
    def start(self):
        """Start the delay effects system."""
        if self.is_running:
            print("⚠️  System is already running")
            return
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        print("🎸 Delay effects system started!")
    
    def stop(self):
        """Stop the delay effects system."""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        print("🛑 Delay effects system stopped")
    
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
                    
                    # Process through delay effect
                    if self.current_delay:
                        # Get stereo output from delay
                        if hasattr(self.current_delay, 'process_mono_to_stereo'):
                            # Stereo delay needs special handling
                            left_out, right_out = self.current_delay.process_mono_to_stereo(audio_in.flatten())
                        else:
                            # Other delays return stereo output
                            left_out, right_out = self.current_delay.process_buffer(audio_in.flatten())
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
    """Enhanced interactive CLI for guitar delay effects."""
    
    def __init__(self):
        self.config = Config()
        self.delay_controller = DelayController()
        self.current_effect = "delay"
        
        print("🎸 Guitar Delay Effects Interactive CLI")
        print("=" * 50)
    
    def run(self):
        """Run the interactive CLI."""
        print("\n🎛️ Available commands:")
        print("  effect <name>     - Switch to effect (delay)")
        print("  start             - Start the current effect")
        print("  stop              - Stop the current effect")
        print("  status            - Show current status")
        print("  help              - Show this help")
        print("  quit              - Exit the CLI")
        print("\n🎛️ Delay-specific commands:")
        print("  delay <type>      - Set delay type (basic, tape, multi, tempo, stereo)")
        print("  time <seconds>    - Set delay time")
        print("  feedback <0-0.9> - Set feedback amount")
        print("  wet <0-1.0>       - Set wet mix amount")
        print("  effects           - List available delay effects")
        print("  demo              - Run delay effects demo")
        
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
        elif cmd == "delay":
            if args:
                self.delay_controller.set_delay_effect(args[0])
            else:
                print("❌ Please specify delay type: basic, tape, multi, tempo, stereo")
        elif cmd == "time":
            if args:
                try:
                    time_val = float(args[0])
                    self.delay_controller.set_delay_time(time_val)
                except ValueError:
                    print("❌ Invalid time value")
            else:
                print("❌ Please specify delay time in seconds")
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
        elif cmd == "effects":
            self.delay_controller.list_effects()
        elif cmd == "demo":
            self.run_demo()
        elif cmd == "effect":
            if args:
                if args[0] == "delay":
                    self.current_effect = "delay"
                    print("✅ Switched to delay effects")
                else:
                    print(f"❌ Unknown effect: {args[0]}")
            else:
                print("❌ Please specify effect name")
        else:
            print(f"❌ Unknown command: {cmd}")
            print("💡 Type 'help' for available commands")
    
    def show_help(self):
        """Show help information."""
        print("\n🎸 Guitar Delay Effects CLI Help")
        print("=" * 40)
        print("🎛️ Basic Commands:")
        print("  start             - Start the delay effects")
        print("  stop              - Stop the delay effects")
        print("  status            - Show current status")
        print("  quit              - Exit the CLI")
        print("\n🎛️ Delay Control:")
        print("  delay <type>      - Set delay type")
        print("  time <seconds>    - Set delay time")
        print("  feedback <0-0.9>  - Set feedback amount")
        print("  wet <0-1.0>       - Set wet mix amount")
        print("  effects           - List available effects")
        print("  demo              - Run effects demo")
        print("\n🎛️ Delay Types:")
        print("  basic             - Clean echo effect")
        print("  tape              - Vintage tape delay")
        print("  multi             - Multi-tap delay")
        print("  tempo             - Tempo-synced delay")
        print("  stereo            - Stereo ping-pong delay")
    
    def show_status(self):
        """Show current status."""
        status = self.delay_controller.get_status()
        print("\n🎛️ Current Status:")
        print(f"  Running: {status['running']}")
        print(f"  Effect: {status['effect_type']}")
        print(f"  Delay Time: {status['delay_time']:.2f}s")
        print(f"  Feedback: {status['feedback']:.2f}")
        print(f"  Wet Mix: {status['wet_mix']:.2f}")
    
    def run_demo(self):
        """Run a demo of the delay effects."""
        print("🎵 Running delay effects demo...")
        
        # Create a test signal (sine wave)
        duration = 2.0
        sample_rate = self.config.sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
        
        # Process through different delay effects
        effects = ['basic', 'tape', 'multi', 'tempo', 'stereo']
        
        for effect in effects:
            print(f"\n🎛️ Testing {effect} delay...")
            self.delay_controller.set_delay_effect(effect)
            
            # Process the test signal
            if self.delay_controller.current_delay:
                try:
                    if effect == 'stereo':
                        # Stereo delay needs special handling
                        left_out, right_out = self.delay_controller.current_delay.process_mono_to_stereo(test_signal)
                    else:
                        # All other delays now return stereo output
                        left_out, right_out = self.delay_controller.current_delay.process_buffer(test_signal)
                    print(f"✅ {effect} delay processed successfully (stereo)")
                except Exception as e:
                    print(f"❌ {effect} delay processing failed: {e}")
            else:
                print(f"❌ Failed to create {effect} delay")
        
        print("\n🎵 Demo completed!")

def main():
    """Main entry point."""
    cli = EnhancedInteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main()
