#!/bin/bash

# Raspberry Pi Setup Script for Guitar Effects
# This script automates the setup process for Raspberry Pi

echo "🎸 Setting up Guitar Effects on Raspberry Pi..."
echo "=================================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /sys/firmware/devicetree/base/model 2>/dev/null; then
    echo "❌ This script is designed for Raspberry Pi only!"
    exit 1
fi

echo "✅ Detected Raspberry Pi"

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y python3-pip python3-dev python3-venv
sudo apt-get install -y libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install -y libffi-dev libssl-dev git

# Install GPIO library
echo "🔌 Installing GPIO library..."
pip3 install RPi.GPIO

# Add user to audio group
echo "🎵 Adding user to audio group..."
sudo usermod -a -G audio $USER

# Set audio permissions
echo "🔊 Setting audio permissions..."
sudo chmod 666 /dev/snd/* 2>/dev/null || true

# Set CPU governor to performance for better audio performance
echo "⚡ Setting CPU governor to performance..."
if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the guitar effects: python main.py"
echo ""
echo "🔌 GPIO Pin Layout:"
echo "   Start Button: GPIO 17"
echo "   Stop Button: GPIO 18"
echo "   Tempo Up: GPIO 22"
echo "   Tempo Down: GPIO 23"
echo ""
echo "📖 See README.md for detailed wiring instructions"
