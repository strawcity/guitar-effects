#!/usr/bin/env python3
"""
Interactive CLI for Guitar Delay Effects System

A menu-driven interface for controlling delay effects with real-time
parameter adjustment and effect switching.
"""

import threading
import time
import numpy as np
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
        
        # Initialize default delay
        self.set_delay_effect('basic')
        
        print("🎛️ Delay Controller initialized")
    
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
        print("🎸 Delay effects system started!")
    
    def stop(self):
        """Stop the delay effects system."""
        self.is_running = False
        print("🛑 Delay effects system stopped")

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
