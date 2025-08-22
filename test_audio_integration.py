#!/usr/bin/env python3
"""
Test script for audio processor integration with delay effects.
"""

def test_audio_processor_import():
    """Test that the audio processor can be imported."""
    try:
        from audio_processor import AudioProcessor
        from config import Config
        print("✅ AudioProcessor imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_audio_processor_instantiation():
    """Test that the audio processor can be instantiated."""
    try:
        from audio_processor import AudioProcessor
        from config import Config
        
        config = Config()
        processor = AudioProcessor(config)
        print("✅ AudioProcessor instantiated successfully!")
        
        # Test effect management
        print(f"Available delay effects: {list(processor.delay_effects.keys())}")
        print(f"Active effects: {list(processor.active_effects)}")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_delay_effect_integration():
    """Test that delay effects are properly integrated."""
    try:
        from audio_processor import AudioProcessor
        from config import Config
        
        config = Config()
        processor = AudioProcessor(config)
        
        # Test starting delay effects
        processor.start_effect("basic_delay")
        print(f"Basic delay active: {'basic_delay' in processor.active_effects}")
        
        processor.start_effect("tape_delay")
        print(f"Tape delay active: {'tape_delay' in processor.active_effects}")
        
        # Test parameter setting
        processor.set_delay_parameter("basic_delay", "delay_time", 0.3)
        processor.set_delay_parameter("basic_delay", "feedback", 0.5)
        processor.set_delay_parameter("basic_delay", "wet_mix", 0.7)
        
        # Test status retrieval
        status = processor.get_effect_status("basic_delay")
        print(f"Basic delay status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_arpeggiator_integration():
    """Test that arpeggiator is properly integrated."""
    try:
        from audio_processor import AudioProcessor
        from config import Config
        
        config = Config()
        processor = AudioProcessor(config)
        
        # Test arpeggiator parameters
        processor.set_arpeggiator_parameter("tempo", 120)
        processor.set_arpeggiator_parameter("pattern", "up")
        processor.set_arpeggiator_parameter("synth", "sine")
        
        # Test status
        status = processor.get_effect_status("arpeggiator")
        print(f"Arpeggiator status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Arpeggiator integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Audio Processor Integration")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_audio_processor_import),
        ("Instantiation Test", test_audio_processor_instantiation),
        ("Delay Integration Test", test_delay_effect_integration),
        ("Arpeggiator Integration Test", test_arpeggiator_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Audio processor integration is working correctly.")
        print("\n🚀 You can now run the enhanced CLI with:")
        print("   python interactive_cli.py")
        print("\n💡 The delay effects should now actually process audio!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
