#!/usr/bin/env python3
"""
Test script for the Guitar Stereo Delay Effects System
This script tests the stereo delay system without requiring audio input/output
"""

import numpy as np
import time
from config import Config
from delay import StereoDelay
from gpio_interface import GPIOInterface

def test_config():
    """Test configuration system"""
    print("Testing Config...")
    config = Config()
    assert config.sample_rate == 48000
    assert config.chunk_size == 1024
    assert config.default_delay_time == 0.5
    assert config.default_feedback == 0.3
    assert config.default_wet_mix == 0.6
    print("✓ Config test passed")

def test_stereo_delay():
    """Test stereo delay effect"""
    print("Testing Stereo Delay Effect...")
    config = Config()
    
    # Create test audio signal
    sample_rate = config.sample_rate
    duration = 0.1
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    # Test Stereo Delay
    print("  Testing Stereo Delay...")
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
    
    left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    
    # Check stereo separation
    stereo_separation = np.std(left_out - right_out)
    assert stereo_separation > 0, "No stereo separation detected"
    
    print("    ✓ Stereo Delay passed")
    print(f"    📊 Stereo separation: {stereo_separation:.4f}")
    
    print("✓ Stereo delay effect test passed")

def test_stereo_delay_parameters():
    """Test stereo delay parameter adjustment"""
    print("Testing Stereo Delay Parameters...")
    
    # Test parameter adjustment
    stereo_delay = StereoDelay(
        sample_rate=44100,
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
    assert stereo_delay.left_delay == 0.4
    print("    ✓ Left delay adjustment passed")
    
    # Test right delay adjustment
    stereo_delay.set_right_delay(0.8)
    assert stereo_delay.right_delay == 0.8
    print("    ✓ Right delay adjustment passed")
    
    # Test feedback adjustment
    stereo_delay.set_parameters(feedback=0.5)
    assert stereo_delay.feedback == 0.5
    print("    ✓ Feedback adjustment passed")
    
    # Test wet mix adjustment
    stereo_delay.set_parameters(wet_mix=0.8)
    assert stereo_delay.wet_mix == 0.8
    print("    ✓ Wet mix adjustment passed")
    
    # Test stereo parameters
    stereo_delay.set_stereo_parameters(ping_pong=False, stereo_width=0.8, cross_feedback=0.3)
    assert stereo_delay.ping_pong == False
    assert stereo_delay.stereo_width == 0.8
    assert stereo_delay.cross_feedback == 0.3
    print("    ✓ Stereo parameters adjustment passed")
    
    print("✓ All stereo delay parameter tests passed")

def test_stereo_delay_processing():
    """Test stereo delay audio processing"""
    print("Testing Stereo Delay Processing...")
    
    # Create stereo delay
    stereo_delay = StereoDelay(
        sample_rate=44100,
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
    sample_rate = 44100
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Test mono to stereo processing
    left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
    
    # Verify output
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    
    # Test stereo processing
    left_in = test_signal * 0.8
    right_in = test_signal * 0.6
    left_out, right_out = stereo_delay.process_buffer(left_in, right_in)
    
    # Verify output
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    
    print("    ✓ Stereo delay processing passed")
    print("✓ All stereo delay processing tests passed")

def test_gpio_interface():
    """Test GPIO interface (if available)"""
    print("Testing GPIO Interface...")
    config = Config()
    gpio = GPIOInterface(config)
    
    if gpio.gpio_available:
        print("  GPIO available on this platform")
        print(f"  Button pins: {config.button_pins}")
        print("  ✓ GPIO interface test passed")
    else:
        print("  GPIO not available on this platform")
        print("  ✓ GPIO interface test passed (no GPIO available)")

def main():
    """Run all tests"""
    print("🎸 Guitar Stereo Delay Effects System Test")
    print("=" * 60)
    
    tests = [
        ("Config Test", test_config),
        ("Stereo Delay Test", test_stereo_delay),
        ("Stereo Delay Parameters Test", test_stereo_delay_parameters),
        ("Stereo Delay Processing Test", test_stereo_delay_processing),
        ("GPIO Interface Test", test_gpio_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The stereo delay system is ready.")
        print("🎵 Connect an audio input to start processing guitar with stereo delay effects!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
