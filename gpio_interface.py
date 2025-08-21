import time
import threading
from config import Config

class GPIOInterface:
    """GPIO interface for Raspberry Pi with fallback for other platforms"""
    
    def __init__(self, config):
        self.config = config
        self.gpio_available = config.gpio_available
        
        # GPIO state
        self.led_states = {}
        self.button_states = {}
        self.callbacks = {}
        
        # Initialize GPIO if available
        if self.gpio_available:
            self._init_gpio()
        else:
            print("⚠️  GPIO not available on this platform")
    
    def _init_gpio(self):
        """Initialize GPIO pins"""
        try:
            import RPi.GPIO as GPIO
            
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            # LEDs are no longer used
            
            # Setup button pins
            for button, pin in self.config.button_pins.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.FALLING, 
                                   callback=lambda pin, button=button: self._button_callback(button),
                                   bouncetime=300)
                self.button_states[button] = False
            
            # Setup audio interface pins
            for control, pin in self.config.audio_interface_pins.items():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            
            print("✅ GPIO initialized successfully")
            
        except ImportError:
            print("❌ RPi.GPIO not available - install with: pip install RPi.GPIO")
            self.gpio_available = False
        except Exception as e:
            print(f"❌ GPIO initialization failed: {e}")
            self.gpio_available = False
    
    def _button_callback(self, button):
        """Handle button press events"""
        if button in self.callbacks:
            try:
                self.callbacks[button]()
            except Exception as e:
                print(f"Button callback error: {e}")
    
    def register_button_callback(self, button, callback):
        """Register a callback for a button press"""
        if button in self.config.button_pins:
            self.callbacks[button] = callback
            print(f"✅ Registered callback for {button} button")
        else:
            print(f"❌ Button {button} not available")
    
    def set_led(self, note, state):
        """Deprecated: LEDs removed; no-op for compatibility"""
        return
    
    def flash_led(self, note, duration=0.1):
        """Deprecated: LEDs removed; no-op for compatibility"""
        return
    
    def flash_chord_leds(self, chord_notes, duration=0.5):
        """Deprecated: LEDs removed; no-op for compatibility"""
        return
    
    def set_volume_led(self, volume_level):
        """Deprecated: LEDs removed; no-op for compatibility"""
        return
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.gpio_available:
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
                print("✅ GPIO cleaned up")
            except Exception as e:
                print(f"GPIO cleanup error: {e}")
    
    def get_status(self):
        """Get current GPIO status"""
        return {
            'available': self.gpio_available,
            'led_states': self.led_states.copy(),
            'button_states': self.button_states.copy(),
            'registered_callbacks': list(self.callbacks.keys())
        }
    
    def simulate_button_press(self, button):
        """Simulate button press (for testing on non-Pi platforms)"""
        if button in self.callbacks:
            print(f"🔘 Simulating {button} button press")
            self.callbacks[button]()
        else:
            print(f"❌ No callback registered for {button} button")
    
    def simulate_led_control(self, note, state):
        """Deprecated: LEDs removed; no-op for compatibility"""
        return
