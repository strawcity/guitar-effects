#!/usr/bin/env python3
"""
Raspberry Pi Audio Stability Test with Stereo Delay

Tests different buffer sizes to find the optimal setting for your Pi setup.
This will help identify the minimum buffer size that works without underruns.
Now includes stereo delay effect processing.
"""

import sounddevice as sd
import numpy as np
import time
import threading
from delay import StereoDelay

class AudioStabilityTest:
    def __init__(self):
        self.sample_rate = 48000
        self.test_duration = 10  # seconds
        self.underrun_count = 0
        self.overflow_count = 0
        self.is_running = False
        
        # Initialize stereo delay effect
        self.stereo_delay = StereoDelay(
            sample_rate=self.sample_rate,
            left_delay=0.3,
            right_delay=0.6,
            feedback=0.3,
            wet_mix=0.6,
            ping_pong=True,
            stereo_width=0.5,
            cross_feedback=0.2
        )
        
    def test_buffer_size(self, buffer_size: int, latency_setting: str = 'high'):
        """Test a specific buffer size for stability."""
        print(f"\n🧪 Testing buffer size: {buffer_size} samples")
        print(f"📊 Latency: {buffer_size/self.sample_rate*1000:.1f}ms")
        print(f"⚙️  Setting: {latency_setting}")
        
        self.underrun_count = 0
        self.overflow_count = 0
        self.is_running = True
        
        def audio_callback(indata, outdata, frames, time, status):
            if status.input_underflow:
                self.underrun_count += 1
            if status.input_overflow:
                self.overflow_count += 1
            if status.output_underflow:
                self.underrun_count += 1
                
            # Process through stereo delay effect
            input_audio = indata[:, 0] if indata.ndim > 1 else indata
            
            # Get stereo output from delay
            left_out, right_out = self.stereo_delay.process_mono_to_stereo(input_audio)
            
            # Output stereo audio
            if outdata.ndim > 1:
                outdata[:, 0] = left_out[:frames]
                outdata[:, 1] = right_out[:frames]
            else:
                # Mono output - mix L+R
                outdata[:frames] = (left_out[:frames] + right_out[:frames]) * 0.5
            
        try:
            with sd.Stream(
                channels=(1, 2),  # Mono input, stereo output
                samplerate=self.sample_rate,
                blocksize=buffer_size,
                dtype=np.float32,
                latency=latency_setting,
                callback=audio_callback
            ) as stream:
                print(f"🎵 Stream started - listening for {self.test_duration} seconds...")
                print("💡 Play your guitar or make some noise to test stereo delay effect")
                
                # Run test
                start_time = time.time()
                while time.time() - start_time < self.test_duration and self.is_running:
                    time.sleep(0.1)
                    
                print(f"⏹️  Test completed")
                
        except Exception as e:
            print(f"❌ Stream error: {e}")
            return False
            
        # Report results
        if self.underrun_count == 0 and self.overflow_count == 0:
            print(f"✅ STABLE - No audio issues detected")
            return True
        else:
            print(f"❌ UNSTABLE - Underruns: {self.underrun_count}, Overflows: {self.overflow_count}")
            return False
    
    def find_optimal_buffer_size(self):
        """Find the optimal buffer size for this Pi."""
        print("🔍 FINDING OPTIMAL BUFFER SIZE FOR YOUR PI")
        print("=" * 60)
        
        # Test different buffer sizes (from small to large)
        buffer_sizes = [256, 512, 1024, 2048, 4096, 8192]
        
        optimal_size = None
        
        for buffer_size in buffer_sizes:
            if self.test_buffer_size(buffer_size, 'high'):
                optimal_size = buffer_size
                print(f"🎯 Found stable buffer size: {buffer_size}")
                break
            else:
                print(f"⚠️  Buffer size {buffer_size} is too small")
                
        if optimal_size:
            print(f"\n🎉 RECOMMENDATION: Use buffer size {optimal_size}")
            print(f"📊 This gives you {optimal_size/self.sample_rate*1000:.1f}ms latency")
            print(f"🔧 Update your config to use this buffer size")
        else:
            print(f"\n❌ No stable buffer size found - check your audio setup")
            print(f"💡 Try: python3 fix_pi_audio.py --fix")
            
        return optimal_size
    
    def test_current_settings(self):
        """Test with current audio settings."""
        print("🧪 TESTING CURRENT AUDIO SETTINGS")
        print("=" * 50)
        
        from config import Config
        config = Config()
        
        if config.is_pi:
            buffer_size = 2048  # Current Pi setting
        else:
            buffer_size = 256   # Current other systems setting
            
        print(f"💡 Testing current settings for your system")
        stable = self.test_buffer_size(buffer_size, 'high')
        
        if stable:
            print(f"\n✅ Current settings are stable!")
            print(f"💡 Your audio system should work without underruns")
        else:
            print(f"\n❌ Current settings are unstable")
            print(f"💡 Running full optimization test...")
            self.find_optimal_buffer_size()

def main():
    """Main test function."""
    print("🎸 RASPBERRY PI AUDIO STABILITY TEST WITH STEREO DELAY")
    print("=" * 60)
    print("This test will help find the best audio settings for your Pi")
    print("Make sure your Scarlett 2i2 is connected and working")
    print("Stereo delay effect will be active during testing")
    print()
    
    tester = AudioStabilityTest()
    
    try:
        # First test current settings
        tester.test_current_settings()
        
        print(f"\n" + "=" * 60)
        print("💡 TIPS FOR STABLE AUDIO:")
        print("1. Use a powered USB hub for your Scarlett 2i2")
        print("2. Ensure adequate power supply for your Pi")
        print("3. Close unnecessary programs")
        print("4. Use a fast SD card (Class 10+)")
        print("5. Run: python3 fix_pi_audio.py --fix")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
