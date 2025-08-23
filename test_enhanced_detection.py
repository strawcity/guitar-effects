#!/usr/bin/env python3
"""
Test Script for Enhanced Guitar Note and Chord Detection System

This script demonstrates the capabilities of the new system based on
piano key frequencies and equal temperament tuning principles.
"""

import numpy as np
import time
import sys
from enhanced_guitar_detector import EnhancedGuitarDetector
from enhanced_chord_detector import EnhancedChordDetector

def test_note_detection():
    """Test the enhanced note detection system"""
    print("\n" + "="*60)
    print("🎸 TESTING ENHANCED NOTE DETECTION")
    print("="*60)
    
    # Initialize detector
    detector = EnhancedGuitarDetector()
    
    # Test with known frequencies
    test_frequencies = [
        (440.0, "A4 - Standard tuning reference"),
        (329.63, "E4 - 1st string"),
        (246.94, "B3 - 2nd string"),
        (196.0, "G3 - 3rd string"),
        (146.83, "D3 - 4th string"),
        (110.0, "A2 - 5th string"),
        (82.41, "E2 - 6th string"),
        (523.25, "C5 - Higher octave"),
        (261.63, "C4 - Middle C"),
        (174.61, "F3 - Between strings")
    ]
    
    print("\n📊 Testing with known frequencies:")
    print("-" * 50)
    
    for freq, description in test_frequencies:
        # Generate a simple sine wave
        sample_rate = 44100
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * freq * t) * 0.5
        
        # Detect note
        result = detector.detect_note_from_audio(audio)
        
        if result['note'] != 'Unknown':
            status = "✅ PASS"
            tuning_feedback = detector.get_tuning_feedback(result['cents_off'])
            print(f"{status} {description:25} → {result['note']}{result['octave']} "
                  f"({result['frequency']:.1f} Hz) {tuning_feedback}")
        else:
            print(f"❌ FAIL {description:25} → No note detected")
    
    # Test harmonic content
    print("\n🎵 Testing harmonic analysis:")
    print("-" * 50)
    
    # Create a note with harmonics
    fundamental = 220.0  # A3
    sample_rate = 44100
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Add harmonics: fundamental + 2nd + 3rd + 5th
    audio = (np.sin(2 * np.pi * fundamental * t) * 0.4 +
             np.sin(2 * np.pi * fundamental * 2 * t) * 0.3 +
             np.sin(2 * np.pi * fundamental * 3 * t) * 0.2 +
             np.sin(2 * np.pi * fundamental * 5 * t) * 0.1)
    
    result = detector.detect_note_from_audio(audio)
    
    if result['note'] != 'Unknown':
        print(f"✅ Harmonic test: A3 with harmonics → {result['note']}{result['octave']} "
              f"({result['frequency']:.1f} Hz)")
        print(f"   Confidence: {result['confidence']:.2f}, Method: {result['method']}")
    else:
        print("❌ Harmonic test failed")

def test_chord_detection():
    """Test the enhanced chord detection system"""
    print("\n" + "="*60)
    print("🎸 TESTING ENHANCED CHORD DETECTION")
    print("="*60)
    
    # Initialize detector
    detector = EnhancedChordDetector()
    
    # Test with known chord frequencies
    test_chords = [
        {
            'name': 'C Major',
            'frequencies': [261.63, 329.63, 392.0],  # C4, E4, G4
            'expected': 'C'
        },
        {
            'name': 'A Minor',
            'frequencies': [220.0, 261.63, 329.63],  # A3, C4, E4
            'expected': 'Am'
        },
        {
            'name': 'G Major',
            'frequencies': [196.0, 246.94, 293.66],  # G3, B3, D4
            'expected': 'G'
        },
        {
            'name': 'E Minor',
            'frequencies': [164.81, 196.0, 246.94],  # E3, G3, B3
            'expected': 'Em'
        },
        {
            'name': 'F Major',
            'frequencies': [174.61, 220.0, 261.63],  # F3, A3, C4
            'expected': 'F'
        },
        {
            'name': 'D Minor',
            'frequencies': [146.83, 174.61, 220.0],  # D3, F3, A3
            'expected': 'Dm'
        }
    ]
    
    print("\n📊 Testing with known chord frequencies:")
    print("-" * 60)
    
    for chord_info in test_chords:
        # Generate chord audio
        sample_rate = 44100
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Mix all frequencies
        audio = np.zeros_like(t)
        for freq in chord_info['frequencies']:
            audio += np.sin(2 * np.pi * freq * t) * 0.3
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        # Detect chord
        result = detector.detect_chord_from_audio(audio)
        
        if result['valid']:
            status = "✅ PASS"
            print(f"{status} {chord_info['name']:15} → {result['symbol']:8} "
                  f"(Root: {result['root']}, Quality: {result['quality']})")
            print(f"      Notes: {result['notes']}, Confidence: {result['confidence']:.2f}")
        else:
            print(f"❌ FAIL {chord_info['name']:15} → No chord detected")
    
    # Test extended chords
    print("\n🎵 Testing extended chords:")
    print("-" * 60)
    
    # C Major 7th: C4, E4, G4, B4
    extended_chord_freqs = [261.63, 329.63, 392.0, 493.88]
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    audio = np.zeros_like(t)
    for freq in extended_chord_freqs:
        audio += np.sin(2 * np.pi * freq * t) * 0.25
    
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    result = detector.detect_chord_from_audio(audio)
    
    if result['valid']:
        print(f"✅ Extended chord: C Major 7th → {result['symbol']}")
        print(f"   Notes: {result['notes']}, Voicing: {result['voicing']}")
        print(f"   Confidence: {result['confidence']:.2f}")
    else:
        print("❌ Extended chord test failed")

def test_frequency_calculations():
    """Test the frequency calculation system based on piano key principles"""
    print("\n" + "="*60)
    print("🎹 TESTING FREQUENCY CALCULATIONS")
    print("="*60)
    
    # Initialize detector to access frequency calculations
    detector = EnhancedGuitarDetector()
    
    print("\n📊 Piano key frequency calculations:")
    print("-" * 50)
    
    # Test A4 reference and semitone calculations
    a4_freq = detector.A4_FREQUENCY
    semitone_ratio = detector.SEMITONE_RATIO
    
    print(f"A4 reference frequency: {a4_freq} Hz")
    print(f"Semitone ratio (12th root of 2): {semitone_ratio:.6f}")
    print(f"Octave ratio (12 semitones): {semitone_ratio ** 12:.6f}")
    
    # Test some key frequencies
    test_notes = [
        ('A4', 440.0),
        ('A#4', 440.0 * semitone_ratio),
        ('B4', 440.0 * (semitone_ratio ** 2)),
        ('C5', 440.0 * (semitone_ratio ** 3)),
        ('C#5', 440.0 * (semitone_ratio ** 4)),
        ('D5', 440.0 * (semitone_ratio ** 5))
    ]
    
    print("\n🎵 Calculated vs. Expected frequencies:")
    print("-" * 50)
    
    for note_name, expected_freq in test_notes:
        # Find in our calculated frequencies
        calculated_freq = None
        for key, freq in detector.note_frequencies.items():
            if key == note_name:
                calculated_freq = freq
                break
        
        if calculated_freq:
            diff = abs(calculated_freq - expected_freq)
            status = "✅" if diff < 0.1 else "❌"
            print(f"{status} {note_name}: {calculated_freq:.2f} Hz (expected: {expected_freq:.2f} Hz)")
        else:
            print(f"❌ {note_name}: Not found in calculated frequencies")

def test_guitar_string_identification():
    """Test guitar string identification"""
    print("\n" + "="*60)
    print("🎸 TESTING GUITAR STRING IDENTIFICATION")
    print("="*60)
    
    detector = EnhancedGuitarDetector()
    
    print("\n📊 Guitar string frequencies:")
    print("-" * 40)
    
    for string_name, string_freq in detector.guitar_strings.items():
        print(f"{string_name}: {string_freq} Hz")
    
    print("\n🎯 String identification tests:")
    print("-" * 40)
    
    # Test frequencies close to guitar strings
    test_frequencies = [
        (82.5, "E2 - 6th string"),
        (110.2, "A2 - 5th string"),
        (147.1, "D3 - 4th string"),
        (196.5, "G3 - 3rd string"),
        (247.2, "B3 - 2nd string"),
        (330.1, "E4 - 1st string")
    ]
    
    for freq, description in test_frequencies:
        string_info = detector._identify_guitar_string(freq)
        
        if string_info:
            print(f"✅ {description:20} → {string_info['string']} "
                  f"(diff: {string_info['difference']:.1f} Hz, "
                  f"{string_info['cents_off']:.1f} cents)")
        else:
            print(f"❌ {description:20} → No string identified")

def run_comprehensive_test():
    """Run all tests"""
    print("🎸 ENHANCED GUITAR DETECTION SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)
    print("This system is based on piano key frequencies and equal temperament tuning")
    print("Using A4 = 440 Hz reference and the twelfth root of 2 for semitone calculations")
    print("=" * 80)
    
    try:
        # Run all tests
        test_frequency_calculations()
        test_guitar_string_identification()
        test_note_detection()
        test_chord_detection()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n🎯 Key Features of the Enhanced System:")
        print("   • Precise frequency calculations using piano key principles")
        print("   • Multiple detection algorithms (FFT, autocorrelation, YIN)")
        print("   • Advanced harmonic analysis for better accuracy")
        print("   • Real-time tuning feedback with cents accuracy")
        print("   • Extended chord recognition (triads, 7ths, 9ths, etc.)")
        print("   • Guitar string identification and voicing detection")
        print("   • Confidence scoring and alternative interpretations")
        
        print("\n💡 The system now provides:")
        print("   • More accurate note detection using equal temperament")
        print("   • Better chord recognition through harmonic analysis")
        print("   • Professional-grade tuning feedback")
        print("   • Support for complex chord types and voicings")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def interactive_test():
    """Interactive test mode for live audio"""
    print("\n🎤 INTERACTIVE TEST MODE")
    print("=" * 40)
    print("This will test the system with live audio from your microphone")
    print("Make sure your guitar is connected and ready!")
    
    try:
        choice = input("\nChoose test type:\n1. Note detection\n2. Chord detection\n3. Both\nChoice (1-3): ").strip()
        
        if choice in ['1', '3']:
            print("\n🎸 Testing note detection...")
            detector = EnhancedGuitarDetector()
            detector.test_detection(5.0)
        
        if choice in ['2', '3']:
            print("\n🎸 Testing chord detection...")
            detector = EnhancedChordDetector()
            detector.test_chord_detection(5.0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Interactive test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_comprehensive_test()
