#!/bin/bash

# Raspberry Pi Setup Script for Rust Audio Processor with Scarlett 2i2
# Run this script on your Raspberry Pi

set -e

echo "🎸 Setting up Rust Audio Processor for Raspberry Pi with Scarlett 2i2"
echo "================================================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Rust
echo "🦀 Installing Rust..."
if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
else
    echo "✅ Rust already installed"
fi

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y \
    build-essential \
    pkg-config \
    libasound2-dev \
    libssl-dev \
    libudev-dev \
    libdbus-1-dev \
    libavahi-client-dev \
    libjack-jackd2-dev \
    libpulse-dev \
    libsndfile1-dev \
    libsamplerate0-dev \
    libfftw3-dev \
    cmake \
    git \
    alsa-utils \
    htop

# Check for Scarlett 2i2
echo "🎛️  Checking for Scarlett 2i2..."
if lsusb | grep -q "Focusrite"; then
    echo "✅ Focusrite Scarlett 2i2 detected"
else
    echo "⚠️  Scarlett 2i2 not detected. Please connect it and run this script again."
    echo "   Or continue if you're using a different audio interface."
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Configure ALSA for Scarlett 2i2
echo "🔧 Configuring ALSA..."
if [ -f /etc/asound.conf ]; then
    echo "⚠️  /etc/asound.conf already exists. Backing up..."
    sudo cp /etc/asound.conf /etc/asound.conf.backup
fi

# Create ALSA configuration
sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Default ALSA configuration for Scarlett 2i2
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

echo "📝 ALSA configuration created. You may need to adjust the card number."
echo "   Run 'aplay -l' to see available audio cards."

# Add user to audio group
echo "👤 Adding user to audio group..."
sudo usermod -a -G audio $USER

# Set performance governor
echo "⚡ Setting CPU performance governor..."
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Test audio setup
echo "🎵 Testing audio setup..."
echo "   This will play a test tone. Press Ctrl+C to stop."

# Check if we can play audio
if command -v speaker-test &> /dev/null; then
    echo "🔊 Playing test tone..."
    speaker-test -D plughw:2,0 -c 2 -t sine -f 440 -l 1 || {
        echo "⚠️  Audio test failed. You may need to adjust the card number in /etc/asound.conf"
        echo "   Run 'aplay -l' to see available cards"
    }
else
    echo "⚠️  speaker-test not available. Skipping audio test."
fi

# Build the project
echo "🔨 Building Rust Audio Processor..."
if [ -d "src" ]; then
    echo "✅ Source code found. Building..."
    cargo build --release
else
    echo "⚠️  Source code not found in current directory."
    echo "   Please run this script from the rust_audio_processor directory."
    exit 1
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/rust-audio-processor.service > /dev/null << EOF
[Unit]
Description=Rust Audio Processor for Guitar Effects
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/target/release/rust_audio_processor
Restart=always
RestartSec=3
Environment=RUST_LOG=info

# Audio group permissions
SupplementaryGroups=audio

# Performance settings
Nice=-10
IOSchedulingClass=realtime

[Install]
WantedBy=multi-user.target
EOF

# Enable service
echo "🚀 Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable rust-audio-processor

echo "✅ Setup complete!"
echo ""
echo "🎛️  Next steps:"
echo "1. Reboot your Pi: sudo reboot"
echo "2. After reboot, start the service: sudo systemctl start rust-audio-processor"
echo "3. Check status: sudo systemctl status rust-audio-processor"
echo "4. View logs: sudo journalctl -u rust-audio-processor -f"
echo ""
echo "🎸 Happy playing!"
