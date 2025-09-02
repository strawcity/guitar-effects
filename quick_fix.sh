#!/bin/bash

echo "🔧 Quick USB Audio Broken Pipe Fix"
echo "=================================="
echo ""

echo "🎵 Current USB audio devices:"
aplay -l | grep -i usb || echo "No USB devices found"

echo ""
echo "🔧 Applying quick fixes..."

# 1. Stop PulseAudio
echo "🛑 Stopping PulseAudio..."
pulseaudio --kill 2>/dev/null || echo "PulseAudio was not running"

# 2. Create simple ALSA config
echo "📝 Creating ALSA configuration..."
sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Simple USB Audio Configuration
pcm.!default {
    type hw
    card 2
    device 0
}

ctl.!default {
    type hw
    card 2
}
EOF

# 3. Set permissions
echo "🔧 Setting audio permissions..."
sudo chmod 666 /dev/snd/* 2>/dev/null || echo "Could not set permissions"

# 4. Add user to audio group
echo "👤 Adding user to audio group..."
sudo usermod -a -G audio $USER 2>/dev/null || echo "User already in audio group"

# 5. Set CPU governor
echo "⚡ Setting CPU governor..."
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

echo ""
echo "✅ Quick fix applied!"
echo ""
echo "💡 Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. Try: cargo run --release"
echo ""
echo "🔧 If still broken pipe errors:"
echo "   - Try different USB port"
echo "   - Use powered USB hub"
echo "   - Check USB cable"
echo "   - Run: ./fix_usb_audio.sh (full fix)"
