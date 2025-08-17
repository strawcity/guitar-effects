#!/usr/bin/env python3
"""
Headless Mode for Guitar Arpeggiator
Runs without screen, controlled by GPIO buttons and LEDs
"""

import time
import threading
import signal
import sys
from config import Config
from gpio_interface import GPIOInterface
from main import GuitarArpeggiator

class HeadlessArpeggiator:
    """Headless mode arpeggiator controlled by GPIO buttons"""
    
    def __init__(self):
        self.config = Config()
        self.gpio = GPIOInterface(self.config)
        self.arpeggiator = None
        self.is_running = False
        self.shutdown_requested = False
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize GPIO callbacks
        self._setup_gpio_callbacks()
        
        # Status tracking
        self.status_led_state = False
        self.status_thread = None
        
        print("🎸 Headless Guitar Arpeggiator initialized!")
        print("   Press START button to begin")
        print("   Press STOP button to stop")
        print("   Press TEMPO buttons to adjust")
        print("   Press Ctrl+C to shutdown")
    
    def _setup_gpio_callbacks(self):
        """Setup GPIO button callbacks"""
        if not self.gpio.gpio_available:
            print("⚠️  GPIO not available - running in simulation mode")
            return
        
        # Start/Stop button
        self.gpio.register_button_callback('start', self._start_arpeggiator)
        self.gpio.register_button_callback('stop', self._stop_arpeggiator)
        
        # Tempo control buttons
        self.gpio.register_button_callback('tempo_up', self._tempo_up)
        self.gpio.register_button_callback('tempo_down', self._tempo_down)
        
        print("✅ GPIO button callbacks registered")
    
    def _start_arpeggiator(self):
        """Start the arpeggiator"""
        if self.is_running:
            print("⚠️  Arpeggiator already running")
            return
        
        try:
            print("🚀 Starting arpeggiator...")
            
            # Create and start arpeggiator
            self.arpeggiator = GuitarArpeggiator()
            self.arpeggiator.start()
            
            self.is_running = True
            
            # Start status LED blinking
            self._start_status_led()
            
            # Flash all LEDs to indicate start
            self.gpio.flash_chord_leds(['C', 'E', 'G'], duration=1.0)
            
            print("✅ Arpeggiator started successfully!")
            
        except Exception as e:
            print(f"❌ Failed to start arpeggiator: {e}")
            self._flash_error_leds()
    
    def _stop_arpeggiator(self):
        """Stop the arpeggiator"""
        if not self.is_running:
            print("⚠️  Arpeggiator not running")
            return
        
        try:
            print("🛑 Stopping arpeggiator...")
            
            # Stop the arpeggiator
            if self.arpeggiator:
                self.arpeggiator.stop()
                self.arpeggiator = None
            
            self.is_running = False
            
            # Stop status LED
            self._stop_status_led()
            
            # Turn off all LEDs
            for note in ['C', 'E', 'G']:
                self.gpio.set_led(note, False)
            
            print("✅ Arpeggiator stopped")
            
        except Exception as e:
            print(f"❌ Error stopping arpeggiator: {e}")
    
    def _tempo_up(self):
        """Increase tempo"""
        if self.arpeggiator and self.is_running:
            current_tempo = self.arpeggiator.tempo
            new_tempo = min(200, current_tempo + 10)
            self.arpeggiator.set_tempo(new_tempo)
            
            # Flash tempo LED
            self.gpio.flash_led('C', duration=0.2)
            print(f"🎵 Tempo increased to {new_tempo} BPM")
    
    def _tempo_down(self):
        """Decrease tempo"""
        if self.arpeggiator and self.is_running:
            current_tempo = self.arpeggiator.tempo
            new_tempo = max(60, current_tempo - 10)
            self.arpeggiator.set_tempo(new_tempo)
            
            # Flash tempo LED
            self.gpio.flash_led('G', duration=0.2)
            print(f"🎵 Tempo decreased to {new_tempo} BPM")
    
    def _start_status_led(self):
        """Start blinking status LED"""
        if not self.gpio.gpio_available:
            return
        
        self.status_thread = threading.Thread(target=self._status_led_loop, daemon=True)
        self.status_thread.start()
    
    def _stop_status_led(self):
        """Stop blinking status LED"""
        self.status_thread = None
    
    def _status_led_loop(self):
        """Blink status LED to show system is running"""
        while self.status_thread and self.is_running:
            # Use the 'E' LED as a status indicator
            self.gpio.set_led('E', self.status_led_state)
            self.status_led_state = not self.status_led_state
            time.sleep(1.0)  # Blink every second
    
    def _flash_error_leds(self):
        """Flash all LEDs to indicate error"""
        if not self.gpio.gpio_available:
            return
        
        # Flash all LEDs rapidly 3 times
        for _ in range(3):
            for note in ['C', 'E', 'G']:
                self.gpio.set_led(note, True)
            time.sleep(0.2)
            for note in ['C', 'E', 'G']:
                self.gpio.set_led(note, False)
            time.sleep(0.2)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🔄 Received signal {signum}, shutting down...")
        self.shutdown_requested = True
        self._stop_arpeggiator()
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup GPIO and other resources"""
        print("🧹 Cleaning up...")
        
        if self.gpio.gpio_available:
            self.gpio.cleanup()
        
        print("✅ Cleanup complete")
    
    def run(self):
        """Main run loop - wait for button presses"""
        print("🎯 Waiting for button presses...")
        print("   System ready for headless operation")
        
        try:
            while not self.shutdown_requested:
                time.sleep(0.1)
                
                # Check if arpeggiator is still running
                if self.is_running and self.arpeggiator and not self.arpeggiator.is_running:
                    print("⚠️  Arpeggiator stopped unexpectedly")
                    self.is_running = False
                    self._stop_status_led()
                
        except KeyboardInterrupt:
            print("\n🔄 Keyboard interrupt received")
            self._stop_arpeggiator()
        finally:
            self._cleanup()

def main():
    """Main entry point for headless mode"""
    print("=" * 60)
    print("🎸 GUITAR ARPEGGIATOR - HEADLESS MODE")
    print("=" * 60)
    
    # Check if running on Pi
    config = Config()
    if not config.is_pi:
        print("⚠️  Headless mode is designed for Raspberry Pi")
        print("   Running in simulation mode...")
    
    # Create and run headless arpeggiator
    headless = HeadlessArpeggiator()
    headless.run()

if __name__ == "__main__":
    main()
