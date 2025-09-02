#!/bin/bash

echo "🔍 USB Audio Broken Pipe Diagnostic"
echo "==================================="
echo ""

echo "🎵 USB Audio Devices:"
echo "Output devices:"
aplay -l | grep -i usb || echo "No USB output devices found"
echo ""
echo "Input devices:"
arecord -l | grep -i usb || echo "No USB input devices found"

echo ""
echo "🔧 ALSA Configuration:"
if [ -f /etc/asound.conf ]; then
    echo "✅ /etc/asound.conf exists:"
    cat /etc/asound.conf
else
    echo "❌ No /etc/asound.conf found"
fi

echo ""
echo "📊 System Status:"
echo "PulseAudio:"
pulseaudio --check 2>/dev/null && echo "✅ Running" || echo "❌ Not running"

echo ""
echo "Audio permissions:"
ls -la /dev/snd/ 2>/dev/null || echo "No /dev/snd/ directory"

echo ""
echo "User audio group:"
groups $USER | grep audio && echo "✅ User is in audio group" || echo "❌ User is not in audio group"

echo ""
echo "CPU Governor:"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo ""
echo "🔍 Recent USB errors:"
dmesg | grep -i usb | tail -3

echo ""
echo "💡 Recommended fixes:"
echo "1. Quick fix: ./quick_fix.sh"
echo "2. Full fix: ./fix_usb_audio.sh"
echo "3. Manual: Stop PulseAudio, set ALSA config, reboot"
