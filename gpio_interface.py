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
            
            # Setup LED pins
            for note, pin in self.config.led_pins.items():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
                self.led_states[note] = False
            
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
        """Set LED state for a note"""
        if not self.gpio_available:
            return
        
        if note in self.config.led_pins:
            try:
                import RPi.GPIO as GPIO
                pin = self.config.led_pins[note]
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
                self.led_states[note] = state
            except Exception as e:
                print(f"LED control error: {e}")
    
    def flash_led(self, note, duration=0.1):
        """Flash LED briefly"""
        if not self.gpio_available:
            return
        
        self.set_led(note, True)
        time.sleep(duration)
        self.set_led(note, False)
    
    def flash_chord_leds(self, chord_notes, duration=0.5):
        """Flash LEDs for detected chord notes"""
        if not self.gpio_available:
            return
        
        # Flash all chord LEDs
        for note in chord_notes:
            if note in self.config.led_pins:
                self.set_led(note, True)
        
        time.sleep(duration)
        
        # Turn off all LEDs
        for note in chord_notes:
            if note in self.config.led_pins:
                self.set_led(note, False)
    
    def set_volume_led(self, volume_level):
        """Set volume indicator LED (if available)"""
        if not self.gpio_available or 'volume_up' not in self.config.audio_interface_pins:
            return
        
        try:
            import RPi.GPIO as GPIO
            
            # Simple volume indicator using available pins
            if volume_level > 0.7:
                GPIO.output(self.config.audio_interface_pins['volume_up'], GPIO.HIGH)
                GPIO.output(self.config.audio_interface_pins['volume_down'], GPIO.LOW)
            elif volume_level < 0.3:
                GPIO.output(self.config.audio_interface_pins['volume_up'], GPIO.LOW)
                GPIO.output(self.config.audio_interface_pins['volume_down'], GPIO.HIGH)
            else:
                GPIO.output(self.config.audio_interface_pins['volume_up'], GPIO.LOW)
                GPIO.output(self.config.audio_interface_pins['volume_down'], GPIO.LOW)
                
        except Exception as e:
            print(f"Volume LED control error: {e}")
    
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
        """Simulate LED control (for testing on non-Pi platforms)"""
        if note in self.config.led_pins:
            self.led_states[note] = state
            status = "ON" if state else "OFF"
            print(f"💡 Simulating LED {note}: {status}")
        else:
            print(f"❌ LED {note} not available")
