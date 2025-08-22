#!/usr/bin/env python3
"""
Test script to verify audio setup on Raspberry Pi with Scarlett 2i2
"""

import sounddevice as sd
import numpy as np
import time

def test_audio_devices():
    """Test audio device detection"""
    print("🔊 Testing audio device detection...")
    
    try:
        devices = sd.query_devices()
        print(f"Found {len(devices)} audio devices:")
        
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']}")
            print(f"     Inputs: {device.get('max_inputs', 'N/A')}, Outputs: {device.get('max_outputs', 'N/A')}")
            print(f"     Sample rates: {device.get('default_samplerate', 'N/A')}")
            print()
        
        # Find Scarlett 2i2
        scarlett_input = None
        scarlett_output = None
        
        for i, device in enumerate(devices):
            name = device['name'].lower()
            if 'scarlett' in name or 'focusrite' in name:
                if device.get('max_inputs', 0) > 0:
                    scarlett_input = i
                if device.get('max_outputs', 0) > 0:
                    scarlett_output = i
        
        if scarlett_input is not None:
            print(f"✅ Found Scarlett input device: {devices[scarlett_input]['name']} (ID: {scarlett_input})")
        else:
            print("❌ No Scarlett input device found")
            
        if scarlett_output is not None:
            print(f"✅ Found Scarlett output device: {devices[scarlett_output]['name']} (ID: {scarlett_output})")
        else:
            print("❌ No Scarlett output device found")
            
        return scarlett_input, scarlett_output
        
    except Exception as e:
        print(f"❌ Error querying devices: {e}")
        return None, None

def test_audio_stream(input_device, output_device):
    """Test audio stream creation"""
    print("\n🎵 Testing audio stream creation...")
    
    try:
        # Create a test stream
        with sd.Stream(
            channels=(1, 1),
            samplerate=48000,
            blocksize=2048,
            dtype=np.float32,
            latency='high',
            device=(input_device, output_device) if input_device is not None and output_device is not None else None
        ) as stream:
            print("✅ Audio stream created successfully!")
            print(f"   Active: {stream.active}")
            print(f"   Sample rate: {stream.samplerate}")
            print(f"   Channels: {stream.channels}")
            print(f"   Blocksize: {stream.blocksize}")
            return True
            
    except Exception as e:
        print(f"❌ Error creating audio stream: {e}")
        return False

def test_audio_playback(output_device):
    """Test audio playback"""
    print("\n🔊 Testing audio playback...")
    
    try:
        # Generate a test tone (440 Hz sine wave)
        duration = 2.0  # seconds
        sample_rate = 48000
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = 0.3 * np.sin(2 * np.pi * 440 * t)
        
        print("Playing 440 Hz test tone for 2 seconds...")
        print("You should hear this through your Scarlett 2i2 monitor outputs!")
        
        sd.play(tone, sample_rate, device=output_device)
        sd.wait()
        
        print("✅ Audio playback test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during audio playback: {e}")
        return False

def main():
    """Main test function"""
    print("🎸 Guitar Arpeggiator Audio Setup Test")
    print("=" * 50)
    
    # Test device detection
    input_device, output_device = test_audio_devices()
    
    if input_device is None or output_device is None:
        print("\n⚠️  Scarlett 2i2 not detected. Please check:")
        print("   1. USB connection to Raspberry Pi")
        print("   2. Device is powered on")
        print("   3. No other applications are using the audio device")
        return
    
    # Test stream creation
    if not test_audio_stream(input_device, output_device):
        print("\n❌ Audio stream test failed. Check audio permissions and device availability.")
        return
    
    # Test audio playback
    if not test_audio_playback(output_device):
        print("\n❌ Audio playback test failed. Check monitor output settings.")
        return
    
    print("\n🎉 All audio tests passed!")
    print("\nYour Scarlett 2i2 is properly configured for the guitar arpeggiator.")
    print("You should now be able to:")
    print("  1. Hear your guitar through the monitor outputs")
    print("  2. Hear generated arpeggios mixed with your guitar")
    print("  3. Use the system without audio crashes")

if __name__ == "__main__":
    main()
