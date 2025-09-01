#!/bin/bash

echo "🎸 Raspberry Pi Audio System Test"
echo "================================="
echo ""

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  This script is designed for Raspberry Pi"
    echo "   Running on: $(uname -a)"
    echo ""
fi

# Test 1: Basic system info
echo "📋 System Information:"
echo "  OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo ""

# Test 2: USB devices
echo "🔌 USB Devices:"
lsusb | grep -i audio || echo "  No USB audio devices found"
echo ""

# Test 3: ALSA devices
echo "🎵 ALSA Audio Devices:"
echo "  Playback devices:"
aplay -l 2>/dev/null || echo "    No playback devices found"
echo ""
echo "  Capture devices:"
arecord -l 2>/dev/null || echo "    No capture devices found"
echo ""

# Test 4: ALSA configuration
echo "⚙️  ALSA Configuration:"
if [ -f /etc/asound.conf ]; then
    echo "  /etc/asound.conf exists:"
    cat /etc/asound.conf | sed 's/^/    /'
else
    echo "  No /etc/asound.conf found"
fi
echo ""

# Test 5: Audio permissions
echo "🔐 Audio Permissions:"
if [ -d /dev/snd ]; then
    echo "  /dev/snd/ contents:"
    ls -la /dev/snd/ | sed 's/^/    /'
else
    echo "  No /dev/snd/ directory found"
fi
echo ""

# Test 6: User audio group
echo "👤 User Audio Group:"
if groups $USER | grep -q audio; then
    echo "  ✅ User $USER is in audio group"
else
    echo "  ❌ User $USER is NOT in audio group"
    echo "  💡 Run: sudo usermod -a -G audio $USER"
fi
echo ""

# Test 7: PulseAudio status
echo "🔊 PulseAudio Status:"
if pulseaudio --check 2>/dev/null; then
    echo "  ⚠️  PulseAudio is running"
    echo "  💡 Consider stopping it: pulseaudio --kill"
else
    echo "  ✅ PulseAudio is not running"
fi
echo ""

# Test 8: Basic audio tests
echo "🧪 Basic Audio Tests:"

# Test output
echo "  Testing output..."
if timeout 3s speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1 >/dev/null 2>&1; then
    echo "    ✅ Output test successful"
else
    echo "    ❌ Output test failed"
    echo "    💡 Try: speaker-test -D default -c 2 -t sine -f 440 -l 1"
fi

# Test input
echo "  Testing input..."
if timeout 3s arecord -D hw:2,0 -c 2 -f S16_LE -r 48000 -d 1 /tmp/test.wav >/dev/null 2>&1; then
    echo "    ✅ Input test successful"
    rm -f /tmp/test.wav
else
    echo "    ❌ Input test failed"
    echo "    💡 Try: arecord -D default -c 2 -f S16_LE -r 48000 -d 1 /tmp/test.wav"
fi
echo ""

# Test 9: Rust audio processor
echo "🦀 Rust Audio Processor Test:"
if command -v cargo >/dev/null 2>&1; then
    echo "  ✅ Cargo is available"
    
    # Check if we're in the right directory
    if [ -f "Cargo.toml" ]; then
        echo "  ✅ In rust_audio_processor directory"
        
        # Test device detection
        echo "  Testing device detection..."
        if cargo run --release --example test_audio_devices >/tmp/device_test.log 2>&1; then
            echo "    ✅ Device detection successful"
            echo "    📋 Device list:"
            grep -E "\[[0-9]+\]" /tmp/device_test.log | head -5 | sed 's/^/      /'
        else
            echo "    ❌ Device detection failed"
            echo "    📋 Error log:"
            tail -10 /tmp/device_test.log | sed 's/^/      /'
        fi
    else
        echo "  ❌ Not in rust_audio_processor directory"
        echo "  💡 Run: cd rust_audio_processor"
    fi
else
    echo "  ❌ Cargo not available"
    echo "  💡 Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi
echo ""

# Test 10: System logs
echo "📊 Recent Audio/USB Logs:"
echo "  Recent USB events:"
dmesg | grep -i usb | tail -3 | sed 's/^/    /' || echo "    No recent USB events"
echo ""
echo "  Recent audio events:"
dmesg | grep -i audio | tail -3 | sed 's/^/    /' || echo "    No recent audio events"
echo ""

# Summary and recommendations
echo "📋 Summary and Recommendations:"
echo ""

if lsusb | grep -q -i audio; then
    echo "✅ USB audio device detected"
else
    echo "❌ No USB audio device detected"
    echo "   - Check USB connections"
    echo "   - Try different USB ports"
    echo "   - Check if device is powered on"
fi

if aplay -l >/dev/null 2>&1; then
    echo "✅ ALSA playback devices available"
else
    echo "❌ No ALSA playback devices"
    echo "   - Run: sudo modprobe snd-usb-audio"
    echo "   - Check: dmesg | grep -i audio"
fi

if groups $USER | grep -q audio; then
    echo "✅ User has audio permissions"
else
    echo "❌ User missing audio permissions"
    echo "   - Run: sudo usermod -a -G audio $USER"
    echo "   - Log out and back in"
fi

if ! pulseaudio --check 2>/dev/null; then
    echo "✅ PulseAudio not interfering"
else
    echo "⚠️  PulseAudio may interfere"
    echo "   - Run: pulseaudio --kill"
fi

echo ""
echo "🎸 Next Steps:"
echo "1. If all tests pass, try: cargo run --release"
echo "2. If tests fail, run: ./fix_audio_io.sh"
echo "3. For detailed diagnostics: cargo run --release --example test_audio_devices"
echo "4. Check the troubleshooting guide: PI_AUDIO_TROUBLESHOOTING.md"
echo ""
echo "🔧 Quick Fix Commands:"
echo "  sudo usermod -a -G audio $USER"
echo "  pulseaudio --kill"
echo "  sudo chmod 666 /dev/snd/*"
echo "  sudo modprobe snd-usb-audio"
echo ""
