#!/usr/bin/env python3
"""
Enhanced Interactive CLI for Guitar Effects System

Supports multiple effects including arpeggiator and delay effects,
with a menu-driven interface for easy effect selection and control.
"""

import threading
import time
from typing import Optional, Dict, Any

from main import GuitarArpeggiator
from delay import (BasicDelay, TapeDelay, MultiTapDelay, 
                   TempoSyncedDelay, StereoDelay)


class EffectController:
    """Base class for effect controllers."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = False
        
    def start(self):
        """Start the effect."""
        self.is_active = True
        
    def stop(self):
        """Stop the effect."""
        self.is_active = False
        
    def get_status(self) -> Dict[str, Any]:
        """Get effect status."""
        return {"name": self.name, "active": self.is_active}
        
    def get_help(self) -> str:
        """Get effect-specific help."""
        return f"Help for {self.name} effect"


class ArpeggiatorController(EffectController):
    """Controller for the arpeggiator effect."""
    
    def __init__(self):
        super().__init__("Arpeggiator")
        self.arpeggiator = GuitarArpeggiator()
        self.run_thread = None
        
    def start(self):
        """Start the arpeggiator."""
        if self.is_active:
            print("Arpeggiator already running.")
            return
            
        self.is_active = True
        self.run_thread = threading.Thread(target=self.arpeggiator.start, daemon=True)
        self.run_thread.start()
        print("Started arpeggiator in background.")
        
    def stop(self):
        """Stop the arpeggiator."""
        if not self.is_active:
            print("Arpeggiator not running.")
            return
            
        self.arpeggiator.stop()
        if self.run_thread:
            self.run_thread.join(timeout=2.0)
        self.run_thread = None
        self.is_active = False
        print("Stopped arpeggiator.")
        
    def get_status(self) -> Dict[str, Any]:
        """Get arpeggiator status."""
        status = super().get_status()
        status.update({
            "tempo": self.arpeggiator.tempo,
            "pattern": self.arpeggiator.pattern,
            "synth": self.arpeggiator.synth_type,
            "duration": self.arpeggiator.duration
        })
        
        current = getattr(self.arpeggiator, 'current_chord', None)
        if current and current.get('valid'):
            status["current_chord"] = f"{current.get('root')} {current.get('quality')} (conf {current.get('confidence'):.2f})"
        else:
            status["current_chord"] = "none"
            
        return status
        
    def set_tempo(self, tempo: int):
        """Set arpeggiator tempo."""
        self.arpeggiator.set_tempo(tempo)
        
    def set_pattern(self, pattern: str):
        """Set arpeggiator pattern."""
        self.arpeggiator.set_pattern(pattern)
        
    def set_synth(self, synth: str):
        """Set arpeggiator synth type."""
        self.arpeggiator.set_synth(synth)
        
    def set_duration(self, duration: float):
        """Set arpeggiator duration."""
        self.arpeggiator.set_duration(duration)
        
    def demo_mode(self):
        """Run arpeggiator demo."""
        self.arpeggiator.demo_mode()
        
    def test_audio(self):
        """Test audio system."""
        self.arpeggiator.test_audio_system()
        
    def list_patterns(self):
        """List available patterns."""
        patterns = list(self.arpeggiator.arpeggio_engine.patterns.keys())
        print("Available patterns:", ", ".join(patterns))
        
    def list_synths(self):
        """List available synths."""
        synths = list(self.arpeggiator.synth_engine.synth_types.keys())
        print("Available synths:", ", ".join(synths))
        
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
    
    def __init__(self, delay_type: str = "basic"):
        super().__init__(f"Delay ({delay_type.title()})")
        self.delay_type = delay_type
        self.delay_effect = None
        self.sample_rate = 44100
        self._create_delay_effect()
        
    def _create_delay_effect(self):
        """Create the appropriate delay effect."""
        if self.delay_type == "basic":
            self.delay_effect = BasicDelay(sample_rate=self.sample_rate)
        elif self.delay_type == "tape":
            self.delay_effect = TapeDelay(sample_rate=self.sample_rate)
        elif self.delay_type == "multi":
            self.delay_effect = MultiTapDelay(sample_rate=self.sample_rate)
        elif self.delay_type == "tempo":
            self.delay_effect = TempoSyncedDelay(sample_rate=self.sample_rate)
        elif self.delay_type == "stereo":
            self.delay_effect = StereoDelay(sample_rate=self.sample_rate)
        else:
            self.delay_effect = BasicDelay(sample_rate=self.sample_rate)
            
    def get_status(self) -> Dict[str, Any]:
        """Get delay effect status."""
        status = super().get_status()
        if self.delay_effect:
            status.update(self.delay_effect.get_parameters())
            status["info"] = self.delay_effect.get_info()
        return status
        
    def set_delay_time(self, delay_time: float):
        """Set delay time."""
        if self.delay_effect:
            self.delay_effect.set_delay_time(delay_time)
            
    def set_feedback(self, feedback: float):
        """Set feedback amount."""
        if self.delay_effect:
            self.delay_effect.set_feedback(feedback)
            
    def set_wet_mix(self, wet_mix: float):
        """Set wet/dry mix."""
        if self.delay_effect:
            self.delay_effect.set_wet_mix(wet_mix)
            
    def set_tape_parameters(self, **kwargs):
        """Set tape-specific parameters."""
        if hasattr(self.delay_effect, 'set_tape_parameters'):
            self.delay_effect.set_tape_parameters(**kwargs)
            
    def sync_taps_to_tempo(self, bpm: float, divisions: list = None):
        """Sync multi-tap delay to tempo."""
        if hasattr(self.delay_effect, 'sync_taps_to_tempo'):
            self.delay_effect.sync_taps_to_tempo(bpm, divisions)
            
    def set_tempo(self, bpm: float):
        """Set tempo for tempo-synced delay."""
        if hasattr(self.delay_effect, 'set_tempo'):
            self.delay_effect.set_tempo(bpm)
            
    def set_stereo_parameters(self, **kwargs):
        """Set stereo-specific parameters."""
        if hasattr(self.delay_effect, 'set_stereo_parameters'):
            self.delay_effect.set_stereo_parameters(**kwargs)
            
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
        self.effects = {
            "arpeggiator": ArpeggiatorController(),
            "basic_delay": DelayController("basic"),
            "tape_delay": DelayController("tape"),
            "multi_delay": DelayController("multi"),
            "tempo_delay": DelayController("tempo"),
            "stereo_delay": DelayController("stereo")
        }
        self.current_effect = "arpeggiator"
        
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
            # Stop all effects
            for effect in self.effects.values():
                if effect.is_active:
                    effect.stop()
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
                
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for effect-specific commands")


def main():
    cli = EnhancedInteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()


