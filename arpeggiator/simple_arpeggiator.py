#!/usr/bin/env python3
"""
Simplified Guitar Arpeggiator - Optimized for real-time performance
"""

import numpy as np
import sounddevice as sd
import time
import threading
from config import Config
from enhanced_chord_detector import EnhancedChordDetector
from .arpeggio_engine import ArpeggioEngine
from .synth_engine import SynthEngine

class SimpleGuitarArpeggiator:
    def __init__(self):
        self.config = Config()
        self.chord_detector = EnhancedChordDetector(self.config.sample_rate)
        self.arpeggio_engine = ArpeggioEngine(self.config)
        self.synth_engine = SynthEngine(self.config)
        
        # Audio state
        self.is_running = False
        self.current_chord = None
        self.audio_thread = None
        
        # Settings
        self.tempo = 120
        self.pattern = 'up'
        self.synth_type = 'saw'
        self.duration = 2.0
        
        # Audio processing
        self.last_chord_time = 0
        self.chord_cooldown = 1.0  # Wait 1 second between chord detections
        
        print("Simple Guitar Arpeggiator initialized!")
        print(f"Tempo: {self.tempo} BPM, Pattern: {self.pattern}, Synth: {self.synth_type}")
    
    def start(self):
        """Start the arpeggiator"""
        if self.is_running:
            print("Arpeggiator is already running!")
            return
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        print("Arpeggiator started! Press Ctrl+C to stop.")
        print("Play guitar chords to hear arpeggios!")
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the arpeggiator"""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        print("\nArpeggiator stopped.")
    
    def audio_loop(self):
        """Main audio processing loop - simplified for better performance"""
        try:
            # Use smaller buffer and lower latency
            with sd.InputStream(
                channels=1,
                samplerate=self.config.sample_rate,
                blocksize=512,  # Smaller buffer for lower latency
                dtype=np.float32,
                latency='low'
            ) as stream:
                print("Audio input stream opened successfully!")
                
                while self.is_running:
                    try:
                        # Read audio data
                        audio_data, overflowed = stream.read(512)
                        
                        if overflowed:
                            print("Buffer overflow - audio system overloaded")
                            time.sleep(0.1)  # Give system time to catch up
                            continue
                        
                        # Process audio if we have data
                        if audio_data is not None and len(audio_data) > 0:
                            # Convert to 1D array
                            audio_1d = audio_data.flatten().astype(np.float32)
                            
                            # Check if audio is above silence threshold
                            if np.max(np.abs(audio_1d)) > 0.01:  # Higher threshold for guitar
                                # Check cooldown to avoid processing too frequently
                                current_time = time.time()
                                if current_time - self.last_chord_time > self.chord_cooldown:
                                    # Detect chord
                                    chord_result = self.chord_detector.detect_chord_from_audio(audio_1d)
                                    
                                    # Process if valid chord detected
                                    if chord_result['valid'] and chord_result['confidence'] > 0.7:
                                        self.last_chord_time = current_time
                                        self.current_chord = chord_result
                                        
                                        print(f"🎸 Detected: {chord_result['root']} {chord_result['quality']} "
                                              f"(confidence: {chord_result['confidence']:.2f})")
                                        
                                        # Generate and play arpeggio
                                        self.play_chord_arpeggio(chord_result)
                        
                        # Small delay to prevent excessive CPU usage
                        time.sleep(0.02)  # 50 FPS processing
                        
                    except Exception as e:
                        print(f"Audio processing error: {e}")
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"Audio stream error: {e}")
            self.is_running = False
    
    def play_chord_arpeggio(self, chord):
        """Generate and play arpeggio for a detected chord"""
        try:
            # Generate arpeggio
            arpeggio = self.arpeggio_engine.generate_arpeggio(
                chord, self.pattern, self.tempo, self.duration
            )
            
            if arpeggio and arpeggio.get('notes'):
                # Render to audio
                audio_data = self.synth_engine.render_arpeggio(arpeggio, self.synth_type)
                
                if len(audio_data) > 0:
                    # Play the arpeggio
                    print(f"🎵 Playing {self.pattern} arpeggio...")
                    sd.play(audio_data, self.config.sample_rate)
                    sd.wait()
                    print("✅ Arpeggio completed")
                    
        except Exception as e:
            print(f"Arpeggio playback error: {e}")
    
    def set_tempo(self, tempo):
        """Set the tempo in BPM"""
        self.tempo = max(60, min(200, tempo))
        print(f"Tempo set to {self.tempo} BPM")
    
    def set_pattern(self, pattern):
        """Set the arpeggio pattern"""
        if pattern in self.arpeggio_engine.patterns:
            self.pattern = pattern
            print(f"Pattern set to: {pattern}")
        else:
            print(f"Invalid pattern: {pattern}")
            print(f"Available: {list(self.arpeggio_engine.patterns.keys())}")
    
    def set_synth(self, synth_type):
        """Set the synthesizer type"""
        if synth_type in self.synth_engine.synth_types:
            self.synth_type = synth_type
            print(f"Synth set to: {synth_type}")
        else:
            print(f"Invalid synth: {synth_type}")
            print(f"Available: {list(self.synth_engine.synth_types.keys())}")
    
    def demo(self):
        """Run demo with synthetic chord"""
        print("Running demo...")
        
        # Create demo chord
        demo_chord = {
            'root': 'C',
            'quality': 'major',
            'notes': ['C', 'E', 'G'],
            'note_details': [
                {'note': 'C', 'octave': 4, 'frequency': 261.63, 'strength': 1.0, 'cents_off': 0},
                {'note': 'E', 'octave': 4, 'frequency': 329.63, 'strength': 0.8, 'cents_off': 0},
                {'note': 'G', 'octave': 4, 'frequency': 392.00, 'strength': 0.9, 'cents_off': 0}
            ],
            'confidence': 0.95,
            'timestamp': time.time(),
            'valid': True
        }
        
        self.play_chord_arpeggio(demo_chord)
        print("Demo completed!")

def main():
    """Main entry point"""
    print("=" * 50)
    print("SIMPLE GUITAR ARPEGGIATOR")
    print("=" * 50)
    
    # Create arpeggiator
    arpeggiator = SimpleGuitarArpeggiator()
    
    # Configure settings
    arpeggiator.set_tempo(120)
    arpeggiator.set_pattern('up_down')
    arpeggiator.set_synth('saw')
    
    print("\nCommands:")
    print("  start() - Start live arpeggiator")
    print("  demo() - Run demo")
    print("  set_tempo(bpm) - Set tempo")
    print("  set_pattern(name) - Set pattern")
    print("  set_synth(type) - Set synth")
    print("  stop() - Stop system")
    
    # Run demo first
    arpeggiator.demo()
    
    # Start live system
    print("\nStarting live arpeggiator...")
    arpeggiator.start()

if __name__ == "__main__":
    main()
