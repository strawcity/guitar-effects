import numpy as np
import sounddevice as sd
import time as time_module
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
        self.tempo = 100  # Default to 100 BPM for consistent timing
        self.pattern = self.config.default_pattern
        self.synth_type = self.config.default_synth
        self.duration = 2.4  # Full measure at 100 BPM (4 beats × 0.6 seconds)
        
        # Auto-detect audio devices
        self.input_device = None
        self.output_device = None
        
        print("Guitar Arpeggiator initialized!")
        print(f"Default tempo: {self.tempo} BPM (full measure: {self.duration:.1f}s)")
        print(f"Default pattern: {self.pattern}")
        print(f"Default synth: {self.synth_type}")
        print("🎵 Arpeggios will play for full musical measures - no new chords until measure completes!")
        
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
        

        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        print("Arpeggiator started! Press Ctrl+C to stop.")
        
        try:
            while self.is_running:
                time_module.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the arpeggiator"""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        

        
        print("\nArpeggiator stopped.")
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback function - called by sounddevice for each audio chunk"""
        try:
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
                    # Show meter and measure progress
                    measure_progress = ""
                    if hasattr(self, 'arpeggio_start_time') and hasattr(self, 'arpeggio_audio') and self.arpeggio_audio is not None:
                        current_time = time_module.time()
                        measure_duration = 60.0 / self.tempo * 4  # 4 beats per measure
                        elapsed = current_time - self.arpeggio_start_time
                        if elapsed < measure_duration:
                            progress = elapsed / measure_duration
                            measure_progress = f" | Measure: {progress:.1%}"
                    
                    print(f"\r🎤 Input: {meter} | Max: {max_level:.4f} | Avg: {avg_level:.4f} | Threshold: 0.0100 | Frames: {frames}{measure_progress}", end="", flush=True)
                
                # Only process if we have valid audio data and above threshold
                if max_level > 0.01:  # Higher threshold for guitar
                    current_time = time_module.time()
                    
                    # Check if we can start a new arpeggio
                    can_start_new = False
                    
                    if not hasattr(self, 'arpeggio_start_time'):
                        # First time, can start immediately
                        can_start_new = True
                    elif not hasattr(self, 'arpeggio_audio') or self.arpeggio_audio is None:
                        # No arpeggio currently playing, can start new one
                        can_start_new = True
                    else:
                        # Check if current arpeggio has finished its measure
                        measure_duration = 60.0 / self.tempo * 4  # 4 beats per measure
                        if current_time - self.arpeggio_start_time >= measure_duration:
                            can_start_new = True
                    
                    if can_start_new:
                        # Detect chord with detailed debugging
                        chord_result = self.chord_detector.detect_chord(audio_data)
                        
                        # Always show the raw detection results for debugging
                        if chord_result['valid']:
                            print(f"\n🔍 Raw chord detection results:")
                            print(f"   Root: {chord_result['root']}")
                            print(f"   Quality: {chord_result['quality']}")
                            print(f"   Confidence: {chord_result['confidence']:.2f}")
                            
                                                    # Show the detected notes with enhanced info
                        if 'note_details' in chord_result:
                            print(f"   Detected notes:")
                            for note_info in chord_result['note_details']:
                                note = note_info.get('note', 'Unknown')
                                freq = note_info.get('frequency', 0)
                                strength = note_info.get('strength', 0)
                                cents_off = note_info.get('cents_off', 0)
                                guitar_string = note_info.get('guitar_string', {})
                                
                                # Format tuning status
                                if abs(cents_off) < 10:
                                    tuning_status = "✅ In tune"
                                elif abs(cents_off) < 25:
                                    tuning_status = "⚠️  Slightly off"
                                else:
                                    tuning_status = "❌ Out of tune"
                                
                                print(f"     {note}: {freq:.1f} Hz (strength: {strength:.2f}, cents: {cents_off:+.1f}) {tuning_status}")
                                
                                # Show guitar string info if available
                                if guitar_string and guitar_string.get('string'):
                                    expected = guitar_string.get('expected_freq', 0)
                                    diff = guitar_string.get('difference', 0)
                                    print(f"       Guitar: {guitar_string['string']} (expected: {expected:.1f} Hz, diff: {diff:.1f} Hz)")
                        
                        # Show the chord notes
                        if 'notes' in chord_result:
                            print(f"   Chord notes: {chord_result['notes']}")
                        
                        # Update current chord if valid and above confidence threshold
                        if chord_result['valid'] and chord_result['confidence'] > 0.6:
                            self.last_chord_time = current_time
                            self.current_chord = chord_result
                            print(f"🎸 ✅ Chord confirmed: {chord_result['root']} {chord_result['quality']}")
                            
                            # Generate arpeggio
                            self.current_arpeggio = self.arpeggio_engine.generate_arpeggio(
                                chord_result, self.pattern, self.tempo, self.duration
                            )
                            
                            # Play arpeggio in separate thread to avoid blocking
                            threading.Thread(target=self.play_arpeggio, daemon=True).start()
                        else:
                            print(f"⚠️  Chord detected but confidence too low ({chord_result.get('confidence', 0):.2f})")
                            if chord_result.get('valid'):
                                print(f"   Detected: {chord_result.get('root', 'Unknown')} {chord_result.get('quality', 'Unknown')}")
                
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
            
            # Output mixed audio: pass-through + arpeggio
            if outdata is not None:
                if indata is not None:
                    # Start with pass-through audio (guitar input)
                    # Handle different input shapes - ensure we get mono audio
                    if indata.ndim == 2:
                        # If input is 2D, take the first channel or average across channels
                        if indata.shape[1] == 1:
                            # Single channel, 2D format
                            input_audio = indata[:, 0]
                        else:
                            # Multiple channels, average them
                            input_audio = np.mean(indata, axis=1)
                    else:
                        # 1D input
                        input_audio = indata
                    
                    gain = 2.0  # Increase volume for better monitoring
                    # Ensure output is the right shape
                    if outdata.ndim == 2:
                        outdata[:, 0] = np.clip(input_audio * gain, -1.0, 1.0)
                    else:
                        outdata[:] = np.clip(input_audio * gain, -1.0, 1.0)
                else:
                    outdata.fill(0)
                
                # Mix in arpeggio audio if available
                if hasattr(self, 'arpeggio_audio') and self.arpeggio_audio is not None:
                    if hasattr(self, 'arpeggio_position') and hasattr(self, 'arpeggio_length'):
                        # Calculate how many samples to output
                        samples_to_output = min(frames, self.arpeggio_length - self.arpeggio_position)
                        
                        if samples_to_output > 0:
                            # Get the arpeggio audio for this frame
                            arpeggio_frame = self.arpeggio_audio[self.arpeggio_position:self.arpeggio_position + samples_to_output]
                            
                            # Mix with pass-through (arpeggio at 0.7 volume)
                            arpeggio_gain = 0.7
                            
                            # Ensure shapes match for mixing
                            if outdata.ndim == 2:
                                # 2D output
                                if len(arpeggio_frame) == frames:
                                    # Full frame
                                    outdata[:, 0] = np.clip(outdata[:, 0] + arpeggio_frame * arpeggio_gain, -1.0, 1.0)
                                else:
                                    # Partial frame (end of arpeggio)
                                    outdata[:samples_to_output, 0] = np.clip(outdata[:samples_to_output, 0] + arpeggio_frame * arpeggio_gain, -1.0, 1.0)
                            else:
                                # 1D output
                                if len(arpeggio_frame) == frames:
                                    # Full frame
                                    outdata[:] = np.clip(outdata + arpeggio_frame * arpeggio_gain, -1.0, 1.0)
                                else:
                                    # Partial frame (end of arpeggio)
                                    outdata[:samples_to_output] = np.clip(outdata[:samples_to_output] + arpeggio_frame * arpeggio_gain, -1.0, 1.0)
                            
                            # Update position
                            self.arpeggio_position += samples_to_output
                            
                            # Check if arpeggio is finished
                            if self.arpeggio_position >= self.arpeggio_length:
                                self.arpeggio_audio = None
                                self.arpeggio_position = 0
                                self.arpeggio_length = 0
                
        except Exception as e:
            # Catch any errors in the callback to prevent crashes
            print(f"\n⚠️  Audio callback error: {e}")
            if outdata is not None:
                outdata.fill(0)
    
    def audio_loop(self):
        """Main audio processing loop using callback-based approach"""
        try:
            # Use callback-based stream for better performance
            with sd.Stream(
                channels=(1, 1),  # Input and output for pass-through
                samplerate=self.config.sample_rate,
                blocksize=2048,  # Larger buffer for Pi stability
                dtype=np.float32,
                latency='high',  # Use high latency for stability
                callback=self.audio_callback,
                device=(self.input_device, self.output_device)  # Use auto-detected devices
            ) as stream:
                print("Audio stream opened successfully!")
                print("Audio pass-through enabled - you should hear your guitar!")
                
                # Keep the stream alive
                while self.is_running:
                    time_module.sleep(0.1)
                    
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
                # Store the arpeggio audio for output in the main callback
                self.arpeggio_audio = audio_data
                self.arpeggio_position = 0
                self.arpeggio_length = len(audio_data)
                self.arpeggio_start_time = time_module.time()  # Record when arpeggio started
                print(f"🎵 Arpeggio started: {len(audio_data)} samples, duration: {self.duration:.1f}s")
                
        except Exception as e:
            print(f"Playback error: {e}")
    

    

    
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
            'timestamp': time_module.time(),
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