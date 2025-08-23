#!/usr/bin/env python3
"""
Test script to verify threshold fixes work correctly
"""

import numpy as np
from enhanced_chord_detector import EnhancedChordDetector

def test_threshold_checks():
    """Test that threshold checks prevent false detections"""
    print("🧪 Testing threshold checks...")
    
    # Test 1: Very weak signal (should return empty result)
    print("\n1️⃣ Testing very weak signal (0.001)...")
    weak_audio = np.random.normal(0, 0.001, 4096).astype(np.float32)
    
    detector = EnhancedChordDetector()
    result = detector.detect_chord_from_audio(weak_audio)
    
    if result['valid']:
        print("❌ Weak signal incorrectly detected as valid chord")
        print(f"   Result: {result['root']} {result['quality']}")
    else:
        print("✅ Weak signal correctly rejected")
    
    # Test 2: Strong signal (should work)
    print("\n2️⃣ Testing strong signal (0.01)...")
    strong_audio = np.random.normal(0, 0.01, 4096).astype(np.float32)
    
    result = detector.detect_chord_from_audio(strong_audio)
    print(f"   Result: valid={result['valid']}, notes={len(result.get('note_details', []))}")
    
    # Test 3: Enhanced chord detector threshold check
    print("\n3️⃣ Testing enhanced chord detector threshold check...")
    chord_detector = EnhancedChordDetector()
    
    # Test with weak audio
    result = chord_detector.detect_chord_from_audio(weak_audio)
    if result['valid']:
        print("❌ Enhanced chord detector should have rejected weak signal")
        print(f"   Result: {result['root']} {result['quality']}")
    else:
        print("✅ Enhanced chord detector correctly rejected weak signal")
    
    print("\n🎯 Threshold tests completed!")

if __name__ == "__main__":
    test_threshold_checks()
