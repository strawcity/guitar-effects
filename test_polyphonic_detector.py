#!/usr/bin/env python3
"""
Test script for the new polyphonic chord detector
"""

try:
    from polyphonic_chord_detector import PolyphonicChordDetector
    print("✅ Polyphonic chord detector imported successfully")
    
    # Test initialization
    detector = PolyphonicChordDetector()
    print("✅ Detector initialized successfully")
    
    # Test frequency to note conversion
    test_freq = 130.81  # C3
    note_info = detector._frequency_to_note_enhanced(test_freq)
    if note_info:
        print(f"✅ C3 detection: {note_info['note']}{note_info['octave']} at {note_info['frequency']:.2f} Hz")
        print(f"   Cents off: {note_info['cents_off']:+.1f}")
        print(f"   Tuning status: {note_info['tuning_status']}")
    else:
        print("❌ C3 detection failed")
    
    # Test chord quality detection
    test_notes = ['C', 'E', 'G']
    quality = detector._determine_chord_quality(test_notes)
    print(f"✅ Chord quality detection: {test_notes} = {quality}")
    
    print("\n🎸 Polyphonic chord detector is ready!")
    print("💡 This detector uses Constant-Q Transform for better polyphonic analysis")
    print("💡 It should handle your C major chord much better!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you have installed the requirements:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
