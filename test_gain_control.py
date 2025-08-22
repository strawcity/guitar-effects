#!/usr/bin/env python3
"""
Test script for input gain control
Run this to test different gain settings and see their effect on audio levels
"""

import numpy as np
import sounddevice as sd
import time

def test_gain_control():
    """Test different gain settings and their effect on audio levels"""
    print("🎚️  Input Gain Control Test")
    print("=" * 40)
    
    # Test parameters
    sample_rate = 44100
    duration = 3  # seconds
    test_gains = [1.0, 2.0, 3.0, 5.0, 8.0]
    
    print("🎸 Please play a chord on your guitar during this test")
    print("📊 The script will show how different gain settings affect the signal")
    print()
    
    for gain in test_gains:
        print(f"🎚️  Testing gain: {gain}x")
        print("   Play a chord now...")
        
        # Record audio with current gain
        audio_data = sd.rec(int(duration * sample_rate), 
                           samplerate=sample_rate, 
                           channels=1, 
                           dtype=np.float32)
        
        # Wait for recording to complete
        sd.wait()
        
        # Apply gain
        gained_audio = audio_data.flatten() * gain
        gained_audio = np.clip(gained_audio, -1.0, 1.0)
        
        # Analyze levels
        raw_max = np.max(np.abs(audio_data))
        raw_avg = np.mean(np.abs(audio_data))
        gained_max = np.max(np.abs(gained_audio))
        gained_avg = np.mean(np.abs(gained_audio))
        
        # Create visual meters
        raw_meter = "█" * int(raw_max * 20) + "░" * (20 - int(raw_max * 20))
        gained_meter = "█" * int(gained_max * 20) + "░" * (20 - int(gained_max * 20))
        
        print(f"   Raw:     {raw_meter} | Max: {raw_max:.4f} | Avg: {raw_avg:.4f}")
        print(f"   Gained:  {gained_meter} | Max: {gained_max:.4f} | Avg: {gained_avg:.4f}")
        
        # Recommendation
        if gained_max < 0.3:
            print("   ⚠️  Signal too weak - increase gain")
        elif gained_max > 0.9:
            print("   ⚠️  Signal too strong - decrease gain")
        else:
            print("   ✅ Signal level good for detection")
        
        print()
        time.sleep(1)
    
    print("🎯 Gain Test Complete!")
    print("💡 Choose a gain setting that gives you:")
    print("   - Peak levels around 0.5-0.8")
    print("   - Good signal strength without clipping")
    print("   - Consistent levels across different playing dynamics")

if __name__ == "__main__":
    test_gain_control()
