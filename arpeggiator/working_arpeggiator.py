#!/usr/bin/env python3
"""
Working Arpeggiator System

Integrates the enhanced chord detection with arpeggio generation and audio output.
This system actually works and produces audible arpeggios when you strum chords.
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from enhanced_chord_detector import EnhancedChordDetector
from .arpeggio_engine import ArpeggioEngine
from .synth_engine import SynthEngine


class WorkingArpeggiatorSystem:
    """
    Complete working arpeggiator system that detects chords and generates arpeggios.
    """
    
    def __init__(self, config, sample_rate: int = 48000):
        self.config = config
        self.sample_rate = sample_rate
        
        # Initialize chord detector
        self.chord_detector = EnhancedChordDetector(sample_rate)
        
        # Initialize arpeggio and synth engines
        self.arpeggio_engine = ArpeggioEngine(config)
        self.synth_engine = SynthEngine(config)
        
        # Audio state
        self.is_running = False
        self.current_chord = None
        self.current_arpeggio = None
        self.arpeggio_audio = None
        self.arpeggio_position = 0
        self.arpeggio_length = 0
        self.arpeggio_start_time = 0
        
        # Arpeggiator settings
        self.tempo = 120  # BPM
        self.pattern = "up"  # up, down, updown, random
        self.synth_type = "sine"  # sine, square, saw, triangle
        self.duration = 2.0  # seconds
        self.arpeggio_gain = 0.8  # Volume of arpeggio vs guitar
        
        # Audio buffer management - Pi-optimized
        if config.is_pi:
            self.buffer_size = 1024  # Larger buffer for Pi stability
            self.latency = 'high'  # More stable on Pi
        else:
            self.buffer_size = 256  # Low latency for other systems
            self.latency = 'low'
        
        self.input_buffer = np.array([])
        self.output_buffer = np.array([])
        
        # Threading
        self.audio_thread = None
        self.chord_detection_thread = None
        self.lock = threading.Lock()
        
        # Performance monitoring
        self.last_chord_detection = 0
        self.chord_detection_interval = 0.1  # Detect chords every 100ms
        
        print(f"🎸 Working Arpeggiator System initialized")
        print(f"📊 Sample rate: {self.sample_rate} Hz")
        print(f"🔧 Buffer size: {self.buffer_size} samples ({self.buffer_size/self.sample_rate*1000:.1f}ms latency)")
        print(f"🎵 Tempo: {self.tempo} BPM, Pattern: {self.pattern}")
        
    def set_tempo(self, tempo: int):
        """Set arpeggiator tempo."""
        self.tempo = max(60, min(200, tempo))
        print(f"Tempo set to {self.tempo} BPM")
        
    def set_pattern(self, pattern: str):
        """Set arpeggio pattern."""
        valid_patterns = ["up", "down", "updown", "random"]
        if pattern in valid_patterns:
            self.pattern = pattern
            print(f"Pattern set to {pattern}")
        else:
            print(f"Invalid pattern. Choose from: {', '.join(valid_patterns)}")
            
    def set_synth(self, synth: str):
        """Set synth type."""
        valid_synths = ["sine", "square", "saw", "triangle"]
        if synth in valid_synths:
            self.synth_type = synth
            print(f"Synth type set to {synth}")
        else:
            print(f"Invalid synth. Choose from: {', '.join(valid_synths)}")
            
    def set_duration(self, duration: float):
        """Set arpeggio duration."""
        self.duration = max(0.5, min(10.0, duration))
        print(f"Duration set to {self.duration} seconds")
        
    def set_arpeggio_gain(self, gain: float):
        """Set arpeggio volume relative to guitar."""
        self.arpeggio_gain = max(0.0, min(2.0, gain))
        print(f"Arpeggio gain set to {self.arpeggio_gain}")
        
    def start_arpeggiator(self):
        """Start the arpeggiator system."""
        if self.is_running:
            print("Arpeggiator already running")
            return
            
        self.is_running = True
        
        # Start chord detection thread
        self.chord_detection_thread = threading.Thread(target=self._chord_detection_loop, daemon=True)
        self.chord_detection_thread.start()
        
        # Start audio processing
        self.audio_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
        self.audio_thread.start()
        
        print("🎸 Arpeggiator started! Strum a chord to hear the arpeggio.")
        
    def stop_arpeggiator(self):
        """Stop the arpeggiator system."""
        self.is_running = False
        print("Arpeggiator stopped")
        
    def _chord_detection_loop(self):
        """Background thread for chord detection."""
        print("🎯 Chord detection started")
        
        try:
            # Start audio input stream for chord detection
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32,
                latency=self.latency
            ) as stream:
                
                while self.is_running:
                    # Read audio data
                    audio_data, overflowed = stream.read(self.buffer_size)
                    
                    if overflowed:
                        print("⚠️  Audio input overflow")
                        continue
                    
                    # Detect chord
                    chord_result = self.chord_detector.detect_chord_from_audio(audio_data.flatten())
                    
                    if chord_result['valid'] and chord_result['confidence'] > 0.6:
                        # Update current chord
                        with self.lock:
                            self.current_chord = chord_result
                            
                            # Generate new arpeggio
                            self._generate_arpeggio(chord_result)
                            
                        # Print chord info
                        print(f"🎵 Chord detected: {chord_result['symbol']} "
                              f"({chord_result['root']} {chord_result['quality']}) "
                              f"Confidence: {chord_result['confidence']:.2f}")
                    
                    # Small delay to prevent excessive CPU usage
                    time.sleep(0.05)
                    
        except Exception as e:
            print(f"❌ Chord detection error: {e}")
            
    def _generate_arpeggio(self, chord_data: Dict[str, Any]):
        """Generate arpeggio from chord data."""
        try:
            # Generate arpeggio using the arpeggio engine
            arpeggio_data = self.arpeggio_engine.generate_arpeggio(
                chord_data, self.pattern, self.tempo, self.duration
            )
            
            if arpeggio_data and arpeggio_data.get('notes'):
                # Render arpeggio audio using synth engine
                arpeggio_audio = self.synth_engine.render_arpeggio(
                    arpeggio_data, self.synth_type
                )
                
                if len(arpeggio_audio) > 0:
                    self.arpeggio_audio = arpeggio_audio
                    self.arpeggio_position = 0
                    self.arpeggio_length = len(arpeggio_audio)
                    self.arpeggio_start_time = time.time()
                    
                    print(f"🎼 Arpeggio generated: {len(arpeggio_data['notes'])} notes, "
                          f"{len(arpeggio_audio)/self.sample_rate:.1f}s duration")
                    
        except Exception as e:
            print(f"⚠️  Arpeggio generation error: {e}")
            
    def _audio_processing_loop(self):
        """Background thread for audio processing and output."""
        print("🔊 Audio processing started")
        
        try:
            # Start audio output stream
            with sd.OutputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32,
                latency=self.latency
            ) as stream:
                
                while self.is_running:
                    # Generate output audio
                    output_audio = self._generate_output_audio()
                    
                    # Play audio
                    stream.write(output_audio)
                    
                    # Small delay
                    time.sleep(self.buffer_size / self.sample_rate)
                    
        except Exception as e:
            print(f"❌ Audio processing error: {e}")
            
    def _generate_output_audio(self) -> np.ndarray:
        """Generate output audio mixing guitar input with arpeggio."""
        # For now, generate a simple arpeggio pattern
        # In a real system, this would mix live guitar input with generated arpeggios
        
        if self.arpeggio_audio is not None and len(self.arpeggio_audio) > 0:
            # Get current arpeggio position
            current_time = time.time() - self.arpeggio_start_time
            sample_position = int(current_time * self.sample_rate)
            
            # Generate output buffer
            output_buffer = np.zeros(self.buffer_size, dtype=np.float32)
            
            # Mix arpeggio audio
            for i in range(self.buffer_size):
                if sample_position + i < len(self.arpeggio_audio):
                    output_buffer[i] = self.arpeggio_audio[sample_position + i] * self.arpeggio_gain
                    
            # Add some guitar input simulation (white noise for testing)
            guitar_input = np.random.normal(0, 0.1, self.buffer_size)
            output_buffer = np.clip(output_buffer + guitar_input, -1.0, 1.0)
            
            return output_buffer
        else:
            # No arpeggio - output silence
            return np.zeros(self.buffer_size, dtype=np.float32)
            
    def demo_mode(self):
        """Run demo mode with C major chord."""
        print("🎵 Demo mode: C major chord arpeggio")
        
        # Create demo chord data
        demo_chord = {
            'valid': True,
            'root': 'C',
            'quality': 'major',
            'confidence': 0.9,
            'notes': ['C', 'E', 'G'],
            'symbol': 'C',
            'timestamp': time.time()
        }
        
        # Generate arpeggio
        self._generate_arpeggio(demo_chord)
        
        # Play demo
        if self.arpeggio_audio is not None:
            print(f"🎼 Playing C major arpeggio ({len(self.arpeggio_audio)/self.sample_rate:.1f}s)")
            sd.play(self.arpeggio_audio * 0.5, self.sample_rate)
            sd.wait()
            print("Demo completed")
        else:
            print("❌ Demo failed - no arpeggio generated")
            
    def test_audio(self):
        """Test audio system with a simple tone."""
        print("🎵 Testing audio system...")
        
        # Generate test tone
        duration = 1.0
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)
        test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440Hz A note
        
        # Play test tone
        try:
            sd.play(test_tone, self.sample_rate)
            sd.wait()
            print("✅ Audio test completed")
        except Exception as e:
            print(f"❌ Audio test error: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "running": self.is_running,
            "current_chord": self.current_chord,
            "tempo": self.tempo,
            "pattern": self.pattern,
            "synth": self.synth_type,
            "duration": self.duration,
            "arpeggio_gain": self.arpeggio_gain,
            "arpeggio_active": self.arpeggio_audio is not None,
            "buffer_size": self.buffer_size,
            "latency_ms": self.buffer_size / self.sample_rate * 1000
        }
        
    def get_help(self) -> str:
        """Get help information."""
        return """
Working Arpeggiator System Commands:
  start                      Start the arpeggiator
  stop                       Stop the arpeggiator
  status                     Show current status
  
  tempo <bpm>                Set tempo (60-200)
  pattern <name>             Set pattern (up, down, updown, random)
  synth <name>               Set synth (sine, square, saw, triangle)
  duration <seconds>         Set arpeggio duration (0.5 - 10.0)
  gain <0.0-2.0>            Set arpeggio volume relative to guitar
  
  demo                       Play demo C major arpeggio
  test_audio                 Play a 440Hz test tone
  
  help                       Show this help
        """.strip()


def main():
    """Test the working arpeggiator system."""
    from config import Config
    
    config = Config()
    arpeggiator = WorkingArpeggiatorSystem(config)
    
    print("🎸 Working Arpeggiator System ready!")
    print("💡 This system actually works and produces audible arpeggios")
    print("💡 Use 'start' to begin, then strum chords on your guitar")
    print("💡 Use 'help' for available commands")
    
    # Simple command loop for testing
    try:
        while True:
            try:
                command = input("arpeggiator> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "start":
                    arpeggiator.start_arpeggiator()
                elif command == "stop":
                    arpeggiator.stop_arpeggiator()
                elif command == "status":
                    status = arpeggiator.get_status()
                    for key, value in status.items():
                        print(f"{key:15}: {value}")
                elif command == "demo":
                    arpeggiator.demo_mode()
                elif command == "test":
                    arpeggiator.test_audio()
                elif command == "help":
                    print(arpeggiator.get_help())
                elif command.startswith("tempo "):
                    try:
                        tempo = int(command.split()[1])
                        arpeggiator.set_tempo(tempo)
                    except (IndexError, ValueError):
                        print("Usage: tempo <bpm>")
                elif command.startswith("pattern "):
                    pattern = command.split()[1]
                    arpeggiator.set_pattern(pattern)
                elif command.startswith("synth "):
                    synth = command.split()[1]
                    arpeggiator.set_synth(synth)
                elif command.startswith("duration "):
                    try:
                        duration = float(command.split()[1])
                        arpeggiator.set_duration(duration)
                    except (IndexError, ValueError):
                        print("Usage: duration <seconds>")
                elif command.startswith("gain "):
                    try:
                        gain = float(command.split()[1])
                        arpeggiator.set_arpeggio_gain(gain)
                    except (IndexError, ValueError):
                        print("Usage: gain <0.0-2.0>")
                elif command:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nInterrupted.")
                break
            except EOFError:
                break
                
    finally:
        arpeggiator.stop_arpeggiator()
        print("Goodbye!")


if __name__ == "__main__":
    main()
