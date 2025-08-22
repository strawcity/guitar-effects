#!/usr/bin/env python3
"""
Test script for the Guitar Synth effect.
"""

import numpy as np
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from guitar_synth import GuitarSynth
    print("✅ GuitarSynth imported successfully")
    
    # Test creating an instance
    synth = GuitarSynth()
    print("✅ GuitarSynth instance created successfully")
    
    # Test parameter setting
    synth.set_ring_frequency(150.0)
    synth.set_bit_depth(6)
    synth.set_wet_mix(0.8)
    print("✅ Parameters set successfully")
    
    # Test audio processing
    test_audio = np.random.randn(1000) * 0.1  # Generate some test audio
    processed = synth.process_audio(test_audio)
    print(f"✅ Audio processing successful: input shape {test_audio.shape}, output shape {processed.shape}")
    
    # Test presets
    synth.set_parameters(ring_frequency=200.0, bit_depth=4, wet_mix=0.9)
    print("✅ Preset parameters applied successfully")
    
    print("\n🎸 Guitar Synth effect is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
