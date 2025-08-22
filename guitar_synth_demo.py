#!/usr/bin/env python3
"""
Guitar Synth Effect Demo

This script demonstrates the guitar synth effect with different presets and parameter combinations.
"""

import numpy as np
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from guitar_synth import GuitarSynth
    print("🎸 Guitar Synth Effect Demo")
    print("=" * 40)
    
    # Create guitar synth instance
    synth = GuitarSynth()
    
    # Generate test audio (simulated guitar input)
    sample_rate = 44100
    duration = 2.0  # 2 seconds
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a guitar-like signal (chord progression)
    guitar_signal = (
        0.3 * np.sin(2 * np.pi * 220 * t) +      # A3
        0.2 * np.sin(2 * np.pi * 277 * t) +      # C#4
        0.15 * np.sin(2 * np.pi * 330 * t)       # E4
    )
    
    # Add some harmonics and noise for realism
    guitar_signal += 0.1 * np.random.randn(len(t))
    
    print(f"Generated {duration}s guitar signal at {sample_rate}Hz")
    
    # Demo different presets
    presets = {
        "robotic": "Metallic, digital sound with high ring modulation",
        "warm": "Smooth, analog-style filtering with subtle effects", 
        "digital": "Aggressive bit crushing and wave shaping",
        "metallic": "Balanced metallic character with moderate effects"
    }
    
    print("\n🎛️  Demo Presets:")
    print("-" * 40)
    
    for preset_name, description in presets.items():
        print(f"\n{preset_name.upper()}: {description}")
        print(f"Parameters: {synth.get_parameters()}")
        
        # Apply preset
        synth.set_preset(preset_name)
        
        # Process audio
        processed = synth.process_audio(guitar_signal)
        
        # Show some statistics
        input_rms = np.sqrt(np.mean(guitar_signal**2))
        output_rms = np.sqrt(np.mean(processed**2))
        print(f"  Input RMS: {input_rms:.4f}, Output RMS: {output_rms:.4f}")
        print(f"  Gain change: {20 * np.log10(output_rms / input_rms):.1f} dB")
        
    # Demo custom parameter combinations
    print("\n🎛️  Custom Parameter Combinations:")
    print("-" * 40)
    
    # High-frequency ring modulation
    print("\nHigh-frequency ring modulation:")
    synth.set_parameters(ring_frequency=800, bit_depth=16, wet_mix=0.9)
    processed = synth.process_audio(guitar_signal)
    print(f"  Ring freq: 800Hz, Wet mix: 90%")
    
    # Aggressive bit crushing
    print("\nAggressive bit crushing:")
    synth.set_parameters(ring_frequency=0, bit_depth=3, sample_rate_reduction=0.2, wet_mix=0.8)
    processed = synth.process_audio(guitar_signal)
    print(f"  Bit depth: 3 bits, Sample rate: 20%, Wet mix: 80%")
    
    # Warm filtering
    print("\nWarm filtering:")
    synth.set_parameters(filter_cutoff=500, filter_resonance=0.8, envelope_sensitivity=0.7, wet_mix=0.6)
    processed = synth.process_audio(guitar_signal)
    print(f"  Filter cutoff: 500Hz, Resonance: 80%, Envelope: 70%, Wet mix: 60%")
    
    print("\n✅ Demo completed successfully!")
    print("\nTo use in the interactive CLI:")
    print("1. Run: python3 interactive_cli.py")
    print("2. Select guitar synth: select guitar_synth")
    print("3. Start the effect: start")
    print("4. Try presets: preset robotic")
    print("5. Adjust parameters: ring_freq 200")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the guitar-effects directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
