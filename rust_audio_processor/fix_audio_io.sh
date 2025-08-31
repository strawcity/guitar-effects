#!/bin/bash

echo "🔧 Audio I/O Error Diagnostic and Fix Script"
echo "============================================="

echo "📋 Current ALSA configuration:"
cat /etc/asound.conf 2>/dev/null || echo "No /etc/asound.conf found"

echo ""
echo "🎵 Available audio devices:"
aplay -l

echo ""
echo "🎤 Available input devices:"
arecord -l

echo ""
echo "🔍 Checking Scarlett 2i2 supported formats..."
echo "Supported output formats:"
amixer -c 2 sget 'USB Audio' 2>/dev/null || echo "Could not get output format info"

echo ""
echo "Supported input formats:"
amixer -c 2 sget 'USB Audio' 2>/dev/null || echo "Could not get input format info"

echo ""
echo "🔍 Checking PulseAudio status:"
pulseaudio --check 2>/dev/null && echo "PulseAudio is running" || echo "PulseAudio is not running"

echo ""
echo "⚡ Checking audio permissions:"
ls -la /dev/snd/ 2>/dev/null || echo "No /dev/snd/ directory found"

echo ""
echo "👤 Current user audio group membership:"
groups $USER | grep audio && echo "✅ User is in audio group" || echo "❌ User is not in audio group"

echo ""
echo "🔧 Attempting to fix common issues..."

# Stop PulseAudio if it's running to avoid conflicts
echo "🛑 Stopping PulseAudio to avoid conflicts..."
pulseaudio --kill 2>/dev/null || echo "PulseAudio was not running"

# Create a simple ALSA configuration that bypasses PulseAudio
echo "📝 Creating ALSA configuration to bypass PulseAudio..."
sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Direct ALSA configuration bypassing PulseAudio
pcm.!default {
    type plug
    slave.pcm {
        type hw
        card 2
        device 0
    }
    slave.format S16_LE
    slave.rate 48000
    slave.channels 2
}

ctl.!default {
    type hw
    card 2
}
EOF

echo "✅ ALSA configuration updated"

# Test audio with simple commands
echo ""
echo "🧪 Testing audio with simple commands..."

echo "Testing output with speaker-test..."
timeout 3s speaker-test -D default -c 2 -t sine -f 440 -l 1 2>/dev/null && echo "✅ Output test successful" || echo "❌ Output test failed"

echo "Testing input with arecord..."
timeout 3s arecord -D default -c 2 -f S16_LE -r 48000 -d 1 /tmp/test.wav 2>/dev/null && echo "✅ Input test successful" || echo "❌ Input test failed"

echo ""
echo "🎸 Now try running the Rust audio processor:"
echo "cargo run --release"
echo "Then type: start"
echo ""
echo "💡 If you still get I/O errors, try:"
echo "1. Reboot the Raspberry Pi"
echo "2. Check that the Scarlett 2i2 is properly connected"
echo "3. Try different USB ports"
echo "4. Check dmesg for USB errors: dmesg | grep -i usb"
