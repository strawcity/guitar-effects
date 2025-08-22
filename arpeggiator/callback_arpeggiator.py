#!/usr/bin/env python3
"""
Callback-based Guitar Arpeggiator - Uses sounddevice callbacks for optimal performance
"""

import numpy as np
import sounddevice as sd
import time
import threading
from config import Config
from chord_detector import ChordDetector
from .arpeggio_engine import ArpeggioEngine
from .synth_engine import SynthEngine

class CallbackGuitarArpeggiator:
    def __init__(self):
        self.config = Config()
        self.chord_detector = ChordDetector(self.config)
        self.arpeggio_engine = ArpeggioEngine(self.config)
        self.synth_engine = SynthEngine(self.config)
        
        # Audio state
        self.is_running = False
        self.current_chord = None
        self.audio_stream = None
        
        # Settings
        self.tempo = 120
        self.pattern = 'up'
        self.synth_type = 'saw'
        self.duration = 2.0
        
        # Audio processing
        self.last_chord_time = 0
        self.chord_cooldown = 1.0  # Wait 1 second between chord detections
        self.audio_buffer = []
        self.buffer_size = 2048  # Accumulate audio before processing
        
        print("Callback Guitar Arpeggiator initialized!")
        print(f"Tempo: {self.tempo} BPM, Pattern: {self.pattern}, Synth: {self.synth_type}")
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback function - called by sounddevice for each audio chunk"""
        if status:
            print(f"Audio status: {status}")
        
        # Add input audio to buffer
        if indata is not None and len(indata) > 0:
            audio_chunk = indata.flatten().astype(np.float32)
            self.audio_buffer.extend(audio_chunk)
            
            # Process buffer when it's large enough
            if len(self.audio_buffer) >= self.buffer_size:
                self.process_audio_buffer()
                self.audio_buffer = []  # Clear buffer
        
        # Output silence (we're only processing input)
        if outdata is not None:
            outdata.fill(0)
    
    def process_audio_buffer(self):
        """Process accumulated audio buffer for chord detection"""
        try:
            # Convert buffer to numpy array
            audio_data = np.array(self.audio_buffer)
            
            # Check if audio is above silence threshold
            if np.max(np.abs(audio_data)) > 0.01:
                # Check cooldown to avoid processing too frequently
                current_time = time.time()
                if current_time - self.last_chord_time > self.chord_cooldown:
                    # Detect chord
                    chord_result = self.chord_detector.detect_chord(audio_data)
                    
                    # Process if valid chord detected
                    if chord_result['valid'] and chord_result['confidence'] > 0.6:
                        self.last_chord_time = current_time
                        self.current_chord = chord_result
                        
                        print(f"🎸 Detected: {chord_result['root']} {chord_result['quality']} "
                              f"(confidence: {chord_result['confidence']:.2f})")
                        
                        # Generate and play arpeggio in separate thread
                        threading.Thread(target=self.play_chord_arpeggio, 
                                      args=(chord_result,), daemon=True).start()
                        
        except Exception as e:
            print(f"Audio processing error: {e}")
    
    def start(self):
        """Start the arpeggiator using callback-based audio"""
        if self.is_running:
            print("Arpeggiator is already running!")
            return
        
        try:
            # Start audio stream with callback
            self.audio_stream = sd.Stream(
                channels=1,  # 1 input channel
                samplerate=self.config.sample_rate,
                blocksize=512,  # Small blocks for low latency
                dtype=np.float32,
                latency='low',
                callback=self.audio_callback
            )
            
            self.audio_stream.start()
            self.is_running = True
            
            print("Arpeggiator started! Press Ctrl+C to stop.")
            print("Play guitar chords to hear arpeggios!")
            
            # Keep main thread alive
            try:
                while self.is_running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop()
                
        except Exception as e:
            print(f"Failed to start audio stream: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the arpeggiator"""
        self.is_running = False
        
        if self.audio_stream and self.audio_stream.active:
            self.audio_stream.stop()
            self.audio_stream.close()
        
        print("\nArpeggiator stopped.")
    
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
    print("CALLBACK GUITAR ARPEGGIATOR")
    print("=" * 50)
    
    # Create arpeggiator
    arpeggiator = CallbackGuitarArpeggiator()
    
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
