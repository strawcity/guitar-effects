import numpy as np
import sounddevice as sd
import time as time_module
import threading
from config import Config
from delay import BasicDelay, TapeDelay, MultiTapDelay, TempoSyncedDelay, StereoDelay
from gpio_interface import GPIOInterface

class GuitarDelayEffects:
    def __init__(self):
        self.config = Config()
        
        # Initialize GPIO interface
        self.gpio = GPIOInterface(self.config)
        
        # Audio state
        self.is_running = False
        self.audio_thread = None
        
        # Audio buffer management
        self.audio_buffer = []
        self.buffer_max_size = 5  # Maximum number of chunks to buffer
        
        # Delay effects
        self.current_delay = None
        self.delay_chain = []
        
        # Default delay settings
        self.delay_time = 0.5
        self.feedback = 0.3
        self.wet_mix = 0.6
        
        # Auto-detect audio devices
        self.input_device = None
        self.output_device = None
        
        print("🎸 Guitar Delay Effects System initialized!")
        print(f"Default delay time: {self.delay_time}s")
        print(f"Default feedback: {self.feedback}")
        print(f"Default wet mix: {self.wet_mix}")
        print("🎛️ Professional-quality delay effects for guitar processing")
        print("🎵 Real-time audio processing with ultra-low latency")
        
        # Auto-detect and configure audio devices
        self.detect_audio_devices()
        
        # Setup GPIO button callbacks
        self.setup_gpio_callbacks()
        
        # Initialize default delay effect
        self.set_delay_effect('basic')
    
    def setup_gpio_callbacks(self):
        """Setup GPIO button callbacks for Pi control"""
        if self.gpio.gpio_available:
            self.gpio.register_button_callback('start', self.start)
            self.gpio.register_button_callback('stop', self.stop)
            self.gpio.register_button_callback('tempo_up', lambda: self.adjust_delay_time(0.1))
            self.gpio.register_button_callback('tempo_down', lambda: self.adjust_delay_time(-0.1))
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
        """Find the best input device based on platform priorities"""
        for priority in priorities:
            for i, device in enumerate(devices):
                if (device['max_inputs'] > 0 and 
                    priority.lower() in device['name'].lower()):
                    print(f"✅ Found input device: {device['name']}")
                    return i
        
        # Fallback to default input
        default_input = sd.default.device[0]
        print(f"⚠️  Using default input device: {devices[default_input]['name']}")
        return default_input
    
    def _find_output_device(self, devices, priorities):
        """Find the best output device based on platform priorities"""
        for priority in priorities:
            for i, device in enumerate(devices):
                if (device['max_outputs'] > 0 and 
                    priority.lower() in device['name'].lower()):
                    print(f"✅ Found output device: {device['name']}")
                    return i
        
        # Fallback to default output
        default_output = sd.default.device[1]
        print(f"⚠️  Using default output device: {devices[default_output]['name']}")
        return default_output
    
    def set_delay_effect(self, effect_type):
        """Set the current delay effect type"""
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
        
        print(f"✅ Set delay effect to: {effect_type}")
    
    def adjust_delay_time(self, delta):
        """Adjust delay time by delta seconds"""
        self.delay_time = max(0.1, min(2.0, self.delay_time + delta))
        if self.current_delay:
            self.current_delay.set_parameters(delay_time=self.delay_time)
        print(f"🎛️ Delay time: {self.delay_time:.2f}s")
    
    def adjust_feedback(self, delta):
        """Adjust feedback by delta"""
        self.feedback = max(0.0, min(0.9, self.feedback + delta))
        if self.current_delay:
            self.current_delay.set_parameters(feedback=self.feedback)
        print(f"🎛️ Feedback: {self.feedback:.2f}")
    
    def adjust_wet_mix(self, delta):
        """Adjust wet mix by delta"""
        self.wet_mix = max(0.0, min(1.0, self.wet_mix + delta))
        if self.current_delay:
            self.current_delay.set_parameters(wet_mix=self.wet_mix)
        print(f"🎛️ Wet mix: {self.wet_mix:.2f}")
    
    def start(self):
        """Start the delay effects system"""
        if self.is_running:
            print("⚠️  System is already running")
            return
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        print("🎸 Delay effects system started!")
    
    def stop(self):
        """Stop the delay effects system"""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        print("🛑 Delay effects system stopped")
    
    def audio_loop(self):
        """Main audio processing loop"""
        try:
            with sd.Stream(
                device=(self.input_device, self.output_device),
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
    
    def demo_mode(self):
        """Run a demo of the delay effects"""
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
            self.set_delay_effect(effect)
            
            # Process the test signal
            if self.current_delay:
                try:
                    if effect == 'stereo':
                        # Stereo delay needs special handling
                        processed = self.current_delay.process_mono_to_stereo(test_signal)
                    elif effect == 'multi':
                        # Multi-tap delay returns stereo output
                        processed = self.current_delay.process_buffer(test_signal)
                    else:
                        # Other delays should be updated to return stereo
                        processed = self.current_delay.process_buffer(test_signal)
                        # Convert to stereo if needed
                        if not isinstance(processed, tuple):
                            processed = (processed, processed)  # Duplicate for stereo
                    print(f"✅ {effect} delay processed successfully")
                except Exception as e:
                    print(f"❌ {effect} delay processing failed: {e}")
            else:
                print(f"❌ Failed to create {effect} delay")
        
        print("\n🎵 Demo completed!")
    
    def get_status(self):
        """Get current system status"""
        status = {
            'running': self.is_running,
            'delay_type': type(self.current_delay).__name__ if self.current_delay else 'None',
            'delay_time': self.delay_time,
            'feedback': self.feedback,
            'wet_mix': self.wet_mix,
            'input_device': self.input_device,
            'output_device': self.output_device
        }
        return status

def main():
    """Main entry point"""
    print("🎸 Guitar Delay Effects System")
    print("=" * 50)
    
    # Create and initialize the system
    system = GuitarDelayEffects()
    
    # Run demo mode
    system.demo_mode()
    
    # Start the system
    system.start()
    
    try:
        # Keep the main thread alive
        while system.is_running:
            time_module.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        system.stop()

if __name__ == "__main__":
    main()