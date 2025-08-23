#!/usr/bin/env python3
"""
Enhanced Interactive CLI for Guitar Effects System

Supports multiple effects including arpeggiator and delay effects,
with a menu-driven interface for easy effect selection and control.
"""

import threading
import time
from typing import Optional, Dict, Any

from optimized_audio_processor import OptimizedAudioProcessor
from config import Config
from guitar_synth.guitar_synth_controller import GuitarSynthController
from effect_controller import EffectController



class ArpeggiatorController(EffectController):
    """Controller for the arpeggiator effect."""
    
    def __init__(self, audio_processor: OptimizedAudioProcessor):
        super().__init__("arpeggiator", audio_processor)
        # Get reference to the working arpeggiator system
        self.working_arpeggiator = audio_processor.working_arpeggiator
        
    def set_tempo(self, tempo: int):
        """Set arpeggiator tempo."""
        self.working_arpeggiator.set_tempo(tempo)
        self.audio_processor.set_arpeggiator_parameter("tempo", tempo)
        
    def set_pattern(self, pattern: str):
        """Set arpeggiator pattern."""
        self.working_arpeggiator.set_pattern(pattern)
        self.audio_processor.set_arpeggiator_parameter("pattern", pattern)
        
    def set_synth(self, synth: str):
        """Set arpeggiator synth type."""
        self.working_arpeggiator.set_synth(synth)
        self.audio_processor.set_arpeggiator_parameter("synth", synth)
        
    def set_duration(self, duration: float):
        """Set arpeggiator duration."""
        self.working_arpeggiator.set_duration(duration)
        self.audio_processor.set_arpeggiator_parameter("duration", duration)
        
    def demo_mode(self):
        """Run arpeggiator demo."""
        try:
            # Use the working arpeggiator demo mode
            self.working_arpeggiator.demo_mode()
            print("🎵 Demo mode: C major chord arpeggio")
            
        except Exception as e:
            print(f"Demo mode error: {e}")
        
    def test_audio(self):
        """Test audio system."""
        self.working_arpeggiator.test_audio()
        
    def list_patterns(self):
        """List available patterns."""
        # Get patterns from the working arpeggiator
        patterns = ["up", "down", "updown", "random"]
        print("Available patterns:", ", ".join(patterns))
        
    def list_synths(self):
        """List available synths."""
        # Get synths from the working arpeggiator
        synths = ["sine", "square", "saw", "triangle"]
        print("Available synths:", ", ".join(synths))
        
    def start(self):
        """Start the arpeggiator effect (called by CLI)."""
        self.start_arpeggiator()
        
    def stop(self):
        """Stop the arpeggiator effect (called by CLI)."""
        self.stop_arpeggiator()
        
    def start_arpeggiator(self):
        """Start the working arpeggiator system."""
        try:
            # Start the main audio processing stream
            if not self.audio_processor.is_running:
                self.audio_processor.start_audio(input_device=0, output_device=0)
                print("🔊 Main audio stream started")
            
            # Start the working arpeggiator
            self.working_arpeggiator.start_arpeggiator()
            print("🎸 Working arpeggiator started! Strum chords on your guitar to hear arpeggios.")
        except Exception as e:
            print(f"Failed to start arpeggiator: {e}")
            
    def stop_arpeggiator(self):
        """Stop the working arpeggiator system."""
        try:
            # Stop the working arpeggiator
            self.working_arpeggiator.stop_arpeggiator()
            print("Arpeggiator stopped")
            
            # Stop the main audio stream
            if self.audio_processor.is_running:
                self.audio_processor.stop_audio()
                print("🔊 Main audio stream stopped")
        except Exception as e:
            print(f"Failed to stop arpeggiator: {e}")
            
    def get_status(self):
        """Get arpeggiator status."""
        try:
            status = self.working_arpeggiator.get_status()
            print("Arpeggiator Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Failed to get status: {e}")
            
    def get_help(self) -> str:
        """Get arpeggiator help."""
        return """
Arpeggiator Commands:
  start                      Start the arpeggiator
  stop                       Stop the arpeggiator
  status                     Show current status
  
  tempo <bpm>                Set tempo (60-200)
  tempo +<n> | tempo -<n>    Adjust tempo by n (e.g., tempo +10)
  
  pattern <name>             Set pattern (type 'patterns' to list)
  synth <name>               Set synth (type 'synths' to list)
  duration <seconds>         Set arpeggio duration in seconds (0.5 - 10.0)
  
  demo                       Play demo C major arpeggio once
  test_audio                 Play a 440Hz test tone
  
  patterns                   List available patterns
  synths                     List available synths
        """.strip()


class DelayController(EffectController):
    """Controller for delay effects."""
    
    def __init__(self, delay_type: str, audio_processor: OptimizedAudioProcessor):
        super().__init__(f"{delay_type}", audio_processor)
        self.delay_type = delay_type
        
    def set_delay_time(self, delay_time: float):
        """Set delay time."""
        self.audio_processor.set_delay_parameter(self.name, "delay_time", delay_time)
        
    def set_feedback(self, feedback: float):
        """Set feedback amount."""
        self.audio_processor.set_delay_parameter(self.name, "feedback", feedback)
        
    def set_wet_mix(self, wet_mix: float):
        """Set wet/dry mix."""
        self.audio_processor.set_delay_parameter(self.name, "wet_mix", wet_mix)
        
    def set_tape_parameters(self, **kwargs):
        """Set tape-specific parameters."""
        for param, value in kwargs.items():
            self.audio_processor.set_delay_parameter(self.name, param, value)
            
    def sync_taps_to_tempo(self, bpm: float, divisions: list = None):
        """Sync multi-tap delay to tempo."""
        self.audio_processor.set_delay_parameter(self.name, "sync_tempo", bpm)
        
    def set_tempo(self, tempo: float):
        """Set tempo for tempo-synced delay."""
        self.audio_processor.set_delay_parameter(self.name, "tempo", tempo)
        
    def set_stereo_parameters(self, **kwargs):
        """Set stereo-specific parameters."""
        for param, value in kwargs.items():
            self.audio_processor.set_delay_parameter(self.name, param, value)
            
    def get_help(self) -> str:
        """Get delay effect help."""
        base_help = f"""
Delay Effect Commands ({self.delay_type.title()}):
  start                      Start the delay effect
  stop                       Stop the delay effect
  status                     Show current status
  
  delay_time <seconds>       Set delay time in seconds
  feedback <0.0-0.9>         Set feedback amount
  wet_mix <0.0-1.0>          Set wet/dry mix
        """.strip()
        
        if self.delay_type == "tape":
            base_help += """
  saturation <0.0-1.0>       Set tape saturation
  wow_rate <0.0-2.0>         Set wow modulation rate
  flutter_rate <0.0-20.0>    Set flutter modulation rate
  tape_speed <0.5-2.0>       Set tape speed multiplier
            """.strip()
        elif self.delay_type == "multi":
            base_help += """
  sync_tempo <bpm>           Sync taps to tempo
  add_tap <time> <level> <pan>  Add new delay tap
  remove_tap <index>          Remove delay tap
            """.strip()
        elif self.delay_type == "tempo":
            base_help += """
  tempo <bpm>                Set tempo for sync
  note_division <name>        Set note division
  swing <0.0-1.0>            Set swing amount
  humanize <0.0-1.0>         Set humanization
            """.strip()
        elif self.delay_type == "stereo":
            base_help += """
  left_delay <seconds>        Set left channel delay
  right_delay <seconds>       Set right channel delay
  ping_pong <on/off>          Enable/disable ping-pong
  stereo_width <0.0-1.0>      Set stereo width
            """.strip()
            
        return base_help


class EnhancedInteractiveCLI:
    """Enhanced CLI supporting multiple effects."""
    
    def __init__(self):
        # Initialize audio processor
        config = Config()
        self.audio_processor = OptimizedAudioProcessor(config, sample_rate=config.sample_rate)
        
        # Create effect controllers
        self.effects = {
            "arpeggiator": ArpeggiatorController(self.audio_processor),
            "basic_delay": DelayController("basic_delay", self.audio_processor),
            "tape_delay": DelayController("tape_delay", self.audio_processor),
            "multi_delay": DelayController("multi_delay", self.audio_processor),
            "tempo_delay": DelayController("tempo_delay", self.audio_processor),
            "stereo_delay": DelayController("stereo_delay", self.audio_processor),
            "guitar_synth": GuitarSynthController(self.audio_processor)
        }
        self.current_effect = "arpeggiator"
        
        # Don't start audio processing automatically - let user start it when needed
        # self.audio_thread = None
        # self.start_audio_processing()
        
    def start_audio_processing(self):
        """Start audio processing in background thread."""
        # Use Scarlett 2i2 device (device 0) for Pi
        if self.audio_processor.config.is_pi:
            self.audio_thread = threading.Thread(
                target=lambda: self.audio_processor.start_audio(input_device=0, output_device=0), 
                daemon=True
            )
        else:
            self.audio_thread = threading.Thread(target=self.audio_processor.start_audio, daemon=True)
        
        self.audio_thread.start()
        print("Audio processing started in background")
        if self.audio_processor.config.is_pi:
            print("🎧 Using Scarlett 2i2 (device 0) for audio")
        
    def get_current_effect(self) -> EffectController:
        """Get the currently selected effect."""
        return self.effects[self.current_effect]
        
    def list_effects(self):
        """List all available effects."""
        print("\n=== Available Effects ===")
        for effect_name, effect in self.effects.items():
            status = "🟢 Active" if effect.is_active else "🔴 Inactive"
            print(f"  {effect_name:15} - {status}")
        print(f"\nCurrent effect: {self.current_effect}")
        
    def select_effect(self, effect_name: str):
        """Select an effect to control."""
        if effect_name in self.effects:
            self.current_effect = effect_name
            print(f"Selected effect: {effect_name}")
        else:
            print(f"Unknown effect: {effect_name}")
            print("Available effects:", ", ".join(self.effects.keys()))
            
    def show_status(self):
        """Show status of current effect."""
        effect = self.get_current_effect()
        status = effect.get_status()
        
        print(f"\n=== {effect.name} Status ===")
        for key, value in status.items():
            if key != "name":
                print(f"{key:15}: {value}")
        print("=" * 30)
        
    def print_main_help(self):
        """Print main help menu."""
        print("""
🎸 Guitar Effects System - Interactive CLI
==========================================

Main Commands:
  effects                    List all available effects
  select <effect>            Select effect to control
  status                     Show current effect status
  help                       Show effect-specific help
  
  start                      Start current effect
  stop                       Stop current effect
  
  quit | q | exit            Exit the CLI

Available Effects:
  arpeggiator                Chord detection and arpeggio generation
  basic_delay                Simple echo delay effect
  tape_delay                 Vintage tape-style delay
  multi_delay                Multi-tap delay patterns
  tempo_delay                Tempo-synchronized delay
  stereo_delay               Stereo ping-pong delay
  guitar_synth               Guitar synthesizer transformation effect

Type 'select <effect>' to choose an effect, then use 'help' for effect-specific commands.
        """.strip())
        
    def print_effect_help(self):
        """Print help for current effect."""
        effect = self.get_current_effect()
        print(f"\n=== {effect.name} Help ===")
        print(effect.get_help())
        
    def run(self):
        """Run the enhanced CLI."""
        print("\n🎸 Welcome to Guitar Effects System Interactive CLI!")
        self.print_main_help()
        
        try:
            while True:
                try:
                    line = input(f"effects[{self.current_effect}]> ").strip()
                except EOFError:
                    line = "quit"

                if not line:
                    continue

                parts = line.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ("quit", "q", "exit"):
                    break
                elif cmd == "help":
                    self.print_effect_help()
                elif cmd == "effects":
                    self.list_effects()
                elif cmd == "select":
                    if not args:
                        print("Usage: select <effect_name>")
                        self.list_effects()
                        continue
                    self.select_effect(args[0])
                elif cmd == "status":
                    self.show_status()
                elif cmd == "start":
                    self.get_current_effect().start()
                elif cmd == "stop":
                    self.get_current_effect().stop()
                else:
                    # Try to handle effect-specific commands
                    self._handle_effect_command(cmd, args)
                    
        except KeyboardInterrupt:
            print("\nInterrupted.")
        finally:
            # Stop all effects and audio
            for effect in self.effects.values():
                if effect.is_active:
                    effect.stop()
            self.audio_processor.stop_audio()
            print("Goodbye.")
            
    def _handle_effect_command(self, cmd: str, args: list):
        """Handle effect-specific commands."""
        effect = self.get_current_effect()
        
        if cmd == "tempo":
            if not args:
                print("Usage: tempo <bpm>|+<n>|-<n>")
                return
            val = args[0]
            try:
                if val.startswith("+") or val.startswith("-"):
                    delta = int(val)
                    if hasattr(effect, 'tempo'):
                        effect.set_tempo(effect.tempo + delta)
                    else:
                        print("Current effect doesn't support tempo adjustment")
                else:
                    bpm = int(val)
                    effect.set_tempo(bpm)
            except ValueError:
                print("Invalid tempo value.")
                
        elif cmd == "delay_time":
            if not args:
                print("Usage: delay_time <seconds>")
                return
            try:
                delay_time = float(args[0])
                effect.set_delay_time(delay_time)
            except ValueError:
                print("Invalid delay time value.")
                
        elif cmd == "feedback":
            if not args:
                print("Usage: feedback <0.0-0.9>")
                return
            try:
                feedback = float(args[0])
                effect.set_feedback(feedback)
            except ValueError:
                print("Invalid feedback value.")
                
        elif cmd == "wet_mix":
            if not args:
                print("Usage: wet_mix <0.0-1.0>")
                return
            try:
                wet_mix = float(args[0])
                effect.set_wet_mix(wet_mix)
            except ValueError:
                print("Invalid wet mix value.")
                
        elif cmd == "pattern":
            if not args:
                print("Usage: pattern <name>")
                if hasattr(effect, 'list_patterns'):
                    effect.list_patterns()
                return
            effect.set_pattern(args[0])
            
        elif cmd == "synth":
            if not args:
                print("Usage: synth <name>")
                if hasattr(effect, 'list_synths'):
                    effect.list_synths()
                return
            effect.set_synth(args[0])
            
        elif cmd == "duration":
            if not args:
                print("Usage: duration <seconds>")
                return
            try:
                duration = float(args[0])
                effect.set_duration(duration)
            except ValueError:
                print("Invalid duration value.")
                
        elif cmd == "demo":
            if hasattr(effect, 'demo_mode'):
                effect.demo_mode()
            else:
                print("Current effect doesn't support demo mode")
                
        elif cmd == "test_audio":
            if hasattr(effect, 'test_audio'):
                effect.test_audio()
            else:
                print("Current effect doesn't support audio testing")
                
        elif cmd == "patterns":
            if hasattr(effect, 'list_patterns'):
                effect.list_patterns()
            else:
                print("Current effect doesn't support patterns")
                
        elif cmd == "synths":
            if hasattr(effect, 'list_synths'):
                effect.list_synths()
            else:
                print("Current effect doesn't support synths")
                
        # Guitar synth specific commands
        elif cmd == "ring_freq":
            if not args:
                print("Usage: ring_freq <frequency_hz>")
                return
            try:
                freq = float(args[0])
                effect.set_ring_frequency(freq)
            except ValueError:
                print("Invalid frequency value.")
                
        elif cmd == "bit_depth":
            if not args:
                print("Usage: bit_depth <1-16>")
                return
            try:
                depth = int(args[0])
                effect.set_bit_depth(depth)
            except ValueError:
                print("Invalid bit depth value.")
                
        elif cmd == "sample_rate":
            if not args:
                print("Usage: sample_rate <0.1-1.0>")
                return
            try:
                factor = float(args[0])
                effect.set_sample_rate_reduction(factor)
            except ValueError:
                print("Invalid sample rate reduction value.")
                
        elif cmd == "wave_shape":
            if not args:
                print("Usage: wave_shape <0.0-1.0>")
                return
            try:
                amount = float(args[0])
                effect.set_wave_shape_amount(amount)
            except ValueError:
                print("Invalid wave shape amount value.")
                
        elif cmd == "filter_cutoff":
            if not args:
                print("Usage: filter_cutoff <frequency_hz>")
                return
            try:
                cutoff = float(args[0])
                effect.set_filter_cutoff(cutoff)
            except ValueError:
                print("Invalid filter cutoff value.")
                
        elif cmd == "filter_resonance":
            if not args:
                print("Usage: filter_resonance <0.0-1.0>")
                return
            try:
                resonance = float(args[0])
                effect.set_filter_resonance(resonance)
            except ValueError:
                print("Invalid filter resonance value.")
                
        elif cmd == "envelope":
            if not args:
                print("Usage: envelope <0.0-1.0>")
                return
            try:
                sensitivity = float(args[0])
                effect.set_envelope_sensitivity(sensitivity)
            except ValueError:
                print("Invalid envelope sensitivity value.")
                
        elif cmd == "lfo_freq":
            if not args:
                print("Usage: lfo_freq <frequency_hz>")
                return
            try:
                freq = float(args[0])
                effect.set_lfo_frequency(freq)
            except ValueError:
                print("Invalid LFO frequency value.")
                
        elif cmd == "lfo_depth":
            if not args:
                print("Usage: lfo_depth <0.0-1.0>")
                return
            try:
                depth = float(args[0])
                effect.set_lfo_depth(depth)
            except ValueError:
                print("Invalid LFO depth value.")
                
        elif cmd == "preset":
            if not args:
                print("Usage: preset <name>")
                if hasattr(effect, 'list_presets'):
                    effect.list_presets()
                return
            effect.set_preset(args[0])
            
        elif cmd == "presets":
            if hasattr(effect, 'list_presets'):
                effect.list_presets()
            else:
                print("Current effect doesn't support presets")
                
        elif cmd == "reset":
            if hasattr(effect, 'reset'):
                effect.reset()
            else:
                print("Current effect doesn't support reset")
                
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for effect-specific commands")


def main():
    cli = EnhancedInteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()
