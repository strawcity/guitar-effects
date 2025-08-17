import platform
import os

class Config:
    def __init__(self):
        self.platform = platform.system()
        self.is_mac = self.platform == "Darwin"
        self.is_pi = self.platform == "Linux" and os.path.exists("/sys/firmware/devicetree/base/model")
        
        # Audio settings
        self.sample_rate = 48000
        self.chunk_size = 1024  # Further reduced to prevent buffer overflow
        self.input_device = None  # Will auto-detect Scarlett
        self.output_device = None
        
        # Detection settings
        self.min_chord_confidence = 0.6
        self.chord_hold_time = 0.5  # Seconds to hold chord detection
        
        # Arpeggio settings
        self.default_tempo = 120
        self.default_pattern = 'up'
        self.default_synth = 'saw'
        
        # GPIO settings (Pi only)
        self.gpio_available = self.is_pi
        self.led_pins = {'C': 12, 'E': 13, 'G': 16} if self.is_pi else {}
        
        print(f"Running on: {self.platform}")
        print(f"GPIO available: {self.gpio_available}")
