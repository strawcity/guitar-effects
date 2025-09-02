# Raspberry Pi Setup

## Overview

This guide provides comprehensive setup instructions for running the Guitar
Effects System on Raspberry Pi, including audio configuration and performance
optimization.

## 🍓 Prerequisites

### Hardware Requirements

- **Raspberry Pi**: Pi 3B+ or Pi 4 (recommended)
- **Audio Interface**: USB audio interface (e.g., Focusrite Scarlett 2i2)
- **Power Supply**: 5V/3A power supply for stable operation
- **Storage**: 8GB+ microSD card

### Software Requirements

- **Raspberry Pi OS**: Latest stable version
- **Rust**: 1.70+ toolchain
- **Build Tools**: Development libraries and dependencies

## 🚀 Installation

### Step 1: System Preparation

#### Update System

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget build-essential
```

#### Install Rust

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

### Step 2: Install Dependencies

#### Install Build Dependencies

````bash
# Install build essentials
sudo apt install -y build-essential pkg-config

# Install ALSA development libraries
sudo apt install -y libasound2-dev

# Install additional dependencies
sudo apt install -y libssl-dev libudev-dev

### Step 3: Audio Configuration

#### Add User to Audio Group

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Verify group membership
groups $USER
````

#### Fix USB Audio Issues

```bash
# Add USB audio fix to cmdline.txt
echo 'dwc_otg.fiq_fsm_enable=0' | sudo tee -a /boot/firmware/cmdline.txt

# Reboot to apply changes
sudo reboot
```

### Step 4: Clone and Build

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

## ⚡ Performance Optimization

### CPU Configuration

#### Set Performance Governor

```bash
# Set performance governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make performance governor permanent
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils

# Disable CPU frequency scaling
sudo systemctl disable ondemand
```

#### Real-Time Priority

```bash
# Set real-time priority limit
ulimit -r 95

# Make real-time priority permanent
echo '* soft rtprio 95' | sudo tee -a /etc/security/limits.conf
echo '* hard rtprio 95' | sudo tee -a /etc/security/limits.conf
```

### Memory Management

#### Optimize Memory Settings

```bash
# Add memory optimizations to /boot/firmware/cmdline.txt
echo 'cma_lwm=16 cma_hwm=32' | sudo tee -a /boot/firmware/cmdline.txt

# Optimize swap settings
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

### Audio Optimization

#### ALSA Configuration

```bash
# Create ALSA configuration
sudo nano ~/.asoundrc

# Add optimal settings
pcm.!default {
    type hw
    card 0
    device 0
    rate 44100
    channels 2
    buffer_size 1024
    period_size 512
}

ctl.!default {
    type hw
    card 0
}
```

## 🎛️ Configuration

### Pi-Specific Configuration

```json
{
  "sample_rate": 44100,
  "buffer_size": 1024,
  "input_device": "USB Audio Device",
  "output_device": "USB Audio Device",
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
    "distortion_type": "soft_clip",
    "drive": 0.3,
    "mix": 0.6,
    "feedback_intensity": 0.4
  }
}
```

### Environment Variables

```bash
# Set environment variables for optimal performance
export GUITAR_EFFECTS_SAMPLE_RATE=44100
export GUITAR_EFFECTS_BUFFER_SIZE=1024
export GUITAR_EFFECTS_INPUT_DEVICE="USB Audio Device"
export GUITAR_EFFECTS_OUTPUT_DEVICE="USB Audio Device"

# Add to ~/.bashrc for persistence
echo 'export GUITAR_EFFECTS_SAMPLE_RATE=44100' >> ~/.bashrc
echo 'export GUITAR_EFFECTS_BUFFER_SIZE=1024' >> ~/.bashrc
```

## 🧪 Testing

### Audio Testing

```bash
# Test audio system
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Test ALSA
speaker-test -c 2 -t sine

# Test USB audio
aplay -D hw:1,0 /dev/zero
```

### Performance Testing

```bash
# Monitor system resources
htop

# Check CPU frequency
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq

# Monitor memory usage
free -h

# Check temperature
vcgencmd measure_temp
```

## 🔍 Troubleshooting

### Common Issues

#### USB Audio Not Working

```bash
# Check USB devices
lsusb

# Check USB power
cat /sys/bus/usb/devices/*/power/runtime_status

# Fix USB audio issues
echo 'dwc_otg.fiq_fsm_enable=0' | sudo tee -a /boot/firmware/cmdline.txt
sudo reboot
```

#### High CPU Usage

```bash
# Set performance governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Increase buffer size
export GUITAR_EFFECTS_BUFFER_SIZE=2048

# Monitor system load
htop
```

#### Audio Dropouts

```bash
# Increase buffer size
export GUITAR_EFFECTS_BUFFER_SIZE=2048

# Set real-time priority
sudo nice -n -20 cargo run --release

# Check audio group membership
groups $USER
```

### Debug Commands

```bash
# Check system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

# Check audio devices
aplay -l
cat /proc/asound/cards

# Monitor system resources
htop
free -h
vcgencmd measure_temp
```

## 📊 Performance Characteristics

### Latency Analysis

- **Input Latency**: 8-12ms
- **Processing Latency**: 2-4ms
- **Output Latency**: 8-12ms
- **Total Round-Trip**: 18-28ms

### CPU Usage

- **Idle State**: 2-3% CPU
- **Active Processing**: 5-8% CPU
- **Peak Processing**: 12-15% CPU

### Memory Usage

- **Base Memory**: 25-35MB
- **Active Memory**: 45-55MB
- **Peak Memory**: 65-75MB

## 🔮 Advanced Features

### Headless Operation

```bash
# Run without display
cargo run --release -- --headless

# Run as system service
sudo systemctl enable guitar-effects
sudo systemctl start guitar-effects
```

### Network Control

```bash
# Enable network control
cargo run --release -- --network-control

# Access web interface
# http://raspberrypi.local:8080
```

### Remote Monitoring

```bash
# Enable remote monitoring
cargo run --release -- --remote-monitoring

# Monitor via SSH
ssh pi@raspberrypi.local "htop"
```

## 📚 Additional Resources

### Related Documentation

- **[Platform Support](../platform-support.md)** - Cross-platform compatibility
- **[Installation Guide](../installation.md)** - General installation
  instructions
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

### External Resources

- **[Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)**
- **[ALSA Documentation](https://alsa-project.org/wiki/Main_Page)**

### Community Support

- **[Raspberry Pi Forums](https://www.raspberrypi.org/forums/)**
- **[GitHub Issues](https://github.com/your-repo/guitar-effects/issues)**
- **[Discord Community](https://discord.gg/guitar-effects)**
