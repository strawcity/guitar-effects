#!/bin/bash
# Fix USB audio issues on Raspberry Pi for Scarlett 2i2

echo "🔧 Fixing USB audio issues for Scarlett 2i2..."
echo "This script will add the necessary parameter to /boot/cmdline.txt"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "Run: sudo ./fix_usb_audio.sh"
    exit 1
fi

# Check if the fix is already applied
if grep -q "dwc_otg.fiq_fsm_enable=0" /boot/firmware/cmdline.txt; then
    echo "✅ USB audio fix is already applied!"
    echo "Current cmdline.txt:"
    cat /boot/firmware/cmdline.txt
    exit 0
fi

# Backup the original file
cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.backup
echo "✅ Backed up original cmdline.txt to /boot/firmware/cmdline.txt.backup"

# Add the fix parameter
echo "📝 Adding dwc_otg.fiq_fsm_enable=0 to cmdline.txt..."
echo "dwc_otg.fiq_fsm_enable=0" >> /boot/firmware/cmdline.txt

# Show the result
echo ""
echo "✅ USB audio fix applied!"
echo ""
echo "New cmdline.txt:"
cat /boot/cmdline.txt
echo ""
echo "⚠️  IMPORTANT: You must reboot for this to take effect!"
echo ""
echo "To reboot now, run: sudo reboot"
echo "Or reboot later with: sudo reboot"
echo ""
echo "After rebooting, test your Scarlett 2i2 with:"
echo "python test_audio_setup.py"
