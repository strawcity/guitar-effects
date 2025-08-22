#!/usr/bin/env python3
"""
Test script to verify threshold fixes work correctly
"""

import numpy as np
from polyphonic_chord_detector import PolyphonicChordDetector
from chord_detector import ChordDetector

def test_threshold_checks():
    """Test that threshold checks prevent false detections"""
    print("🧪 Testing threshold checks...")
    
    # Test 1: Very weak signal (should return empty result)
    print("\n1️⃣ Testing very weak signal (0.001)...")
    weak_audio = np.random.normal(0, 0.001, 4096).astype(np.float32)
    
    detector = PolyphonicChordDetector()
    result = detector.detect_chord_polyphonic(weak_audio)
    
    if result['valid']:
        print("❌ Weak signal incorrectly detected as valid chord")
        print(f"   Result: {result['root']} {result['quality']}")
    else:
        print("✅ Weak signal correctly rejected")
    
    # Test 2: Strong signal (should work)
    print("\n2️⃣ Testing strong signal (0.01)...")
    strong_audio = np.random.normal(0, 0.01, 4096).astype(np.float32)
    
    result = detector.detect_chord_polyphonic(strong_audio)
    print(f"   Result: valid={result['valid']}, notes={len(result.get('note_details', []))}")
    
    # Test 3: Chord detector threshold check
    print("\n3️⃣ Testing chord detector threshold check...")
    chord_detector = ChordDetector(None)  # Mock config
    
    frequencies = chord_detector.find_frequencies_in_audio(weak_audio)
    if frequencies:
        print("❌ Chord detector should have rejected weak signal")
        print(f"   Found {len(frequencies)} frequencies")
    else:
        print("✅ Chord detector correctly rejected weak signal")
    
    print("\n🎯 Threshold tests completed!")

if __name__ == "__main__":
    test_threshold_checks()
