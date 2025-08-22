#!/usr/bin/env python3
"""
Test script for the enhanced interactive CLI.
"""

def test_cli_import():
    """Test that the enhanced CLI can be imported."""
    try:
        from interactive_cli import EnhancedInteractiveCLI, EffectController, ArpeggiatorController, DelayController
        print("✅ Enhanced CLI classes imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_cli_instantiation():
    """Test that the enhanced CLI can be instantiated."""
    try:
        from interactive_cli import EnhancedInteractiveCLI
        
        cli = EnhancedInteractiveCLI()
        print("✅ Enhanced CLI instantiated successfully!")
        
        # Test effect listing
        print("\n--- Testing Effect Listing ---")
        cli.list_effects()
        
        # Test effect selection
        print("\n--- Testing Effect Selection ---")
        cli.select_effect("basic_delay")
        print(f"Current effect: {cli.current_effect}")
        
        cli.select_effect("arpeggiator")
        print(f"Current effect: {cli.current_effect}")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_effect_controllers():
    """Test individual effect controllers."""
    try:
        from interactive_cli import ArpeggiatorController, DelayController
        
        # Test arpeggiator controller
        print("\n--- Testing Arpeggiator Controller ---")
        arp_controller = ArpeggiatorController()
        print(f"✅ {arp_controller.name} controller created")
        
        # Test delay controllers
        print("\n--- Testing Delay Controllers ---")
        delay_types = ["basic", "tape", "multi", "tempo", "stereo"]
        
        for delay_type in delay_types:
            delay_controller = DelayController(delay_type)
            print(f"✅ {delay_controller.name} controller created")
            
        return True
    except Exception as e:
        print(f"❌ Effect controller error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_functionality():
    """Test basic CLI functionality."""
    try:
        from interactive_cli import EnhancedInteractiveCLI
        
        cli = EnhancedInteractiveCLI()
        
        # Test status display
        print("\n--- Testing Status Display ---")
        cli.show_status()
        
        # Test help display
        print("\n--- Testing Help Display ---")
        cli.print_effect_help()
        
        print("✅ Basic CLI functionality working!")
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Interactive CLI")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_cli_import),
        ("Instantiation Test", test_cli_instantiation),
        ("Effect Controllers Test", test_effect_controllers),
        ("Functionality Test", test_cli_functionality),
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
        print("🎉 All tests passed! Enhanced CLI is working correctly.")
        print("\n🚀 You can now run the enhanced CLI with:")
        print("   python interactive_cli.py")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
