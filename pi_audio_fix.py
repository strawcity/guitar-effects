#!/usr/bin/env python3
"""
Raspberry Pi Audio Fix - Scarlett 2i2 Integration

This script fixes the audio device selection to use your Scarlett 2i2
instead of the default Pi audio devices.
"""

import sounddevice as sd
import numpy as np
import time
import os

def find_scarlett_2i2():
    """Find the Scarlett 2i2 audio device."""
    print("🔍 Looking for Scarlett 2i2...")
    
    devices = sd.query_devices()
    scarlett_devices = []
    
    for i, device in enumerate(devices):
        name = device['name'].lower()
        if 'scarlett' in name or '2i2' in name or 'focusrite' in name:
            scarlett_devices.append((i, device))
            print(f"✅ Found Scarlett 2i2 at device {i}: {device['name']}")
            # Handle different key names for ALSA devices
            input_channels = device.get('max_inputs', device.get('max_input_channels', 0))
            output_channels = device.get('max_outputs', device.get('max_output_channels', 0))
            sample_rate = device.get('default_samplerate', 48000)
            print(f"   Input channels: {input_channels}")
            print(f"   Output channels: {output_channels}")
            print(f"   Sample rate: {sample_rate}")
    
    if not scarlett_devices:
        print("❌ Scarlett 2i2 not found!")
        print("💡 Make sure it's connected via USB")
        print("💡 Try unplugging and reconnecting")
        return None, None
    
    print(f"📊 Found {len(scarlett_devices)} Scarlett device(s)")
    
    # Use the first Scarlett device found
    device_id, device_info = scarlett_devices[0]
    print(f"🎯 Using device {device_id}: {device_info['name']}")
    return device_id, device_info

def test_scarlett_audio(scarlett_device_id):
    """Test audio with the Scarlett 2i2."""
    print(f"\n🧪 Testing Scarlett 2i2 (device {scarlett_device_id})...")
    
    try:
        # Test input stream
        print("Testing input stream...")
        with sd.InputStream(
            device=scarlett_device_id,
            channels=1,
            samplerate=48000,
            blocksize=1024,
            dtype=np.float32,
            latency='high'
        ) as stream:
            print("✅ Input stream working")
            
        # Test output stream
        print("Testing output stream...")
        with sd.OutputStream(
            device=scarlett_device_id,
            channels=1,
            samplerate=48000,
            blocksize=1024,
            dtype=np.float32,
            latency='high'
        ) as stream:
            print("✅ Output stream working")
            
        # Test audio playback
        print("Testing audio playback...")
        sample_rate = 48000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440Hz A note
        
        sd.play(test_tone, sample_rate, device=scarlett_device_id)
        sd.wait()
        print("✅ Audio playback working")
        
        return True
        
    except Exception as e:
        print(f"❌ Scarlett test failed: {e}")
        return False



def update_audio_processor(scarlett_device_id):
    """Update the audio processor to use the Scarlett 2i2."""
    print(f"\n🔧 Updating audio processor...")
    
    try:
        # Read the current audio processor
        with open('optimized_audio_processor.py', 'r') as f:
            content = f.read()
        
        # Add device selection to start_audio method
        if 'device=(input_device, output_device)' in content:
            # Replace with Scarlett device
            content = content.replace(
                'device=(input_device, output_device)',
                f'device=({scarlett_device_id}, {scarlett_device_id})'
            )
            
            # Write back
            with open('optimized_audio_processor.py', 'w') as f:
                f.write(content)
            print("✅ Updated audio processor with Scarlett device")
        else:
            print("✅ Audio processor already has device selection")
            
        return True
        
    except Exception as e:
        print(f"❌ Could not update audio processor: {e}")
        return False

def create_simple_test(scarlett_device_id):
    """Create a simple test script."""
    print(f"\n🧪 Creating simple test script...")
    
    test_content = f"""#!/usr/bin/env python3
import sounddevice as sd
import numpy as np

def test_scarlett():
    print("🎸 Testing Scarlett 2i2...")
    
    try:
        # Test output
        with sd.OutputStream(
            device={scarlett_device_id},
            channels=1,
            samplerate=48000,
            blocksize=1024,
            dtype=np.float32,
            latency='high'
        ) as stream:
            print("✅ Output stream working")
            
            # Play test tone
            sample_rate = 48000
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)
            
            stream.write(test_tone)
            print("✅ Audio output working")
        
        print("🎉 Scarlett 2i2 test successful!")
        
    except Exception as e:
        print(f"❌ Test failed: {{e}}")

if __name__ == "__main__":
    test_scarlett()
"""
    
    test_path = 'test_scarlett_simple.py'
    try:
        with open(test_path, 'w') as f:
            f.write(test_content)
        print(f"✅ Created {test_path}")
        return test_path
    except Exception as e:
        print(f"❌ Could not create test script: {e}")
        return None

def main():
    """Main fix function."""
    print("🔧 RASPBERRY PI + SCARLETT 2I2 AUDIO FIX")
    print("=" * 60)
    print("This script will configure your Pi to use the Scarlett 2i2")
    print("Make sure your Scarlett 2i2 is connected via USB")
    print()
    
    # Find Scarlett 2i2
    print("🔍 Calling find_scarlett_2i2()...")
    scarlett_device_id, device_info = find_scarlett_2i2()
    print(f"🔍 Returned: device_id={scarlett_device_id}, device_info={device_info}")
    
    if scarlett_device_id is None:
        print("❌ Cannot proceed without Scarlett 2i2")
        return
    
    # Test the device
    if not test_scarlett_audio(scarlett_device_id):
        print("❌ Scarlett 2i2 test failed")
        return
    
    
        return
    
    # Update audio processor
    if not update_audio_processor(scarlett_device_id):
        print("❌ Could not update audio processor")
        return
    
    # Create test script
    test_path = create_simple_test(scarlett_device_id)
    
    print("\n🎉 SCARLETT 2I2 INTEGRATION COMPLETE!")
    print("=" * 60)
    print("Your Pi is now configured to use the Scarlett 2i2")
    print()
    print("📋 Next steps:")
    print("1. Test the integration:")
    print(f"   python3 {test_path}")
    print()
    print("2. Try the interactive CLI:")
    print("   python3 interactive_cli.py")
    print("   select delay effect")
    print("   start")
    print()
    print("3. Strum your guitar - you should hear audio!")
    print()
    print("💡 If you still have issues, run:")
    print("   python3 pi_audio_debug.py")

if __name__ == "__main__":
    main()
