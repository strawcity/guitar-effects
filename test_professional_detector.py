#!/usr/bin/env python3
"""
Test script for the new professional guitar detector
"""

try:
    from professional_guitar_detector import ProfessionalGuitarDetector
    print("✅ Professional guitar detector imported successfully")
    
    # Test initialization
    detector = ProfessionalGuitarDetector()
    print("✅ Detector initialized successfully")
    
    # Test frequency to note conversion
    test_freq = 130.81  # C3
    note_info = detector._frequency_to_note(test_freq)
    if note_info:
        print(f"✅ C3 detection: {note_info['note']}{note_info['octave']} at {note_info['frequency']:.2f} Hz")
        print(f"   Cents off: {note_info['cents_off']:+.1f}")
        print(f"   Tuning status: {note_info['tuning_status']}")
    else:
        print("❌ C3 detection failed")
    
    print("\n🎸 Professional guitar detector is ready!")
    print("💡 Run 'python professional_guitar_detector.py' to test with live audio")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you have installed the requirements:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
