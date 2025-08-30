import numpy as np
import sounddevice as sd
import time as time_module
import threading
from config import Config
from delay import StereoDelay
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
        
        # Stereo delay effect
        self.stereo_delay = None
        
        # Default stereo delay settings
        self.left_delay = 0.3
        self.right_delay = 0.6
        self.feedback = 0.3
        self.wet_mix = 0.6
        self.ping_pong = True
        self.stereo_width = 0.5
        self.cross_feedback = 0.2
        
        # Auto-detect audio devices
        self.input_device = None
        self.output_device = None
        
        print("🎸 Guitar Stereo Delay Effects System initialized!")
        print(f"Left delay: {self.left_delay}s")
        print(f"Right delay: {self.right_delay}s")
        print(f"Feedback: {self.feedback}")
        print(f"Wet mix: {self.wet_mix}")
        print("🎛️ Professional-quality stereo delay for guitar processing")
        print("🎵 Real-time audio processing with ultra-low latency")
        
        # Auto-detect and configure audio devices
        self.detect_audio_devices()
        
        # Setup GPIO button callbacks
        self.setup_gpio_callbacks()
        
        # Initialize stereo delay effect
        self.initialize_stereo_delay()
    
    def setup_gpio_callbacks(self):
        """Setup GPIO button callbacks for Pi control"""
        if self.gpio.gpio_available:
            self.gpio.register_button_callback('start', self.start)
            self.gpio.register_button_callback('stop', self.stop)
            self.gpio.register_button_callback('tempo_up', lambda: self.adjust_delay_times(0.1))
            self.gpio.register_button_callback('tempo_down', lambda: self.adjust_delay_times(-0.1))
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
    
    def initialize_stereo_delay(self):
        """Initialize the stereo delay effect"""
        self.stereo_delay = StereoDelay(
            sample_rate=self.config.sample_rate,
            left_delay=self.left_delay,
            right_delay=self.right_delay,
            feedback=self.feedback,
            wet_mix=self.wet_mix,
            ping_pong=self.ping_pong,
            stereo_width=self.stereo_width,
            cross_feedback=self.cross_feedback
        )
        print(f"✅ Stereo delay initialized: {self.stereo_delay.get_info()}")
    
    def adjust_delay_times(self, delta):
        """Adjust both delay times by delta seconds"""
        self.left_delay = max(0.1, min(2.0, self.left_delay + delta))
        self.right_delay = max(0.1, min(2.0, self.right_delay + delta))
        if self.stereo_delay:
            self.stereo_delay.set_left_delay(self.left_delay)
            self.stereo_delay.set_right_delay(self.right_delay)
        print(f"🎛️ Left delay: {self.left_delay:.2f}s, Right delay: {self.right_delay:.2f}s")
    
    def adjust_feedback(self, delta):
        """Adjust feedback by delta"""
        self.feedback = max(0.0, min(0.9, self.feedback + delta))
        if self.stereo_delay:
            self.stereo_delay.set_parameters(feedback=self.feedback)
        print(f"🎛️ Feedback: {self.feedback:.2f}")
    
    def adjust_wet_mix(self, delta):
        """Adjust wet mix by delta"""
        self.wet_mix = max(0.0, min(1.0, self.wet_mix + delta))
        if self.stereo_delay:
            self.stereo_delay.set_parameters(wet_mix=self.wet_mix)
        print(f"🎛️ Wet mix: {self.wet_mix:.2f}")
    
    def start(self):
        """Start the stereo delay effects system"""
        if self.is_running:
            print("⚠️  System is already running")
            return
        
        self.is_running = True
        self.audio_thread = threading.Thread(target=self.audio_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        print("🎸 Stereo delay effects system started!")
    
    def stop(self):
        """Stop the stereo delay effects system"""
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        print("🛑 Stereo delay effects system stopped")
    
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
                    
                    # Process through stereo delay effect
                    if self.stereo_delay:
                        # Get stereo output from delay
                        left_out, right_out = self.stereo_delay.process_mono_to_stereo(audio_in.flatten())
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
    
    def get_status(self):
        """Get current system status"""
        status = {
            'running': self.is_running,
            'left_delay': self.left_delay,
            'right_delay': self.right_delay,
            'feedback': self.feedback,
            'wet_mix': self.wet_mix,
            'ping_pong': self.ping_pong,
            'stereo_width': self.stereo_width,
            'cross_feedback': self.cross_feedback,
            'input_device': self.input_device,
            'output_device': self.output_device
        }
        return status

def main():
    """Main entry point"""
    print("🎸 Guitar Stereo Delay Effects System")
    print("=" * 50)
    
    # Create and initialize the system
    system = GuitarDelayEffects()
    
    # Start the system immediately
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