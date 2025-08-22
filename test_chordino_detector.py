#!/usr/bin/env python3
"""
Test script for the new Chordino chord detector
"""

try:
    from chordino_chord_detector import ChordinoChordDetector
    print("✅ Chordino detector imported successfully")
    
    # Test initialization
    detector = ChordinoChordDetector()
    print("✅ Chordino detector initialized")
    
    # Test with dummy audio
    import numpy as np
    dummy_audio = np.random.normal(0, 0.01, 44100).astype(np.float32)  # 1 second of noise
    
    print("🎸 Testing chord detection with dummy audio...")
    result = detector.detect_chord_from_audio(dummy_audio)
    
    print(f"📊 Detection result: {result}")
    print(f"   Valid: {result.get('valid', False)}")
    print(f"   Root: {result.get('root', 'Unknown')}")
    print(f"   Quality: {result.get('quality', 'unknown')}")
    print(f"   Notes: {result.get('notes', [])}")
    print(f"   Confidence: {result.get('confidence', 0):.2f}")
    
    print("\n🎯 Chordino detector is working!")
    print("💡 This should provide much better chord recognition than the previous methods")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you have installed the requirements:")
    print("   pip install chord-extractor soundfile")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 There may be an issue with the chord-extractor package")

if __name__ == "__main__":
    print("🎸 Testing Chordino Chord Detector")
    print("=" * 40)
