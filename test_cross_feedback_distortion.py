#!/usr/bin/env python3
"""
Test Cross-Feedback Distortion Feature

This script demonstrates the new cross-feedback distortion feature in the
stereo delay effect. It shows how different distortion types affect the
cross-feedback signal and creates interesting musical feedback patterns.
"""

import numpy as np
import sounddevice as sd
import time
from delay.stereo_delay import StereoDelay
from delay.distortion import DistortionType


def generate_test_signal(duration: float = 2.0, sample_rate: int = 44100) -> np.ndarray:
    """Generate a test signal for demonstration."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a guitar-like signal with harmonics
    fundamental = 220  # A3
    signal = (np.sin(2 * np.pi * fundamental * t) * 0.5 +
              np.sin(2 * np.pi * fundamental * 2 * t) * 0.3 +
              np.sin(2 * np.pi * fundamental * 3 * t) * 0.2)
    
    # Add some noise for realism
    signal += np.random.normal(0, 0.01, len(signal))
    
    # Apply envelope
    envelope = np.exp(-t / duration)
    signal *= envelope
    
    return signal


def test_distortion_types():
    """Test different distortion types on cross-feedback."""
    sample_rate = 44100
    duration = 3.0
    
    print("🎸 Testing Cross-Feedback Distortion Types")
    print("=" * 50)
    
    # Generate test signal
    test_signal = generate_test_signal(duration, sample_rate)
    
    # Test different distortion types
    distortion_types = [
        DistortionType.NONE,
        DistortionType.SOFT_CLIP,
        DistortionType.HARD_CLIP,
        DistortionType.TUBE,
        DistortionType.FUZZ,
        DistortionType.BIT_CRUSH,
        DistortionType.WAVESHAPER
    ]
    
    for distortion_type in distortion_types:
        print(f"\n🔊 Testing {distortion_type.value.upper()} distortion...")
        
        # Create stereo delay with cross-feedback distortion
        delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=0.3,
            right_delay=0.6,
            feedback=0.4,
            wet_mix=0.7,
            ping_pong=True,
            stereo_width=0.5,
            cross_feedback=0.3,
            cross_feedback_distortion=True,
            distortion_type=distortion_type,
            distortion_drive=0.4,
            distortion_mix=0.8
        )
        
        # Process the signal
        left_output, right_output = delay.process_mono_to_stereo(test_signal)
        
        # Mix to mono for playback
        mono_output = (left_output + right_output) * 0.5
        
        # Normalize
        if np.max(np.abs(mono_output)) > 0:
            mono_output = mono_output / np.max(np.abs(mono_output)) * 0.8
        
        # Play the result
        print(f"Playing {distortion_type.value} distortion...")
        sd.play(mono_output, sample_rate)
        sd.wait()
        
        # Show parameters
        print(f"Parameters: {delay.get_stereo_info()}")
        
        time.sleep(0.5)  # Brief pause between tests


def test_distortion_parameters():
    """Test different distortion parameters."""
    sample_rate = 44100
    duration = 2.0
    
    print("\n🎛️ Testing Distortion Parameters")
    print("=" * 50)
    
    # Generate test signal
    test_signal = generate_test_signal(duration, sample_rate)
    
    # Test different drive levels
    drive_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for drive in drive_levels:
        print(f"\n🔥 Testing drive level: {drive*100:.0f}%")
        
        delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=0.4,
            right_delay=0.8,
            feedback=0.5,
            wet_mix=0.6,
            ping_pong=True,
            stereo_width=0.4,
            cross_feedback=0.25,
            cross_feedback_distortion=True,
            distortion_type=DistortionType.TUBE,
            distortion_drive=drive,
            distortion_mix=0.7
        )
        
        # Process the signal
        left_output, right_output = delay.process_mono_to_stereo(test_signal)
        mono_output = (left_output + right_output) * 0.5
        
        # Normalize
        if np.max(np.abs(mono_output)) > 0:
            mono_output = mono_output / np.max(np.abs(mono_output)) * 0.8
        
        # Play the result
        print(f"Playing with {drive*100:.0f}% drive...")
        sd.play(mono_output, sample_rate)
        sd.wait()
        
        time.sleep(0.3)


def test_feedback_intensity():
    """Test different feedback intensity levels."""
    sample_rate = 44100
    duration = 2.0
    
    print("\n🔄 Testing Feedback Intensity")
    print("=" * 50)
    
    # Generate test signal
    test_signal = generate_test_signal(duration, sample_rate)
    
    # Test different feedback intensity levels
    intensity_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for intensity in intensity_levels:
        print(f"\n💫 Testing feedback intensity: {intensity*100:.0f}%")
        
        delay = StereoDelay(
            sample_rate=sample_rate,
            left_delay=0.3,
            right_delay=0.6,
            feedback=0.4,
            wet_mix=0.7,
            ping_pong=True,
            stereo_width=0.5,
            cross_feedback=0.3,
            cross_feedback_distortion=True,
            distortion_type=DistortionType.FUZZ,
            distortion_drive=0.5,
            distortion_mix=0.8
        )
        
        # Set feedback intensity
        delay.set_cross_feedback_distortion(feedback_intensity=intensity)
        
        # Process the signal
        left_output, right_output = delay.process_mono_to_stereo(test_signal)
        mono_output = (left_output + right_output) * 0.5
        
        # Normalize
        if np.max(np.abs(mono_output)) > 0:
            mono_output = mono_output / np.max(np.abs(mono_output)) * 0.8
        
        # Play the result
        print(f"Playing with {intensity*100:.0f}% feedback intensity...")
        sd.play(mono_output, sample_rate)
        sd.wait()
        
        time.sleep(0.3)


def interactive_demo():
    """Interactive demonstration of cross-feedback distortion."""
    sample_rate = 44100
    duration = 1.5
    
    print("\n🎮 Interactive Cross-Feedback Distortion Demo")
    print("=" * 50)
    print("This demo will play a continuous loop with real-time parameter changes.")
    print("Press Ctrl+C to stop.")
    
    # Generate a longer test signal
    test_signal = generate_test_signal(duration, sample_rate)
    
    # Create delay with cross-feedback distortion
    delay = StereoDelay(
        sample_rate=sample_rate,
        left_delay=0.3,
        right_delay=0.6,
        feedback=0.4,
        wet_mix=0.7,
        ping_pong=True,
        stereo_width=0.5,
        cross_feedback=0.3,
        cross_feedback_distortion=True,
        distortion_type=DistortionType.SOFT_CLIP,
        distortion_drive=0.3,
        distortion_mix=0.7
    )
    
    try:
        while True:
            # Cycle through different distortion types
            distortion_types = [
                DistortionType.SOFT_CLIP,
                DistortionType.TUBE,
                DistortionType.FUZZ,
                DistortionType.BIT_CRUSH
            ]
            
            for distortion_type in distortion_types:
                print(f"\n🎸 Playing with {distortion_type.value} distortion...")
                
                # Set distortion type
                delay.set_cross_feedback_distortion(distortion_type=distortion_type)
                
                # Process and play
                left_output, right_output = delay.process_mono_to_stereo(test_signal)
                mono_output = (left_output + right_output) * 0.5
                
                # Normalize
                if np.max(np.abs(mono_output)) > 0:
                    mono_output = mono_output / np.max(np.abs(mono_output)) * 0.8
                
                sd.play(mono_output, sample_rate)
                sd.wait()
                
                # Gradually increase drive
                for drive in np.linspace(0.2, 0.8, 3):
                    delay.set_cross_feedback_distortion(drive=drive)
                    print(f"  Drive: {drive*100:.0f}%")
                    
                    left_output, right_output = delay.process_mono_to_stereo(test_signal)
                    mono_output = (left_output + right_output) * 0.5
                    
                    if np.max(np.abs(mono_output)) > 0:
                        mono_output = mono_output / np.max(np.abs(mono_output)) * 0.8
                    
                    sd.play(mono_output, sample_rate)
                    sd.wait()
                    
    except KeyboardInterrupt:
        print("\n\n🎵 Demo stopped. Thanks for listening!")


def main():
    """Main test function."""
    print("🎸 Cross-Feedback Distortion Test Suite")
    print("=" * 60)
    
    # Test different distortion types
    test_distortion_types()
    
    # Test different drive levels
    test_distortion_parameters()
    
    # Test different feedback intensity levels
    test_feedback_intensity()
    
    # Interactive demo
    interactive_demo()


if __name__ == "__main__":
    main()
