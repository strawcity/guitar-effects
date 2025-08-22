#!/usr/bin/env python3
"""
Test script to verify the multi-tap delay fix
"""

import numpy as np
from delay.multi_tap_delay import MultiTapDelay

def test_multi_tap_delay():
    """Test the multi-tap delay to ensure it works without errors."""
    print("Testing Multi-Tap Delay...")
    
    # Create multi-tap delay
    delay = MultiTapDelay(sample_rate=44100)
    
    # Test basic functionality
    print(f"Effect name: {delay.get_effect_name()}")
    print(f"Number of taps: {len(delay.taps)}")
    print(f"Stereo output: {delay.stereo_output}")
    
    # Test processing a simple audio buffer
    input_buffer = np.random.rand(1024) * 0.1  # Small random audio
    
    try:
        left_output, right_output = delay.process_buffer(input_buffer)
        print(f"Successfully processed audio buffer")
        print(f"Input shape: {input_buffer.shape}")
        print(f"Left output shape: {left_output.shape}")
        print(f"Right output shape: {right_output.shape}")
        
        # Verify outputs are valid
        assert left_output.shape == input_buffer.shape
        assert right_output.shape == input_buffer.shape
        assert not np.any(np.isnan(left_output))
        assert not np.any(np.isnan(right_output))
        
        print("✓ Multi-tap delay test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Multi-tap delay test failed: {e}")
        return False

def test_parameters():
    """Test parameter handling."""
    print("\nTesting parameter handling...")
    
    delay = MultiTapDelay(sample_rate=44100)
    
    try:
        # Test getting parameters
        params = delay.get_parameters()
        print(f"Parameters: {params}")
        
        # Test setting tap parameters
        delay.set_tap_parameters(0, delay_time=0.3, level=0.8, pan=0.5)
        print("✓ Parameter handling test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Parameter handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("Multi-Tap Delay Fix Test")
    print("=" * 40)
    
    test1 = test_multi_tap_delay()
    test2 = test_parameters()
    
    if test1 and test2:
        print("\n🎉 All tests passed! The multi-tap delay fix is working.")
    else:
        print("\n❌ Some tests failed. There may still be issues.")
