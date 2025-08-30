#!/usr/bin/env python3
"""
Test Stereo Delay System

Tests the stereo delay system with various configurations and parameters.
"""

import numpy as np
import sounddevice as sd
import time
from config import Config
from delay import StereoDelay

def test_stereo_delay_parameters():
    """Test stereo delay with different parameter combinations."""
    print("🧪 Testing Stereo Delay Parameters")
    print("=" * 50)
    
    config = Config()
    sample_rate = config.sample_rate
    
    # Test signal
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    # Test different parameter combinations
    test_configs = [
        {
            'name': 'Basic Stereo',
            'left_delay': 0.3,
            'right_delay': 0.6,
            'feedback': 0.3,
            'wet_mix': 0.6,
            'ping_pong': True,
            'stereo_width': 0.5,
            'cross_feedback': 0.2
        },
        {
            'name': 'Wide Stereo',
            'left_delay': 0.2,
            'right_delay': 0.8,
            'feedback': 0.4,
            'wet_mix': 0.7,
            'ping_pong': True,
            'stereo_width': 0.8,
            'cross_feedback': 0.3
        },
        {
            'name': 'Tight Stereo',
            'left_delay': 0.4,
            'right_delay': 0.5,
            'feedback': 0.2,
            'wet_mix': 0.5,
            'ping_pong': False,
            'stereo_width': 0.2,
            'cross_feedback': 0.1
        }
    ]
    
    for config_params in test_configs:
        print(f"\n🎛️ Testing: {config_params['name']}")
        
        # Create stereo delay with test parameters
        stereo_delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=config_params['left_delay'],
            right_delay=config_params['right_delay'],
            feedback=config_params['feedback'],
            wet_mix=config_params['wet_mix'],
            ping_pong=config_params['ping_pong'],
            stereo_width=config_params['stereo_width'],
            cross_feedback=config_params['cross_feedback']
        )
        
        # Process test signal
        try:
            left_output, right_output = stereo_delay.process_mono_to_stereo(test_signal)
            
            # Calculate stereo separation
            stereo_separation = np.std(left_output - right_output)
            
            print(f"✅ {config_params['name']} processed successfully")
            print(f"📊 Stereo separation: {stereo_separation:.4f}")
            print(f"🎛️ {stereo_delay.get_info()}")
            
        except Exception as e:
            print(f"❌ {config_params['name']} failed: {e}")

def test_stereo_delay_realtime():
    """Test stereo delay in real-time audio processing."""
    print("\n🎵 Testing Real-time Stereo Delay")
    print("=" * 50)
    
    config = Config()
    
    # Create stereo delay
    stereo_delay = StereoDelay(
        sample_rate=config.sample_rate,
        left_delay=0.3,
        right_delay=0.6,
        feedback=0.3,
        wet_mix=0.6,
        ping_pong=True,
        stereo_width=0.5,
        cross_feedback=0.2
    )
    
    def audio_callback(indata, outdata, frames, time, status):
        # Process through stereo delay
        input_audio = indata[:, 0] if indata.ndim > 1 else indata
        left_out, right_out = stereo_delay.process_mono_to_stereo(input_audio)
        
        # Output stereo
        if outdata.ndim > 1:
            outdata[:, 0] = left_out[:frames]
            outdata[:, 1] = right_out[:frames]
        else:
            # Mono output - mix L+R
            outdata[:frames] = (left_out[:frames] + right_out[:frames]) * 0.5
    
    try:
        with sd.Stream(
            channels=(1, 2),  # Mono input, stereo output
            samplerate=config.sample_rate,
            blocksize=config.chunk_size,
            dtype=np.float32,
            callback=audio_callback
        ) as stream:
            print("🎵 Real-time stereo delay active!")
            print("💡 Play your guitar or make some noise")
            print("⏹️  Press Ctrl+C to stop")
            
            # Run for 10 seconds
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n⏹️  Real-time test stopped")
    except Exception as e:
        print(f"❌ Real-time test error: {e}")

def main():
    """Main test function."""
    print("🎸 Stereo Delay System Test")
    print("=" * 50)
    
    # Test parameter combinations
    test_stereo_delay_parameters()
    
    # Test real-time processing
    test_stereo_delay_realtime()
    
    print("\n✅ All stereo delay tests completed!")

if __name__ == "__main__":
    main()
