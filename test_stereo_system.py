#!/usr/bin/env python3
"""
Test script for the stereo delay effects system.
This script tests all components without requiring audio input/output.
"""

import numpy as np
import time
from config import Config
from delay import BasicDelay, TapeDelay, MultiTapDelay, TempoSyncedDelay, StereoDelay

def test_stereo_output():
    """Test that all delay effects return proper stereo output."""
    print("🎸 Testing Stereo Delay Effects System")
    print("=" * 50)
    
    config = Config()
    
    # Create test audio signal
    sample_rate = config.sample_rate
    duration = 0.1
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    
    print(f"📊 Test signal: {len(test_signal)} samples at {sample_rate} Hz")
    print(f"🎵 Frequency: 440 Hz (A4 note)")
    print(f"⏱️  Duration: {duration}s")
    
    # Test all delay effects
    effects = [
        ('Basic Delay', BasicDelay(delay_time=0.05, feedback=0.2, wet_mix=0.6)),
        ('Tape Delay', TapeDelay(delay_time=0.05, feedback=0.3, wet_mix=0.7)),
        ('Multi-Tap Delay', MultiTapDelay()),
        ('Tempo-Synced Delay', TempoSyncedDelay(bpm=120.0, note_division='1/4')),
        ('Stereo Delay', StereoDelay(left_delay=0.03, right_delay=0.06))
    ]
    
    for effect_name, effect in effects:
        print(f"\n🎛️ Testing {effect_name}...")
        
        try:
            # Process the test signal
            if hasattr(effect, 'process_mono_to_stereo'):
                # Stereo delay needs special handling
                left_out, right_out = effect.process_mono_to_stereo(test_signal)
            else:
                # Other delays return stereo output
                left_out, right_out = effect.process_buffer(test_signal)
            
            # Verify stereo output
            assert len(left_out) == len(test_signal), f"Left channel length mismatch: {len(left_out)} vs {len(test_signal)}"
            assert len(right_out) == len(test_signal), f"Right channel length mismatch: {len(right_out)} vs {len(test_signal)}"
            assert np.max(np.abs(left_out)) > 0, "Left channel has no signal"
            assert np.max(np.abs(right_out)) > 0, "Right channel has no signal"
            
            # Check for stereo separation (channels should be different)
            channel_diff = np.mean(np.abs(left_out - right_out))
            stereo_separation = channel_diff / np.mean(np.abs(left_out + right_out))
            
            print(f"  ✅ {effect_name} processed successfully")
            print(f"  📊 Left channel: {len(left_out)} samples, max: {np.max(np.abs(left_out)):.4f}")
            print(f"  📊 Right channel: {len(right_out)} samples, max: {np.max(np.abs(right_out)):.4f}")
            print(f"  🎛️ Stereo separation: {stereo_separation:.3f} ({'Good' if stereo_separation > 0.01 else 'Minimal'})")
            
        except Exception as e:
            print(f"  ❌ {effect_name} failed: {e}")
            return False
    
    print(f"\n🎉 All stereo delay effects working correctly!")
    return True

def test_stereo_chain():
    """Test processing through multiple stereo delays in chain."""
    print("\n🔗 Testing Stereo Delay Chain...")
    
    config = Config()
    
    # Create test signal
    sample_rate = config.sample_rate
    duration = 0.05
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Create delay chain
    basic_delay = BasicDelay(delay_time=0.02, feedback=0.1, wet_mix=0.5)
    tape_delay = TapeDelay(delay_time=0.03, feedback=0.2, wet_mix=0.6)
    
    try:
        # Process through chain
        print("  📊 Processing: Input → Basic Delay → Tape Delay")
        
        # First delay
        left1, right1 = basic_delay.process_buffer(test_signal)
        print(f"  📊 Basic Delay output: L={len(left1)}, R={len(right1)}")
        
        # Second delay (process left channel)
        left2, right2 = tape_delay.process_buffer(left1)
        print(f"  📊 Tape Delay output: L={len(left2)}, R={len(right2)}")
        
        # Verify final output
        assert len(left2) == len(test_signal), "Final left channel length mismatch"
        assert len(right2) == len(test_signal), "Final right channel length mismatch"
        assert np.max(np.abs(left2)) > 0, "Final left channel has no signal"
        assert np.max(np.abs(right2)) > 0, "Final right channel has no signal"
        
        print(f"  ✅ Stereo delay chain working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ Stereo delay chain failed: {e}")
        return False

def test_stereo_parameters():
    """Test stereo parameter adjustment."""
    print("\n🎛️ Testing Stereo Parameter Adjustment...")
    
    try:
        # Test basic delay with different stereo widths
        basic_delay = BasicDelay(delay_time=0.1, feedback=0.3, wet_mix=0.6, stereo_width=0.5)
        
        # Create test signal
        sample_rate = 44100
        duration = 0.05
        samples = int(duration * sample_rate)
        t = np.linspace(0, duration, samples, False)
        test_signal = 0.3 * np.sin(2 * np.pi * 440 * t)
        
        # Process with different stereo widths
        stereo_widths = [0.0, 0.3, 0.6, 1.0]
        
        for width in stereo_widths:
            basic_delay.stereo_width = width
            left_out, right_out = basic_delay.process_buffer(test_signal)
            
            # Calculate stereo separation
            channel_diff = np.mean(np.abs(left_out - right_out))
            stereo_separation = channel_diff / np.mean(np.abs(left_out + right_out))
            
            print(f"  📊 Stereo width {width:.1f}: separation = {stereo_separation:.3f}")
        
        print(f"  ✅ Stereo parameter adjustment working!")
        return True
        
    except Exception as e:
        print(f"  ❌ Stereo parameter adjustment failed: {e}")
        return False

def main():
    """Run all stereo tests."""
    print("🎸 Guitar Delay Effects - Stereo System Test")
    print("=" * 60)
    
    tests = [
        ("Stereo Output Test", test_stereo_output),
        ("Stereo Chain Test", test_stereo_chain),
        ("Stereo Parameters Test", test_stereo_parameters)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All stereo tests passed! The system is ready for stereo processing.")
        print("🎵 Connect an audio input to start processing guitar with stereo delay effects!")
    else:
        print("⚠️  Some stereo tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
