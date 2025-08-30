
"""
Delay Effects Demo Script

This script demonstrates all the implemented delay effects with various
parameter settings and audio examples.
"""

import numpy as np
import time
from . import (BasicDelay, TapeDelay, MultiTapDelay, 
               TempoSyncedDelay, StereoDelay)


def generate_test_signal(duration: float = 2.0, sample_rate: int = 44100) -> np.ndarray:
    """Generate a test signal for demonstration."""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    
    # Mix of different frequencies
    signal = (0.3 * np.sin(2 * np.pi * 440 * t) +      # A4
              0.2 * np.sin(2 * np.pi * 880 * t) +      # A5
              0.1 * np.sin(2 * np.pi * 220 * t))       # A3
    
    # Add some percussive elements
    percussive = np.exp(-t * 10) * np.random.normal(0, 0.1, len(t))
    signal += percussive
    
    return signal


def demo_basic_delay():
    """Demonstrate the basic delay effect."""
    print("\n=== Basic Delay Demo ===")
    
    # Create basic delay
    delay = BasicDelay(sample_rate=44100, delay_time=0.5, feedback=0.3, wet_mix=0.6)
    
    # Generate test signal
    test_signal = generate_test_signal(2.0)
    
    # Process through delay
    processed = delay.process_buffer(test_signal)
    
    print(f"Effect: {delay.get_effect_name()}")
    print(f"Parameters: {delay.get_parameters()}")
    print(f"Info: {delay.get_info()}")
    
    # Demonstrate parameter changes
    print("\nChanging parameters...")
    delay.set_parameters(delay_time=0.3, feedback=0.5, wet_mix=0.8)
    print(f"New info: {delay.get_info()}")
    
    return delay, processed


def demo_tape_delay():
    """Demonstrate the tape delay effect."""
    print("\n=== Tape Delay Demo ===")
    
    # Create tape delay
    delay = TapeDelay(sample_rate=44100, delay_time=0.6, feedback=0.4, 
                      saturation=0.3, wow_rate=0.5, flutter_rate=8.0)
    
    # Generate test signal
    test_signal = generate_test_signal(2.0)
    
    # Process through delay
    processed = delay.process_buffer(test_signal)
    
    print(f"Effect: {delay.get_effect_name()}")
    print(f"Parameters: {delay.get_parameters()}")
    print(f"Info: {delay.get_info()}")
    
    # Demonstrate tape parameter changes
    print("\nChanging tape parameters...")
    delay.set_tape_parameters(saturation=0.6, wow_rate=1.0, tape_speed=1.5)
    print(f"New info: {delay.get_info()}")
    
    return delay, processed


def demo_multi_tap_delay():
    """Demonstrate the multi-tap delay effect."""
    print("\n=== Multi-Tap Delay Demo ===")
    
    # Create multi-tap delay
    delay = MultiTapDelay(sample_rate=44100, feedback=0.3, wet_mix=0.7)
    
    # Generate test signal
    test_signal = generate_test_signal(2.0)
    
    # Process through delay
    left_output, right_output = delay.process_buffer(test_signal)
    
    print(f"Effect: {delay.get_effect_name()}")
    print(f"Number of taps: {len(delay.taps)}")
    print(f"Tap info: {delay.get_tap_info()}")
    print(f"Info: {delay.get_info()}")
    
    # Demonstrate tempo sync
    print("\nSyncing to tempo...")
    delay.sync_taps_to_tempo(120.0, ['1/4', '1/2', '3/4'])
    print(f"New tap info: {delay.get_tap_info()}")
    
    return delay, left_output, right_output


def demo_tempo_synced_delay():
    """Demonstrate the tempo-synced delay effect."""
    print("\n=== Tempo-Synced Delay Demo ===")
    
    # Create tempo-synced delay
    delay = TempoSyncedDelay(sample_rate=44100, bpm=120.0, note_division='1/4',
                             feedback=0.4, wet_mix=0.6, swing=0.2, humanize=0.1)
    
    # Generate test signal
    test_signal = generate_test_signal(2.0)
    
    # Process through delay
    processed = delay.process_buffer(test_signal)
    
    print(f"Effect: {delay.get_effect_name()}")
    print(f"Musical info: {delay.get_musical_info()}")
    print(f"Available divisions: {delay.get_available_divisions()}")
    print(f"Info: {delay.get_info()}")
    
    # Demonstrate tempo changes
    print("\nChanging tempo...")
    delay.set_tempo(140.0)
    delay.set_note_division('1/8')
    print(f"New musical info: {delay.get_musical_info()}")
    
    return delay, processed


def demo_stereo_delay():
    """Demonstrate the stereo delay effect."""
    print("\n=== Stereo Delay Demo ===")
    
    # Create stereo delay
    delay = StereoDelay(sample_rate=44100, left_delay=0.3, right_delay=0.6,
                        feedback=0.4, wet_mix=0.7, ping_pong=True, 
                        stereo_width=0.5, cross_feedback=0.2)
    
    # Generate test signal
    test_signal = generate_test_signal(2.0)
    
    # Process through delay (mono to stereo)
    left_output, right_output = delay.process_mono_to_stereo(test_signal)
    
    print(f"Effect: {delay.get_effect_name()}")
    print(f"Stereo info: {delay.get_stereo_info()}")
    print(f"Parameters: {delay.get_parameters()}")
    print(f"Info: {delay.get_info()}")
    
    # Demonstrate stereo parameter changes
    print("\nChanging stereo parameters...")
    delay.set_stereo_parameters(ping_pong=False, stereo_width=0.8, cross_feedback=0.3)
    print(f"New stereo info: {delay.get_stereo_info()}")
    
    return delay, left_output, right_output


def run_all_demos():
    """Run all delay effect demonstrations."""
    print("🎸 Guitar Effects - Delay Effects Demo")
    print("=" * 50)
    
    try:
        # Run all demos
        basic_delay, basic_output = demo_basic_delay()
        tape_delay, tape_output = demo_tape_delay()
        multi_tap_delay, mt_left, mt_right = demo_multi_tap_delay()
        tempo_delay, tempo_output = demo_tempo_synced_delay()
        stereo_delay, stereo_left, stereo_right = demo_stereo_delay()
        
        print("\n" + "=" * 50)
        print("✅ All delay effects demonstrated successfully!")
        print("\nSummary of implemented effects:")
        print(f"  • {basic_delay.get_effect_name()}: Clean, simple delay")
        print(f"  • {tape_delay.get_effect_name()}: Vintage tape-style delay")
        print(f"  • {multi_tap_delay.get_effect_name()}: Complex multi-tap patterns")
        print(f"  • {tempo_delay.get_effect_name()}: Musical tempo synchronization")
        print(f"  • {stereo_delay.get_effect_name()}: Stereo ping-pong effects")
        
        print("\n🎯 Ready for integration with the guitar effects system!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
