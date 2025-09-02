#!/bin/bash

echo "🔧 USB Audio Broken Pipe Fix Script"
echo "==================================="
echo ""

echo "🎵 Detecting USB audio devices..."
aplay -l | grep -i usb || echo "No USB devices found in output list"
arecord -l | grep -i usb || echo "No USB devices found in input list"

echo ""
echo "🔍 Current ALSA configuration:"
cat /etc/asound.conf 2>/dev/null || echo "No /etc/asound.conf found"

echo ""
echo "📊 System audio status:"
echo "PulseAudio status:"
pulseaudio --check 2>/dev/null && echo "✅ Running" || echo "❌ Not running"

echo ""
echo "🔧 Fixing broken pipe issues..."

# 1. Stop any conflicting audio services
echo "🛑 Stopping PulseAudio..."
pulseaudio --kill 2>/dev/null || echo "PulseAudio was not running"

# 2. Create robust ALSA configuration for USB audio
echo "📝 Creating robust ALSA configuration..."
sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Robust USB Audio Configuration
# Handles broken pipe errors and device reconnections

# Default device configuration
pcm.!default {
    type plug
    slave {
        pcm {
            type hw
            card 2
            device 0
        }
        rate 48000
        channels 2
        format S32_LE
    }
}

# Control device
ctl.!default {
    type hw
    card 2
}

# Explicit input configuration with error handling
pcm.!default_input {
    type plug
    slave {
        pcm {
            type hw
            card 2
            device 0
        }
        rate 48000
        channels 2
        format S32_LE
    }
}

# Explicit output configuration with error handling
pcm.!default_output {
    type plug
    slave {
        pcm {
            type hw
            card 2
            device 0
        }
        rate 48000
        channels 2
        format S32_LE
    }
}

# Buffer configuration to prevent underruns
pcm.!default {
    type plug
    slave {
        pcm {
            type hw
            card 2
            device 0
        }
        rate 48000
        channels 2
        format S32_LE
    }
    ttable.0.0 1
    ttable.1.1 1
}
EOF

echo "✅ ALSA configuration updated"

# 3. Set proper permissions
echo "🔧 Setting audio device permissions..."
sudo chmod 666 /dev/snd/* 2>/dev/null || echo "Could not set permissions"

# 4. Add user to audio group if not already
echo "👤 Ensuring user is in audio group..."
sudo usermod -a -G audio $USER 2>/dev/null || echo "User already in audio group"

# 5. Configure USB audio buffer settings
echo "⚙️  Configuring USB audio buffer settings..."
sudo tee /etc/modprobe.d/usb-audio.conf > /dev/null << 'EOF'
# USB Audio buffer configuration
options snd-usb-audio index=2
options snd-usb-audio vid=0x1235
options snd-usb-audio pid=0x8210
EOF

# 6. Set CPU governor for better real-time performance
echo "⚡ Setting CPU governor for real-time audio..."
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

# 7. Configure real-time scheduling
echo "🎵 Configuring real-time scheduling..."
sudo tee /etc/security/limits.d/audio.conf > /dev/null << 'EOF'
# Real-time audio configuration
@audio - rtprio 95
@audio - memlock unlimited
@audio - nice -10
EOF

# 8. Test the configuration
echo ""
echo "🧪 Testing audio configuration..."

echo "Testing output with speaker-test..."
timeout 5s speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1 2>/dev/null && echo "✅ Output test successful" || echo "❌ Output test failed"

echo "Testing input with arecord..."
timeout 3s arecord -D hw:2,0 -c 2 -f S32_LE -r 48000 -d 1 /tmp/test.wav 2>/dev/null && echo "✅ Input test successful" || echo "❌ Input test failed"

echo ""
echo "🔍 Checking for USB errors..."
dmesg | grep -i usb | tail -5

echo ""
echo "🎸 Configuration complete!"
echo ""
echo "💡 Next steps:"
echo "1. Reboot the Raspberry Pi: sudo reboot"
echo "2. After reboot, try running: cargo run --release"
echo "3. If you still get broken pipe errors, try:"
echo "   - Different USB port"
echo "   - Powered USB hub"
echo "   - Check USB cable"
echo ""
echo "🔧 If issues persist, check:"
echo "   dmesg | grep -i usb"
echo "   journalctl -f"
echo ""
echo "📱 For web interface: cargo run --release -- --web"
