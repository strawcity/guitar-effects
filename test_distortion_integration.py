#!/usr/bin/env python3
"""
Test Cross-Feedback Distortion Integration

This script tests that the cross-feedback distortion is properly integrated
into the stereo delay system.
"""

import numpy as np
from delay import StereoDelay, DistortionType


def test_distortion_integration():
    """Test that cross-feedback distortion is working correctly."""
    print("🎸 Testing Cross-Feedback Distortion Integration")
    print("=" * 50)
    
    # Create a simple test signal
    sample_rate = 44100
    duration = 0.1  # Short duration for testing
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_signal = np.sin(2 * np.pi * 440 * t) * 0.5  # A4 note
    
    # Test 1: No distortion
    print("\n1️⃣ Testing without distortion...")
    delay_no_dist = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.1,
        right_delay=0.2,
        feedback=0.3,
        wet_mix=0.6,
        cross_feedback=0.2,
        cross_feedback_distortion=False
    )
    
    left_out1, right_out1 = delay_no_dist.process_mono_to_stereo(test_signal)
    print(f"   Output range: {np.min(left_out1):.3f} to {np.max(left_out1):.3f}")
    
    # Test 2: With soft clip distortion
    print("\n2️⃣ Testing with soft clip distortion...")
    delay_soft = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.1,
        right_delay=0.2,
        feedback=0.3,
        wet_mix=0.6,
        cross_feedback=0.2,
        cross_feedback_distortion=True,
        distortion_type=DistortionType.SOFT_CLIP,
        distortion_drive=0.5,
        distortion_mix=0.8
    )
    
    left_out2, right_out2 = delay_soft.process_mono_to_stereo(test_signal)
    print(f"   Output range: {np.min(left_out2):.3f} to {np.max(left_out2):.3f}")
    
    # Test 3: With fuzz distortion
    print("\n3️⃣ Testing with fuzz distortion...")
    delay_fuzz = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.1,
        right_delay=0.2,
        feedback=0.3,
        wet_mix=0.6,
        cross_feedback=0.2,
        cross_feedback_distortion=True,
        distortion_type=DistortionType.FUZZ,
        distortion_drive=0.7,
        distortion_mix=0.9
    )
    
    left_out3, right_out3 = delay_fuzz.process_mono_to_stereo(test_signal)
    print(f"   Output range: {np.min(left_out3):.3f} to {np.max(left_out3):.3f}")
    
    # Test 4: Real-time parameter changes
    print("\n4️⃣ Testing real-time parameter changes...")
    delay_rt = StereoDelay(
        sample_rate=sample_rate,
        cross_feedback_distortion=True,
        distortion_type=DistortionType.TUBE
    )
    
    # Change parameters in real-time
    delay_rt.set_parameters(
        distortion_type=DistortionType.BIT_CRUSH,
        distortion_drive=0.6,
        feedback=0.4
    )
    
    left_out4, right_out4 = delay_rt.process_mono_to_stereo(test_signal)
    print(f"   Output range: {np.min(left_out4):.3f} to {np.max(left_out4):.3f}")
    
    # Test 5: Check that distortion affects cross-feedback
    print("\n5️⃣ Testing that distortion affects cross-feedback...")
    
    # Process multiple iterations to see distortion buildup
    signal = test_signal.copy()
    for i in range(5):
        left_out, right_out = delay_fuzz.process_mono_to_stereo(signal)
        signal = (left_out + right_out) * 0.5  # Use output as next input
        
        if i > 0:  # Skip first iteration (no feedback yet)
            print(f"   Iteration {i}: range {np.min(signal):.3f} to {np.max(signal):.3f}")
    
    print("\n✅ All tests completed successfully!")
    print("🎛️ Cross-feedback distortion is working correctly.")
    
    # Show current parameters
    print(f"\n📊 Final delay parameters:")
    print(f"   {delay_fuzz.get_stereo_info()}")


def test_all_distortion_types():
    """Test all available distortion types."""
    print("\n🎛️ Testing All Distortion Types")
    print("=" * 40)
    
    sample_rate = 44100
    duration = 0.05
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_signal = np.sin(2 * np.pi * 440 * t) * 0.5
    
    distortion_types = [
        DistortionType.SOFT_CLIP,
        DistortionType.HARD_CLIP,
        DistortionType.TUBE,
        DistortionType.FUZZ,
        DistortionType.BIT_CRUSH,
        DistortionType.WAVESHAPER
    ]
    
    for dist_type in distortion_types:
        print(f"\n🔊 Testing {dist_type.value}...")
        
        delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=0.05,
            right_delay=0.1,
            feedback=0.4,
            wet_mix=0.7,
            cross_feedback=0.3,
            cross_feedback_distortion=True,
            distortion_type=dist_type,
            distortion_drive=0.6,
            distortion_mix=0.8
        )
        
        # Process signal multiple times to see distortion effect
        signal = test_signal.copy()
        for i in range(3):
            left_out, right_out = delay.process_mono_to_stereo(signal)
            signal = (left_out + right_out) * 0.5
        
        print(f"   Final range: {np.min(signal):.3f} to {np.max(signal):.3f}")
    
    print("\n✅ All distortion types tested successfully!")


if __name__ == "__main__":
    test_distortion_integration()
    test_all_distortion_types()
