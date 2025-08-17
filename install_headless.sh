#!/bin/bash

# Install Headless Mode for Guitar Arpeggiator
# This script sets up auto-start on boot

echo "🎸 Installing Headless Mode for Guitar Arpeggiator..."
echo "=================================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /sys/firmware/devicetree/base/model 2>/dev/null; then
    echo "❌ This script is designed for Raspberry Pi only!"
    exit 1
fi

echo "✅ Detected Raspberry Pi"

# Get current user
CURRENT_USER=$(whoami)
echo "👤 Current user: $CURRENT_USER"

# Check if we're in the right directory
if [ ! -f "headless_mode.py" ]; then
    echo "❌ Please run this script from the guitar-arpeggiator directory"
    exit 1
fi

# Update service file with correct user path
echo "🔧 Updating service file for user: $CURRENT_USER"
sed -i "s|User=pi|User=$CURRENT_USER|g" guitar-arpeggiator.service
sed -i "s|/home/pi|/home/$CURRENT_USER|g" guitar-arpeggiator.service

# Copy service file to systemd
echo "📁 Installing systemd service..."
sudo cp guitar-arpeggiator.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service to start on boot
echo "✅ Enabling service to start on boot..."
sudo systemctl enable guitar-arpeggiator.service

# Add user to gpio group if it doesn't exist
if ! getent group gpio >/dev/null 2>&1; then
    echo "🔌 Creating gpio group..."
    sudo groupadd gpio
fi

# Add user to gpio group
echo "🔌 Adding user to gpio group..."
sudo usermod -a -G gpio $CURRENT_USER

# Set GPIO permissions
echo "🔌 Setting GPIO permissions..."
sudo usermod -a -G gpio $CURRENT_USER

echo ""
echo "🎉 Headless mode installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. The system will start automatically on boot"
echo "3. Use GPIO buttons to control the arpeggiator:"
echo "   - START button (GPIO 17): Start arpeggiator"
echo "   - STOP button (GPIO 18): Stop arpeggiator"
echo "   - TEMPO UP (GPIO 22): Increase tempo"
echo "   - TEMPO DOWN (GPIO 23): Decrease tempo"
echo ""
echo "🔌 LED Indicators:"
echo "   - C LED (GPIO 12): Chord detection + Tempo up feedback"
echo "   - E LED (GPIO 13): System running status (blinking)"
echo "   - G LED (GPIO 16): Chord detection + Tempo down feedback"
echo ""
echo "📊 Service Management:"
echo "   - Check status: sudo systemctl status guitar-arpeggiator"
echo "   - View logs: sudo journalctl -u guitar-arpeggiator -f"
echo "   - Stop service: sudo systemctl stop guitar-arpeggiator"
echo "   - Start service: sudo systemctl start guitar-arpeggiator"
echo ""
echo "🎯 The system will now:"
echo "   - Start automatically when Pi boots"
echo "   - Wait for START button press"
echo "   - Run without screen interaction"
echo "   - Respond to physical button controls"
echo "   - Show status via LED indicators"
