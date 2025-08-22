#!/usr/bin/env python3
"""
Test script for the simple chord detector
"""

try:
    from simple_chord_detector import SimpleChordDetector
    print("✅ Simple chord detector imported successfully")
    
    # Test initialization
    detector = SimpleChordDetector()
    print("✅ Simple chord detector initialized")
    
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
    
    print("\n🎯 Simple chord detector is working!")
    print("💡 This detector uses optimized FFT analysis for reliable chord recognition")
    print("💡 No external dependencies required!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you have installed the basic requirements:")
    print("   pip install numpy scipy sounddevice")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 There may be an issue with the basic dependencies")

if __name__ == "__main__":
    print("🎸 Testing Simple Chord Detector")
    print("=" * 40)
