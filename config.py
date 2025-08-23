import platform
import os
import subprocess

class Config:
    def __init__(self):
        self.platform = platform.system()
        self.is_mac = self.platform == "Darwin"
        self.is_pi = self.platform == "Linux" and os.path.exists("/sys/firmware/devicetree/base/model")
        self.is_linux = self.platform == "Linux"
        
        # Detect Pi model if available
        self.pi_model = self._detect_pi_model()
        
        # Audio settings
        self.sample_rate = 48000
        self.chunk_size = 1024  # Further reduced to prevent buffer overflow
        self.input_device = None  # Will auto-detect Scarlett
        self.output_device = None
        
        # Platform-specific audio settings
        if self.is_mac:
            self.audio_backend = 'core_audio'
            self.default_latency = 'high'
            self.blocksize = 1024
        elif self.is_pi:
            self.audio_backend = 'alsa'
            self.default_latency = 'low'
            self.blocksize = 512  # Smaller buffer for Pi performance
        else:
            self.audio_backend = 'default'
            self.default_latency = 'high'
            self.blocksize = 1024
        
        # Detection settings
        self.min_chord_confidence = 0.6
        self.chord_hold_time = 0.5  # Seconds to hold chord detection
        
        # Arpeggio settings
        self.default_tempo = 120
        self.default_pattern = 'up'
        self.default_synth = 'saw'
        
        # GPIO settings (Pi only)
        self.gpio_available = self.is_pi
        # LEDs are no longer used; keep attribute as empty for compatibility
        self.led_pins = {}
        if self.is_pi:
            self.button_pins = {'start': 17, 'stop': 18, 'tempo_up': 22, 'tempo_down': 23}
            self.audio_interface_pins = {'mute': 24, 'volume_up': 25, 'volume_down': 26}
        else:
            self.button_pins = {}
            self.audio_interface_pins = {}
        
        # Pi-specific audio optimizations
        if self.is_pi:
            self.audio_optimizations = {
                'use_hardware_mixing': True,
                'buffer_size_multiplier': 2,  # Increase buffer for stability
                'cpu_governor': 'performance',  # Use performance CPU governor
                'audio_group': 'audio'  # Ensure user is in audio group
            }
        else:
            self.audio_optimizations = {}
        
        print(f"Running on: {self.platform}")
        if self.is_pi:
            print(f"Pi Model: {self.pi_model}")
        print(f"Audio Backend: {self.audio_backend}")
        print(f"GPIO available: {self.gpio_available}")
        
        # Apply Pi-specific optimizations
        if self.is_pi:
            self._apply_pi_optimizations()
    
    def _detect_pi_model(self):
        """Detect Raspberry Pi model"""
        if not self.is_pi:
            return None
        
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read().strip()
            return model
        except:
            return "Unknown Pi Model"
    
    def _apply_pi_optimizations(self):
        """Apply Raspberry Pi specific optimizations"""
        try:
            # Set CPU governor to performance for better audio performance
            if os.path.exists('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'):
                subprocess.run(['sudo', 'sh', '-c', 'echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'], 
                             capture_output=True, text=True)
            
            # Ensure user is in audio group
            subprocess.run(['sudo', 'usermod', '-a', '-G', 'audio', os.getenv('USER')], 
                         capture_output=True, text=True)
            
            # Set audio group permissions
            subprocess.run(['sudo', 'chmod', '666', '/dev/snd/*'], 
                         capture_output=True, text=True)
            
            print("✅ Applied Pi audio optimizations")
            
        except Exception as e:
            print(f"⚠️  Could not apply all Pi optimizations: {e}")
            print("   Some features may not work optimally")
    
    def get_audio_devices(self):
        """Get platform-specific audio device recommendations"""
        if self.is_mac:
            return {
                'input_priorities': ['Scarlett', 'Focusrite', '2i2', 'audio interface'],
                'output_priorities': ['speakers', 'headphones', 'MacBook', 'Air'],
                'fallback_input': 'default',
                'fallback_output': 'default'
            }
        elif self.is_pi:
            return {
                'input_priorities': ['Scarlett', '2i2', 'Focusrite', 'USB Audio', 'USB Audio Device'],
                'output_priorities': ['Scarlett', '2i2', 'Focusrite', 'USB Audio', 'USB Audio Device'],
                'fallback_input': 'default',
                'fallback_output': 'default'
            }
        else:
            return {
                'input_priorities': ['default'],
                'output_priorities': ['default'],
                'fallback_input': 'default',
                'fallback_output': 'default'
            }
    
    def get_audio_settings(self):
        """Get platform-specific audio settings"""
        return {
            'latency': self.default_latency,
            'blocksize': self.blocksize,
            'channels': 1,
            'dtype': 'float32',
            'samplerate': self.sample_rate
        }
