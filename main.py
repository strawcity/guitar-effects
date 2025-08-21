import numpy as np
import sounddevice as sd
import time
import threading
from config import Config
from chord_detector import ChordDetector
from arpeggio_engine import ArpeggioEngine
from synth_engine import SynthEngine
from gpio_interface import GPIOInterface

class GuitarArpeggiator:
    def __init__(self):
        self.config = Config()
        self.chord_detector = ChordDetector(self.config)
        self.arpeggio_engine = ArpeggioEngine(self.config)
        self.synth_engine = SynthEngine(self.config)
        
        # Initialize GPIO interface
        self.gpio = GPIOInterface(self.config)
        
        # Audio state
        self.is_running = False
        self.current_chord = None
        self.current_arpeggio = None
        self.audio_thread = None
        
        # Audio buffer management
        self.audio_buffer = []
        self.buffer_max_size = 5  # Maximum number of chunks to buffer
        
        # Settings
        self.tempo = self.config.default_tempo
        self.pattern = self.config.default_pattern
        self.synth_type = self.config.default_synth
        self.duration = 2.0
        
        # Auto-detect audio devices
        self.input_device = None
        self.output_device = None
        
        print("Guitar Arpeggiator initialized!")
        print(f"Default tempo: {self.tempo} BPM")
        print(f"Default pattern: {self.pattern}")
        print(f"Default synth: {self.synth_type}")
        
        # Auto-detect and configure audio devices
        self.detect_audio_devices()
        
        # Setup GPIO button callbacks
        self.setup_gpio_callbacks()
    
    def setup_gpio_callbacks(self):
        """Setup GPIO button callbacks for Pi control"""
        if self.gpio.gpio_available:
            self.gpio.register_button_callback('start', self.start)
            self.gpio.register_button_callback('stop', self.stop)
            self.gpio.register_button_callback('tempo_up', lambda: self.set_tempo(self.tempo + 10))
            self.gpio.register_button_callback('tempo_down', lambda: self.set_tempo(self.tempo - 10))
            print("✅ GPIO button callbacks registered")
    
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
        """Find input device based on platform-specific priorities"""
        # First try priority devices
        for priority in priorities:
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if priority.lower() in device_name:
                    # Check if device has input capability
                    if self._device_has_input(device):
                        print(f"✅ Found priority input device: {device['name']} (ID: {i})")
                        return i
        
        # Fallback to default input
        try:
            default_input = sd.query_devices(kind='input')
            print(f"⚠️  No priority input found, using default: {default_input['name']}")
            return default_input['index']
        except:
            print("⚠️  No input devices found")
            return None
    
    def _find_output_device(self, devices, priorities):
        """Find output device based on platform-specific priorities"""
        # First try priority devices
        for priority in priorities:
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if priority.lower() in device_name:
                    # Check if device has output capability
                    if self._device_has_output(device):
                        print(f"✅ Found priority output device: {device['name']} (ID: {i})")
                        return i
        
        # Fallback to default output
        try:
            default_output = sd.query_devices(kind='output')
            print(f"⚠️  No priority output found, using default: {default_output['name']}")
            return default_output['index']
        except:
            print("⚠️  No output devices found")
            return None
    
    def _device_has_input(self, device):
        """Check if device has input capability"""
        if 'max_inputs' in device:
            return device['max_inputs'] > 0
        elif 'inputs' in device:
            return device['inputs'] > 0
        elif 'hostapi' in device:
            return True
        return False
    
    def _device_has_output(self, device):
        """Check if device has output capability"""
        if 'max_outputs' in device:
            return device['max_outputs'] > 0
        elif 'outputs' in device:
            return device['outputs'] > 0
        elif 'hostapi' in device:
            return True
        return False
    
    def start(self):
        """Start the arpeggiator"""
        if self.is_running:
            print("Arpeggiator is already running!")
            return
        
        # Setup audio pass-through
        passthrough_ok = self.setup_audio_passthrough()
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        print("Arpeggiator started! Press Ctrl+C to stop.")
        
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
        
        # Stop audio pass-through
        self.stop_passthrough()
        
        print("\nArpeggiator stopped.")
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback function - called by sounddevice for each audio chunk"""
        # Handle platform-specific audio errors gracefully
        if status:
            if self.config.is_mac and ('err=-50' in str(status) or 'Unknown Error' in str(status)):
                # Ignore common macOS Core Audio errors
                pass
            elif self.config.is_pi and ('ALSA' in str(status) or 'PulseAudio' in str(status)):
                # Ignore common Pi audio errors
                pass
            else:
                print(f"\nAudio status: {status}")
        
        # Process input audio
        if indata is not None and len(indata) > 0:
            audio_data = indata.flatten().astype(np.float32)
            
            # Visual logging of audio levels
            max_level = np.max(np.abs(audio_data))
            avg_level = np.mean(np.abs(audio_data))
            
            # Create a visual meter (20 characters wide)
            meter_width = 20
            meter_fill = int((max_level * meter_width))
            meter_fill = min(meter_fill, meter_width)
            
            # Create the visual meter
            meter = "█" * meter_fill + "░" * (meter_width - meter_fill)
            
            # Show levels every 5th callback for more frequent updates
            if not hasattr(self, 'callback_count'):
                self.callback_count = 0
            self.callback_count += 1
            
            if self.callback_count % 5 == 0:  # Update every 5th callback
                # Clear line and show meter
                print(f"\r🎤 Input: {meter} | Max: {max_level:.4f} | Avg: {avg_level:.4f} | Threshold: 0.0100 | Frames: {frames}", end="", flush=True)
            
            # Only process if we have valid audio data and above threshold
            if max_level > 0.01:  # Higher threshold for guitar
                # Add cooldown to prevent excessive processing
                current_time = time.time()
                if not hasattr(self, 'last_chord_time') or current_time - getattr(self, 'last_chord_time', 0) > 1.0:
                    # Detect chord
                    chord_result = self.chord_detector.detect_chord(audio_data)
                    
                    # Update current chord if valid
                    if chord_result['valid'] and chord_result['confidence'] > 0.6:
                        self.last_chord_time = current_time
                        self.current_chord = chord_result
                        print(f"\n🎸 Detected: {chord_result['root']} {chord_result['quality']} "
                              f"(confidence: {chord_result['confidence']:.2f})")
                        
                        # LEDs removed: no visual chord feedback
                        
                        # Generate arpeggio
                        self.current_arpeggio = self.arpeggio_engine.generate_arpeggio(
                            chord_result, self.pattern, self.tempo, self.duration
                        )
                        
                        # Play arpeggio in separate thread to avoid blocking
                        threading.Thread(target=self.play_arpeggio, daemon=True).start()
            
            # Show when guitar signal is detected (even if not strong enough for chord detection)
            if max_level > 0.001:  # Lower threshold for signal detection
                if not hasattr(self, 'signal_detected'):
                    self.signal_detected = False
                
                if not self.signal_detected:
                    print(f"\n🎵 Guitar signal detected! Level: {max_level:.4f}")
                    self.signal_detected = True
            else:
                self.signal_detected = False
        else:
            # Debug: show when no input data
            if not hasattr(self, 'no_data_count'):
                self.no_data_count = 0
            self.no_data_count += 1
            if self.no_data_count % 50 == 0:  # Show every 50th occurrence
                print(f"\n⚠️  No input data received (count: {self.no_data_count})")
        
        # Output silence (we're only processing input)
        if outdata is not None:
            outdata.fill(0)
    
    def audio_loop(self):
        """Main audio processing loop using callback-based approach"""
        try:
            # Use callback-based stream for better performance
            with sd.Stream(
                channels=1,
                samplerate=self.config.sample_rate,
                blocksize=1024,  # Larger buffer for Scarlett 2i2
                dtype=np.float32,
                latency='high',  # Use high latency for stability
                callback=self.audio_callback,
                device=self.input_device  # Use auto-detected input device
            ) as stream:
                print("Audio input stream opened successfully!")
                print("Audio pass-through enabled - you should hear your guitar!")
                
                # Keep the stream alive
                while self.is_running:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Audio error: {e}")
            self.is_running = False
    
    def play_arpeggio(self):
        """Play the current arpeggio"""
        if not self.current_arpeggio or not self.current_arpeggio.get('notes'):
            return
        
        try:
            # Render arpeggio to audio
            audio_data = self.synth_engine.render_arpeggio(
                self.current_arpeggio, self.synth_type
            )
            
            if len(audio_data) > 0:
                # Play the audio
                sd.play(audio_data, self.config.sample_rate)
                sd.wait()  # Wait for playback to complete
                
        except Exception as e:
            print(f"Playback error: {e}")
    
    def setup_audio_passthrough(self):
        """Setup audio pass-through for monitoring guitar input"""
        try:
            # Create a duplex stream (input + output) for pass-through
            self.passthrough_stream = sd.Stream(
                channels=(1, 1),  # 1 input, 1 output
                samplerate=self.config.sample_rate,
                blocksize=1024,  # Match the main stream buffer size
                dtype=np.float32,
                latency='high',  # Use high latency for stability
                callback=self.passthrough_callback,
                device=(self.input_device, self.output_device)  # Use auto-detected devices
            )
            self.passthrough_stream.start()
            print("Audio pass-through enabled - you should hear your guitar!")
            return True
        except Exception as e:
            print(f"Could not setup audio pass-through: {e}")
            print("Continuing without pass-through...")
            return False
    
    def passthrough_callback(self, indata, outdata, frames, time, status):
        """Callback for audio pass-through - routes input directly to output"""
        if status:
            print(f"Pass-through status: {status}")
        
        # Route input directly to output with gain boost
        if indata is not None and outdata is not None:
            # Apply gain boost for monitoring
            gain = 2.0  # Increase volume for better monitoring
            outdata[:] = np.clip(indata * gain, -1.0, 1.0)
    
    def process_audio_passthrough(self, audio_data):
        """Process audio for pass-through - now handled by callback"""
        # This is now handled by the passthrough_callback
        pass
    
    def stop_passthrough(self):
        """Stop audio pass-through"""
        if hasattr(self, 'passthrough_stream') and self.passthrough_stream.active:
            self.passthrough_stream.stop()
            self.passthrough_stream.close()
            print("Audio pass-through stopped")
    
    def set_tempo(self, tempo):
        """Set the tempo in BPM"""
        self.tempo = max(60, min(200, tempo))  # Limit to 60-200 BPM
        print(f"Tempo set to {self.tempo} BPM")
    
    def set_pattern(self, pattern):
        """Set the arpeggio pattern"""
        if pattern in self.arpeggio_engine.patterns:
            self.pattern = pattern
            print(f"Pattern set to: {pattern}")
        else:
            print(f"Invalid pattern: {pattern}")
            print(f"Available patterns: {list(self.arpeggio_engine.patterns.keys())}")
    
    def set_synth(self, synth_type):
        """Set the synthesizer type"""
        if synth_type in self.synth_engine.synth_types:
            self.synth_type = synth_type
            print(f"Synth set to: {synth_type}")
        else:
            print(f"Invalid synth: {synth_type}")
            print(f"Available synths: {list(self.synth_engine.synth_types.keys())}")
    
    def set_duration(self, duration):
        """Set the arpeggio duration in seconds"""
        self.duration = max(0.5, min(10.0, duration))  # Limit to 0.5-10 seconds
        print(f"Duration set to {self.duration} seconds")
    
    def demo_mode(self):
        """Run in demo mode with pre-defined chord"""
        print("Running in demo mode...")
        
        # Create a demo C major chord
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
        
        self.current_chord = demo_chord
        
        # Generate and play arpeggio
        self.current_arpeggio = self.arpeggio_engine.generate_arpeggio(
            demo_chord, self.pattern, self.tempo, self.duration
        )
        
        self.play_arpeggio()
        print("Demo completed!")
    
    def test_audio_system(self):
        """Test the audio system with a simple tone"""
        print("🔊 Testing audio system...")
        
        try:
            # Generate a simple test tone
            sample_rate = self.config.sample_rate
            duration = 1.0  # 1 second
            frequency = 440.0  # A4 note
            
            # Generate sine wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            test_tone = np.sin(2 * np.pi * frequency * t) * 0.3  # 30% volume
            
            print("Playing test tone (440 Hz A note) - you should hear this!")
            sd.play(test_tone, sample_rate)
            sd.wait()
            print("✅ Test tone completed - if you heard it, audio output is working!")
            
        except Exception as e:
            print(f"❌ Audio test failed: {e}")

def main():
    """Main entry point"""
    print("=" * 50)
    print("GUITAR ARPEGGIATOR SYSTEM")
    print("=" * 50)
    
    # Create and configure arpeggiator
    arpeggiator = GuitarArpeggiator()
    
    # Set some initial parameters
    arpeggiator.set_tempo(120)
    arpeggiator.set_pattern('up_down')
    arpeggiator.set_synth('saw')
    arpeggiator.set_duration(2.0)
    
    print("\nAvailable commands:")
    print("  start() - Start the arpeggiator")
    print("  demo() - Run demo mode")
    print("  test_audio() - Test audio system with tone")
    print("  set_tempo(bpm) - Set tempo (60-200 BPM)")
    print("  set_pattern(name) - Set pattern")
    print("  set_synth(type) - Set synthesizer")
    print("  set_duration(seconds) - Set duration")
    print("  stop() - Stop the arpeggiator")
    
    print("\nAvailable patterns:", list(arpeggiator.arpeggio_engine.patterns.keys()))
    print("Available synths:", list(arpeggiator.synth_engine.synth_types.keys()))
    
    # Run demo first
    arpeggiator.demo_mode()
    
    # Start the main system
    print("\nStarting arpeggiator...")
    arpeggiator.start()

if __name__ == "__main__":
    main()