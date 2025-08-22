#!/usr/bin/env python3
"""
Test script for delay effects package.
"""

def test_delay_imports():
    """Test that all delay effects can be imported."""
    try:
        from delay import (BasicDelay, TapeDelay, MultiTapDelay, 
                          TempoSyncedDelay, StereoDelay, BaseDelay)
        print("✅ All delay effects imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_delay_instantiation():
    """Test that all delay effects can be instantiated."""
    try:
        from delay import (BasicDelay, TapeDelay, MultiTapDelay, 
                          TempoSyncedDelay, StereoDelay)
        
        # Test basic delay
        basic = BasicDelay()
        print(f"✅ {basic.get_effect_name()} instantiated")
        
        # Test tape delay
        tape = TapeDelay()
        print(f"✅ {tape.get_effect_name()} instantiated")
        
        # Test multi-tap delay
        multi = MultiTapDelay()
        print(f"✅ {multi.get_effect_name()} instantiated")
        
        # Test tempo-synced delay
        tempo = TempoSyncedDelay()
        print(f"✅ {tempo.get_effect_name()} instantiated")
        
        # Test stereo delay
        stereo = StereoDelay()
        print(f"✅ {stereo.get_effect_name()} instantiated")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_delay_functionality():
    """Test basic functionality of delay effects."""
    try:
        from delay import BasicDelay
        import numpy as np
        
        # Create a simple test signal
        sample_rate = 44100
        duration = 0.1  # 100ms
        t = np.linspace(0, duration, int(duration * sample_rate), False)
        test_signal = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
        
        # Test basic delay processing
        delay = BasicDelay(sample_rate=sample_rate, delay_time=0.01, feedback=0.2)
        output = delay.process_buffer(test_signal)
        
        print(f"✅ Basic delay processing successful: {len(output)} samples")
        print(f"   Input: {len(test_signal)} samples, Output: {len(output)} samples")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🎸 Testing Delay Effects Package")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_delay_imports),
        ("Instantiation Test", test_delay_instantiation),
        ("Functionality Test", test_delay_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Delay effects package is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
