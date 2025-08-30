#!/usr/bin/env python3
"""
Test script for Stereo Delay Effects

This script tests the stereo delay effect with various configurations
and parameters to ensure it's working correctly.
"""

import numpy as np
import time
from config import Config
from delay import StereoDelay

def test_stereo_delay_basic():
    """Test basic stereo delay functionality"""
    print("🧪 Testing Basic Stereo Delay...")
    
    config = Config()
    sample_rate = config.sample_rate
    
    # Create test signal
    duration = 0.1
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    # Create stereo delay
    stereo_delay = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.05,
        right_delay=0.1,
        feedback=0.3,
        wet_mix=0.6,
        ping_pong=True,
        stereo_width=0.5,
        cross_feedback=0.2
    )
    
    # Process test signal
    left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
    
    # Verify output
    assert len(left_out) == len(test_signal), "Left output length mismatch"
    assert len(right_out) == len(test_signal), "Right output length mismatch"
    assert np.max(np.abs(left_out)) > 0, "Left output has no signal"
    assert np.max(np.abs(right_out)) > 0, "Right output has no signal"
    
    # Check stereo separation
    stereo_separation = np.std(left_out - right_out)
    assert stereo_separation > 0, "No stereo separation detected"
    
    print(f"✅ Basic stereo delay test passed")
    print(f"📊 Stereo separation: {stereo_separation:.4f}")
    print(f"🎛️ {stereo_delay.get_info()}")

def test_stereo_delay_parameters():
    """Test stereo delay parameter adjustment"""
    print("\n🧪 Testing Stereo Delay Parameters...")
    
    sample_rate = 44100
    
    # Create stereo delay
    stereo_delay = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.3,
        right_delay=0.6,
        feedback=0.3,
        wet_mix=0.6,
        ping_pong=True,
        stereo_width=0.5,
        cross_feedback=0.2
    )
    
    # Test left delay adjustment
    stereo_delay.set_left_delay(0.4)
    assert stereo_delay.left_delay == 0.4, "Left delay not set correctly"
    print("✅ Left delay adjustment passed")
    
    # Test right delay adjustment
    stereo_delay.set_right_delay(0.8)
    assert stereo_delay.right_delay == 0.8, "Right delay not set correctly"
    print("✅ Right delay adjustment passed")
    
    # Test feedback adjustment
    stereo_delay.set_parameters(feedback=0.5)
    assert stereo_delay.feedback == 0.5, "Feedback not set correctly"
    print("✅ Feedback adjustment passed")
    
    # Test wet mix adjustment
    stereo_delay.set_parameters(wet_mix=0.8)
    assert stereo_delay.wet_mix == 0.8, "Wet mix not set correctly"
    print("✅ Wet mix adjustment passed")
    
    # Test stereo parameters
    stereo_delay.set_stereo_parameters(ping_pong=False, stereo_width=0.8, cross_feedback=0.3)
    assert stereo_delay.ping_pong == False, "Ping-pong not set correctly"
    assert stereo_delay.stereo_width == 0.8, "Stereo width not set correctly"
    assert stereo_delay.cross_feedback == 0.3, "Cross-feedback not set correctly"
    print("✅ Stereo parameters adjustment passed")

def test_stereo_delay_processing():
    """Test stereo delay audio processing methods"""
    print("\n🧪 Testing Stereo Delay Processing...")
    
    sample_rate = 44100
    
    # Create stereo delay
    stereo_delay = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.1,
        right_delay=0.2,
        feedback=0.3,
        wet_mix=0.6,
        ping_pong=True,
        stereo_width=0.5,
        cross_feedback=0.2
    )
    
    # Create test signal
    duration = 0.05
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Test mono to stereo processing
    left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
    
    # Verify output
    assert len(left_out) == len(test_signal), "Mono to stereo output length mismatch"
    assert len(right_out) == len(test_signal), "Mono to stereo output length mismatch"
    assert np.max(np.abs(left_out)) > 0, "Mono to stereo left output has no signal"
    assert np.max(np.abs(right_out)) > 0, "Mono to stereo right output has no signal"
    print("✅ Mono to stereo processing passed")
    
    # Test stereo processing
    left_in = test_signal * 0.8
    right_in = test_signal * 0.6
    left_out, right_out = stereo_delay.process_buffer(left_in, right_in)
    
    # Verify output
    assert len(left_out) == len(test_signal), "Stereo processing output length mismatch"
    assert len(right_out) == len(test_signal), "Stereo processing output length mismatch"
    assert np.max(np.abs(left_out)) > 0, "Stereo processing left output has no signal"
    assert np.max(np.abs(right_out)) > 0, "Stereo processing right output has no signal"
    print("✅ Stereo processing passed")

def test_stereo_delay_configurations():
    """Test different stereo delay configurations"""
    print("\n🧪 Testing Stereo Delay Configurations...")
    
    sample_rate = 44100
    
    # Create test signal
    duration = 0.05
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Test different configurations
    configs = [
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
        },
        {
            'name': 'Long Delay',
            'left_delay': 0.8,
            'right_delay': 1.2,
            'feedback': 0.6,
            'wet_mix': 0.8,
            'ping_pong': True,
            'stereo_width': 0.6,
            'cross_feedback': 0.4
        }
    ]
    
    for config_params in configs:
        print(f"  Testing {config_params['name']}...")
        
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
        left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
        
        # Verify output
        assert len(left_out) == len(test_signal), f"{config_params['name']} output length mismatch"
        assert len(right_out) == len(test_signal), f"{config_params['name']} output length mismatch"
        assert np.max(np.abs(left_out)) > 0, f"{config_params['name']} left output has no signal"
        assert np.max(np.abs(right_out)) > 0, f"{config_params['name']} right output has no signal"
        
        # Check stereo separation
        stereo_separation = np.std(left_out - right_out)
        print(f"    ✅ {config_params['name']} passed (separation: {stereo_separation:.4f})")

def main():
    """Run all stereo delay tests"""
    print("🎸 Stereo Delay Effects Test Suite")
    print("=" * 50)
    
    try:
        test_stereo_delay_basic()
        test_stereo_delay_parameters()
        test_stereo_delay_processing()
        test_stereo_delay_configurations()
        
        print("\n" + "=" * 50)
        print("🎉 All stereo delay tests passed!")
        print("✅ The stereo delay effect is working correctly")
        print("🎵 Ready for real-time audio processing")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
