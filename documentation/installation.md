# Installation Guide

## Overview

This guide provides detailed installation instructions for the Guitar Effects
System across all supported platforms. Follow the platform-specific instructions
for your system.

## 📋 Prerequisites

### System Requirements

#### Minimum Requirements

- **CPU**: 1.5 GHz dual-core processor
- **RAM**: 2 GB RAM
- **Storage**: 100 MB free space
- **Audio**: USB audio interface (recommended) or built-in audio
- **OS**: macOS 10.15+, Ubuntu 18.04+, or Raspberry Pi OS

#### Recommended Requirements

- **CPU**: 2.5 GHz quad-core processor
- **RAM**: 4 GB RAM
- **Storage**: 500 MB free space
- **Audio**: Focusrite Scarlett 2i2 or similar USB audio interface
- **OS**: Latest stable version

### Required Software

#### Rust Toolchain

- **Rust**: 1.70+ (latest stable recommended)
- **Cargo**: Included with Rust installation
- **Build Tools**: Platform-specific build dependencies

#### Platform Dependencies

**macOS**:

- Xcode Command Line Tools
- Core Audio (built-in)

**Linux**:

- Build essentials
- ALSA development libraries
- pkg-config

**Raspberry Pi**:

- Build essentials
- ALSA development libraries
- GPIO libraries (optional)

## 🍎 macOS Installation

### Step 1: Install Rust

#### Using rustup (Recommended)

```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts and select option 1 (default installation)

# Reload shell environment
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

#### Using Homebrew (Alternative)

```bash
# Install Rust using Homebrew
brew install rust

# Verify installation
rustc --version
cargo --version
```

### Step 2: Install Build Dependencies

#### Install Xcode Command Line Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
gcc --version
```

### Step 3: Clone and Build

#### Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-repo/guitar-effects.git
cd guitar-effects

# Verify repository
ls -la
```

#### Build the Project

```bash
# Build in release mode for optimal performance
cargo build --release

# Verify build
ls -la target/release/
```

### Step 4: Test Installation

#### Test Audio System

```bash
# Test audio system
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Run basic example
cargo run --example basic_usage
```

### Step 5: Configure Audio (Optional)

#### Set Up Scarlett 2i2

```bash
# Check if Scarlett 2i2 is detected
cargo run --release -- --list-devices

# If not detected, install Focusrite drivers
# Download from: https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-2i2
```

## 🐧 Linux Installation

### Step 1: Install Rust

#### Using rustup (Recommended)

```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts and select option 1 (default installation)

# Reload shell environment
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

#### Using Package Manager (Alternative)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install rustc cargo

# Fedora
sudo dnf install rust cargo

# Arch Linux
sudo pacman -S rust

# Verify installation
rustc --version
cargo --version
```

### Step 2: Install Build Dependencies

#### Ubuntu/Debian

```bash
# Install build essentials
sudo apt update
sudo apt install build-essential pkg-config

# Install ALSA development libraries
sudo apt install libasound2-dev

# Install additional dependencies
sudo apt install libssl-dev libudev-dev
```

#### Fedora

```bash
# Install build tools
sudo dnf groupinstall "Development Tools"

# Install ALSA development libraries
sudo dnf install alsa-lib-devel

# Install additional dependencies
sudo dnf install openssl-devel systemd-devel
```

#### Arch Linux

```bash
# Install build tools
sudo pacman -S base-devel

# Install ALSA development libraries
sudo pacman -S alsa-lib

# Install additional dependencies
sudo pacman -S openssl systemd
```

### Step 3: Clone and Build

#### Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-repo/guitar-effects.git
cd guitar-effects

# Verify repository
ls -la
```

#### Build the Project

```bash
# Build in release mode for optimal performance
cargo build --release

# Verify build
ls -la target/release/
```

### Step 4: Configure Audio Permissions

#### Add User to Audio Group

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Log out and log back in for changes to take effect
```

#### Fix Audio Device Permissions

```bash
# Fix audio device permissions
sudo chmod 666 /dev/snd/*

# Make permissions persistent
echo 'KERNEL=="snd*", MODE="0666"' | sudo tee /etc/udev/rules.d/99-audio.rules

# Reload udev rules
sudo udevadm control --reload-rules
```

### Step 5: Test Installation

#### Test Audio System

```bash
# Test audio system
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Test ALSA
speaker-test -c 2 -t sine

# Run basic example
cargo run --example basic_usage
```

## 🍓 Raspberry Pi Installation

### Step 1: Prepare Raspberry Pi

#### Update System

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget
```

### Step 2: Install Rust

#### Install Rust Using rustup

```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts and select option 1 (default installation)

# Reload shell environment
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

### Step 3: Install Build Dependencies

#### Install Required Packages

```bash
# Install build essentials
sudo apt install -y build-essential pkg-config

# Install ALSA development libraries
sudo apt install -y libasound2-dev

# Install additional dependencies
sudo apt install -y libssl-dev libudev-dev
```

### Step 4: Configure Audio

#### Add User to Audio Group

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Verify group membership
groups $USER
```

#### Fix USB Audio Issues

```bash
# Add USB audio fix to cmdline.txt
echo 'dwc_otg.fiq_fsm_enable=0' | sudo tee -a /boot/firmware/cmdline.txt

# Reboot to apply changes
sudo reboot
```

### Step 5: Clone and Build

#### Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-repo/guitar-effects.git
cd guitar-effects

# Verify repository
ls -la
```

#### Build the Project

```bash
# Build in release mode for optimal performance
cargo build --release

# Verify build
ls -la target/release/
```

### Step 6: Configure GPIO (Optional)

#### Install GPIO Libraries

```bash
# Install GPIO libraries
sudo apt install -y python3-gpiozero

# Or install WiringPi
sudo apt install -y wiringpi
```

#### Test GPIO

```bash
# Test GPIO access
gpio readall

# Test specific GPIO pin
gpio -g mode 17 out
gpio -g write 17 1
gpio -g write 17 0
```

### Step 7: Test Installation

#### Test Audio System

```bash
# Test audio system
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Test ALSA
speaker-test -c 2 -t sine

# Run basic example
cargo run --example basic_usage
```

## 🔧 Post-Installation Configuration

### Audio Device Configuration

#### Configure Default Audio Device

```bash
# List available audio devices
cargo run --release -- --list-devices

# Test specific device
cargo run --release -- --device "Scarlett 2i2" --test-audio
```

#### Create Configuration File

```bash
# Create configuration directory
mkdir -p ~/.config/guitar-effects

# Create default configuration
cat > ~/.config/guitar-effects/config.json << EOF
{
  "sample_rate": 44100,
  "buffer_size": 1024,
  "input_device": "Scarlett 2i2",
  "output_device": "Scarlett 2i2",
  "stereo_delay": {
    "left_delay": 0.3,
    "right_delay": 0.6,
    "feedback": 0.3,
    "wet_mix": 0.6,
    "ping_pong": true,
    "stereo_width": 0.3,
    "cross_feedback": 0.2
  },
  "distortion": {
    "enabled": true,
    "distortion_type": "tube",
    "drive": 0.4,
    "mix": 0.7,
    "feedback_intensity": 0.5
  }
}
EOF
```

### Performance Optimization

#### Linux/Raspberry Pi Optimization

```bash
# Set real-time priority limit
ulimit -r 95

# Make real-time priority permanent
echo '* soft rtprio 95' | sudo tee -a /etc/security/limits.conf
echo '* hard rtprio 95' | sudo tee -a /etc/security/limits.conf

# Set performance CPU governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make CPU governor permanent
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
```

#### macOS Optimization

```bash
# Set audio buffer size
defaults write com.apple.audio.AudioServer "IOBufferSize" -int 512

# Restart audio system
sudo killall coreaudiod
```

## 🧪 Testing Installation

### Basic Functionality Test

```bash
# Test basic functionality
cargo run --release -- --test-audio

# Expected output: "Audio test passed"
```

### Audio Device Test

```bash
# List audio devices
cargo run --release -- --list-devices

# Expected output: List of available audio devices
```

### Performance Test

```bash
# Run performance test
cargo run --release -- --benchmark

# Expected output: Performance metrics
```

### Example Programs

```bash
# Run basic usage example
cargo run --example basic_usage

# Run distortion demo
cargo run --example distortion_demo

# Run audio device test
cargo run --example test_audio_devices
```

## 🔍 Troubleshooting Installation

### Common Issues

#### Rust Installation Issues

```bash
# If rustup fails, try manual installation
curl -O https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init
chmod +x rustup-init
./rustup-init
```

#### Build Dependencies Issues

```bash
# On Ubuntu/Debian, install additional dependencies
sudo apt install -y libssl-dev libudev-dev pkg-config

# On Fedora, install additional dependencies
sudo dnf install -y openssl-devel systemd-devel pkgconfig
```

#### Audio Permission Issues

```bash
# Fix audio permissions
sudo chmod 666 /dev/snd/*

# Add user to audio group
sudo usermod -a -G audio $USER

# Log out and log back in
```

#### USB Audio Issues (Raspberry Pi)

```bash
# Add USB audio fix
echo 'dwc_otg.fiq_fsm_enable=0' | sudo tee -a /boot/firmware/cmdline.txt

# Reboot to apply changes
sudo reboot
```

### Verification Commands

```bash
# Verify Rust installation
rustc --version
cargo --version

# Verify build dependencies
pkg-config --version
gcc --version

# Verify audio system
aplay -l  # Linux/Pi
system_profiler SPAudioDataType  # macOS

# Verify project build
cargo build --release
ls -la target/release/
```

## 📚 Next Steps

### After Installation

1. **Read the Quick Start Guide**: `../QUICKSTART.md`
2. **Explore Examples**: `../examples/`
3. **Check Documentation**: `docs/`
4. **Test with Your Guitar**: Connect your guitar and test the effects

### Learning Resources

- **[System Architecture](architecture.md)**: Understand the system design
- **[Examples & Tutorials](examples.md)**: Learn through examples
- **[API Reference](api-reference.md)**: Complete API documentation
- **[Troubleshooting](troubleshooting.md)**: Solve common issues

### Getting Help

- **Check Troubleshooting Guide**: `docs/troubleshooting.md`
- **Run Diagnostics**: `cargo run --release -- --diagnostics`
- **Check System Logs**: Platform-specific log locations
- **Report Issues**: Include platform, error messages, and diagnostic output
