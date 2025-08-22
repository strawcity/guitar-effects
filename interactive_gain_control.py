#!/usr/bin/env python3
"""
Interactive Gain Control for Guitar Arpeggiator
Run this script to test and adjust gain settings interactively
"""

import numpy as np
import sounddevice as sd
import time
import threading

class InteractiveGainControl:
    def __init__(self):
        self.gain = 3.0
        self.target_level = 0.7
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start real-time audio monitoring with current gain"""
        if self.is_monitoring:
            print("⚠️  Already monitoring audio")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_audio, daemon=True)
        self.monitor_thread.start()
        print("🎤 Started audio monitoring...")
        print("💡 Play your guitar to see the effect of gain changes")
        
    def stop_monitoring(self):
        """Stop audio monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("🛑 Stopped audio monitoring")
        
    def _monitor_audio(self):
        """Monitor audio input with current gain settings"""
        try:
            with sd.InputStream(samplerate=44100, channels=1, dtype=np.float32) as stream:
                while self.is_monitoring:
                    # Read audio data
                    audio_data, overflowed = stream.read(1024)
                    if overflowed:
                        print("⚠️  Audio buffer overflow")
                        continue
                    
                    # Apply current gain
                    raw_audio = audio_data.flatten()
                    gained_audio = raw_audio * self.gain
                    gained_audio = np.clip(gained_audio, -1.0, 1.0)
                    
                    # Calculate levels
                    raw_max = np.max(np.abs(raw_audio))
                    raw_avg = np.mean(np.abs(raw_audio))
                    gained_max = np.max(np.abs(gained_audio))
                    gained_avg = np.mean(np.abs(gained_audio))
                    
                    # Create visual meters
                    raw_meter = "█" * int(raw_max * 20) + "░" * (20 - int(raw_max * 20))
                    gained_meter = "█" * int(gained_max * 20) + "░" * (20 - int(gained_max * 20))
                    
                    # Status indicators
                    raw_status = "✅" if raw_max > 0.1 else "⚠️" if raw_max > 0.01 else "❌"
                    gained_status = "✅" if gained_max > 0.5 else "⚠️" if gained_max > 0.3 else "❌"
                    
                    # Display
                    print(f"\r🎤 Raw: {raw_status} {raw_meter} | Max: {raw_max:.4f} | Gain: {gained_status} {gained_meter} | Max: {gained_max:.4f} | Gain: {self.gain:.1f}x", end="", flush=True)
                    
                    time.sleep(0.1)  # Update 10 times per second
                    
        except Exception as e:
            print(f"❌ Audio monitoring error: {e}")
            self.is_monitoring = False
    
    def set_gain(self, new_gain):
        """Set the gain value"""
        if 0.5 <= new_gain <= 10.0:
            old_gain = self.gain
            self.gain = new_gain
            print(f"🎚️  Gain changed: {old_gain:.1f}x → {self.gain:.1f}x")
            
            # Show recommendation
            if self.gain < 2.0:
                print("💡 Low gain - good for strong guitar signals")
            elif self.gain < 5.0:
                print("💡 Medium gain - good for most guitar signals")
            else:
                print("💡 High gain - good for weak guitar signals")
        else:
            print(f"⚠️  Gain {new_gain:.1f}x is outside valid range (0.5-10.0)")
    
    def adjust_gain(self, delta):
        """Adjust gain by delta amount"""
        new_gain = self.gain + delta
        self.set_gain(new_gain)
    
    def show_status(self):
        """Show current gain settings and recommendations"""
        print(f"\n🎚️  Current Settings:")
        print(f"   Gain: {self.gain:.1f}x")
        print(f"   Target Level: {self.target_level}")
        print(f"   Monitoring: {'Yes' if self.is_monitoring else 'No'}")
        
        print(f"\n💡 Recommendations:")
        if self.gain < 2.0:
            print("   - Current gain is low")
            print("   - Good for strong guitar signals")
            print("   - Try 'gain+ 2' if detection is poor")
        elif self.gain < 5.0:
            print("   - Current gain is moderate")
            print("   - Good for most guitar signals")
            print("   - Adjust with 'gain+' or 'gain-' as needed")
        else:
            print("   - Current gain is high")
            print("   - Good for weak guitar signals")
            print("   - Try 'gain- 2' if signal is clipping")
    
    def run_interactive(self):
        """Run the interactive gain control interface"""
        print("🎚️  Interactive Gain Control")
        print("=" * 40)
        print("Commands:")
        print("  start - Start audio monitoring")
        print("  stop - Stop audio monitoring")
        print("  gain+ - Increase gain by 0.5")
        print("  gain- - Decrease gain by 0.5")
        print("  gain++ - Increase gain by 1.0")
        print("  gain-- - Decrease gain by 1.0")
        print("  gain=value - Set specific gain (e.g., gain=5.0)")
        print("  status - Show current settings")
        print("  quit - Exit")
        print()
        
        self.show_status()
        
        while True:
            try:
                command = input("🎚️  Command: ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "start":
                    self.start_monitoring()
                elif command == "stop":
                    self.stop_monitoring()
                elif command == "gain+":
                    self.adjust_gain(0.5)
                elif command == "gain-":
                    self.adjust_gain(-0.5)
                elif command == "gain++":
                    self.adjust_gain(1.0)
                elif command == "gain--":
                    self.adjust_gain(-1.0)
                elif command.startswith("gain="):
                    try:
                        value = float(command.split("=")[1])
                        self.set_gain(value)
                    except ValueError:
                        print("⚠️  Invalid gain value. Use format: gain=5.0")
                elif command == "status":
                    self.show_status()
                elif command == "help":
                    print("Commands: start, stop, gain+, gain-, gain++, gain--, gain=value, status, quit")
                else:
                    print(f"❓ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Clean up
        self.stop_monitoring()

def main():
    """Main entry point"""
    controller = InteractiveGainControl()
    controller.run_interactive()

if __name__ == "__main__":
    main()
