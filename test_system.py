#!/usr/bin/env python3
"""
Test script for the Guitar Delay Effects System
This script tests all components without requiring audio input/output
"""

import numpy as np
import time
from config import Config
from delay import BasicDelay, TapeDelay, MultiTapDelay, TempoSyncedDelay, StereoDelay
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

def test_delay_effects():
    """Test all delay effects"""
    print("Testing Delay Effects...")
    config = Config()
    
    # Create test audio signal
    sample_rate = config.sample_rate
    duration = 0.1
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    # Test Basic Delay
    print("  Testing Basic Delay...")
    basic_delay = BasicDelay(delay_time=0.1, feedback=0.3, wet_mix=0.6)
    left_out, right_out = basic_delay.process_buffer(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    print("    ✓ Basic Delay passed")
    
    # Test Tape Delay
    print("  Testing Tape Delay...")
    tape_delay = TapeDelay(delay_time=0.1, feedback=0.3, wet_mix=0.6)
    left_out, right_out = tape_delay.process_buffer(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    print("    ✓ Tape Delay passed")
    
    # Test Multi-Tap Delay
    print("  Testing Multi-Tap Delay...")
    multi_delay = MultiTapDelay()
    multi_delay.sync_taps_to_tempo(120.0, ['1/4', '1/2', '3/4'])
    left_out, right_out = multi_delay.process_buffer(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    print("    ✓ Multi-Tap Delay passed")
    
    # Test Tempo-Synced Delay
    print("  Testing Tempo-Synced Delay...")
    tempo_delay = TempoSyncedDelay(bpm=120.0, note_division='1/4', feedback=0.3, wet_mix=0.6)
    left_out, right_out = tempo_delay.process_buffer(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    print("    ✓ Tempo-Synced Delay passed")
    
    # Test Stereo Delay
    print("  Testing Stereo Delay...")
    stereo_delay = StereoDelay(left_delay=0.05, right_delay=0.1, feedback=0.3, wet_mix=0.6)
    left_out, right_out = stereo_delay.process_mono_to_stereo(test_signal)
    assert len(left_out) == len(test_signal)
    assert len(right_out) == len(test_signal)
    assert np.max(np.abs(left_out)) > 0
    assert np.max(np.abs(right_out)) > 0
    print("    ✓ Stereo Delay passed")
    
    print("✓ All delay effects tests passed")

def test_delay_parameters():
    """Test delay parameter adjustment"""
    print("Testing Delay Parameters...")
    
    # Test parameter adjustment
    delay = BasicDelay(delay_time=0.5, feedback=0.3, wet_mix=0.6)
    
    # Test delay time adjustment
    delay.set_parameters(delay_time=0.8)
    assert delay.delay_time == 0.8
    print("    ✓ Delay time adjustment passed")
    
    # Test feedback adjustment
    delay.set_parameters(feedback=0.5)
    assert delay.feedback == 0.5
    print("    ✓ Feedback adjustment passed")
    
    # Test wet mix adjustment
    delay.set_parameters(wet_mix=0.8)
    assert delay.wet_mix == 0.8
    print("    ✓ Wet mix adjustment passed")
    
    print("✓ Delay parameters test passed")

def test_gpio_interface():
    """Test GPIO interface (if available)"""
    print("Testing GPIO Interface...")
    config = Config()
    gpio = GPIOInterface(config)
    
    # Test GPIO availability detection
    if config.is_pi:
        print(f"  Running on Pi: {config.pi_model}")
        print(f"  GPIO available: {gpio.gpio_available}")
    else:
        print("  Not running on Pi - GPIO not available")
    
    # Test status method
    status = gpio.get_status()
    assert isinstance(status, dict)
    print("    ✓ GPIO status method passed")
    
    print("✓ GPIO interface test passed")

def test_audio_device_detection():
    """Test audio device detection"""
    print("Testing Audio Device Detection...")
    config = Config()
    
    # Test device priorities
    devices = config.get_audio_devices()
    assert 'input_priorities' in devices
    assert 'output_priorities' in devices
    assert isinstance(devices['input_priorities'], list)
    assert isinstance(devices['output_priorities'], list)
    
    print(f"  Input priorities: {devices['input_priorities']}")
    print(f"  Output priorities: {devices['output_priorities']}")
    print("✓ Audio device detection test passed")

def test_integration():
    """Test full system integration"""
    print("Testing System Integration...")
    
    config = Config()
    
    # Create test audio signal
    sample_rate = config.sample_rate
    duration = 0.1
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    # Test delay chain
    basic_delay = BasicDelay(delay_time=0.05, feedback=0.2, wet_mix=0.5)
    tape_delay = TapeDelay(delay_time=0.1, feedback=0.3, wet_mix=0.6)
    
    # Process through delay chain
    left1, right1 = basic_delay.process_buffer(test_signal)
    left2, right2 = tape_delay.process_buffer(left1)  # Process left channel
    
    print(f"  Pipeline: Input -> Basic Delay -> Tape Delay -> Output")
    print(f"  Input: {len(test_signal)} samples")
    print(f"  Basic Delay: {len(left1)} samples (stereo)")
    print(f"  Tape Delay: {len(left2)} samples (stereo)")
    
    assert len(left2) == len(test_signal)
    assert len(right2) == len(test_signal)
    assert np.max(np.abs(left2)) > 0
    assert np.max(np.abs(right2)) > 0
    
    print("✓ Integration test passed")

def main():
    """Run all tests"""
    print("=" * 60)
    print("GUITAR DELAY EFFECTS SYSTEM - COMPONENT TESTS")
    print("=" * 60)
    
    try:
        test_config()
        test_delay_effects()
        test_delay_parameters()
        test_gpio_interface()
        test_audio_device_detection()
        test_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("The Guitar Delay Effects System is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
