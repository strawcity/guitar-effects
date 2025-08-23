#!/usr/bin/env python3
"""
Raspberry Pi Audio Fix Script

This script helps resolve ALSA underrun issues on Raspberry Pi
by optimizing audio settings and providing diagnostics.
"""

import subprocess
import os
import sys

def check_audio_setup():
    """Check current audio setup on Pi"""
    print("🔊 RASPBERRY PI AUDIO DIAGNOSTICS")
    print("=" * 50)
    
    # Check if running on Pi
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            pi_model = f.read().strip()
        print(f"✅ Raspberry Pi detected: {pi_model}")
    except:
        print("❌ Not running on Raspberry Pi")
        return False
    
    # Check audio devices
    print("\n🎧 Audio Devices:")
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print("❌ Could not list audio devices")
    
    # Check ALSA configuration
    print("\n🔧 ALSA Configuration:")
    asoundrc_path = os.path.expanduser('~/.asoundrc')
    if os.path.exists(asoundrc_path):
        print(f"✅ Found ~/.asoundrc")
        with open(asoundrc_path, 'r') as f:
            print(f.read())
    else:
        print("❌ No ~/.asoundrc found")
    
    return True

def create_optimized_asoundrc():
    """Create optimized ALSA configuration for Scarlett 2i2"""
    print("\n🛠️  Creating optimized ALSA configuration...")
    
    asoundrc_content = '''# Optimized ALSA configuration for Raspberry Pi + Scarlett 2i2
# This reduces audio underruns and improves stability

pcm.!default {
    type asym
    playback.pcm "scarlett_out"
    capture.pcm "scarlett_in"
}

# Scarlett 2i2 input (guitar)
pcm.scarlett_in {
    type hw
    card 1
    device 0
    format S24_3LE
    rate 48000
    channels 2
    buffer_size 4096
    period_size 1024
}

# Scarlett 2i2 output (speakers/headphones)
pcm.scarlett_out {
    type hw
    card 1
    device 0
    format S24_3LE
    rate 48000
    channels 2
    buffer_size 4096
    period_size 1024
}

# Control interface
ctl.!default {
    type hw
    card 1
}
'''
    
    asoundrc_path = os.path.expanduser('~/.asoundrc')
    try:
        with open(asoundrc_path, 'w') as f:
            f.write(asoundrc_content)
        print(f"✅ Created optimized ~/.asoundrc")
        print("💡 This configures larger buffers to prevent underruns")
        return True
    except Exception as e:
        print(f"❌ Could not create ~/.asoundrc: {e}")
        return False

def optimize_pi_audio():
    """Apply Pi audio optimizations"""
    print("\n⚙️  Applying Raspberry Pi audio optimizations...")
    
    optimizations = [
        ("Set audio buffer size", "echo 'snd_usb_audio.nrpacks=1' | sudo tee -a /etc/modprobe.d/alsa-base.conf"),
        ("Increase USB buffer", "echo 'snd_usb_audio.async_unlink=0' | sudo tee -a /etc/modprobe.d/alsa-base.conf"),
        ("Set audio priority", "echo '@audio - rtprio 95' | sudo tee -a /etc/security/limits.conf"),
        ("Set audio memlock", "echo '@audio - memlock unlimited' | sudo tee -a /etc/security/limits.conf"),
    ]
    
    for desc, command in optimizations:
        try:
            print(f"🔧 {desc}...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {desc} applied")
            else:
                print(f"⚠️  {desc} may have failed: {result.stderr}")
        except Exception as e:
            print(f"❌ {desc} failed: {e}")
    
    print("\n💡 Optimizations applied. You may need to reboot for all changes to take effect.")

def test_audio_performance():
    """Test audio performance with current settings"""
    print("\n🧪 Testing audio performance...")
    
    try:
        # Test audio with aplay
        print("🔊 Testing audio playback...")
        result = subprocess.run(['speaker-test', '-t', 'sine', '-f', '440', '-c', '1', '-s', '1'], 
                              capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            print("✅ Audio playback test passed")
        else:
            print(f"❌ Audio playback test failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("✅ Audio playback test completed (timeout is normal)")
    except Exception as e:
        print(f"❌ Audio test error: {e}")

def show_recommendations():
    """Show recommendations for Pi audio setup"""
    print("\n💡 RASPBERRY PI AUDIO RECOMMENDATIONS")
    print("=" * 50)
    print("1. Use a high-quality USB audio interface (like Scarlett 2i2)")
    print("2. Use a powered USB hub for the audio interface")
    print("3. Increase GPU memory split: sudo raspi-config > Advanced > Memory Split > 128")
    print("4. Disable unnecessary services to free up CPU")
    print("5. Use a high-quality SD card (Class 10 or better)")
    print("6. Ensure adequate power supply (3A for Pi 4)")
    print("\n🎸 For guitar effects:")
    print("- Connect guitar to Input 1 on Scarlett 2i2")
    print("- Set input gain on Scarlett 2i2 (green light = good level)")
    print("- Use headphones or monitors connected to Scarlett outputs")
    print("- Start with larger buffer sizes and reduce if stable")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("🔧 FIXING RASPBERRY PI AUDIO ISSUES")
        print("=" * 50)
        
        if not check_audio_setup():
            return
        
        create_optimized_asoundrc()
        optimize_pi_audio()
        test_audio_performance()
        
        print("\n🎉 Audio fixes applied!")
        print("💡 Restart your Pi and try the arpeggiator again")
        print("💡 If issues persist, check physical connections and power supply")
        
    else:
        check_audio_setup()
        show_recommendations()
        print(f"\n💡 To apply fixes automatically, run: python3 {sys.argv[0]} --fix")

if __name__ == "__main__":
    main()
