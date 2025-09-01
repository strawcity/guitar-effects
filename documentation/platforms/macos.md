# macOS Setup

## Overview

This guide provides comprehensive setup instructions for running the Guitar
Effects System on macOS, including Core Audio integration, Scarlett 2i2
auto-detection, and performance optimization.

## 🍎 Prerequisites

### Hardware Requirements

- **Mac**: macOS 10.15+ (Catalina or later)
- **Audio Interface**: Focusrite Scarlett 2i2 or similar USB audio interface
- **USB Ports**: USB 2.0 or USB 3.0 for audio interface
- **RAM**: 4GB+ recommended for optimal performance

### Software Requirements

- **macOS**: Latest stable version
- **Xcode Command Line Tools**: For building Rust applications
- **Rust**: 1.70+ toolchain
- **Focusrite Drivers**: Latest drivers for Scarlett 2i2

## 🚀 Installation

### Step 1: Install Xcode Command Line Tools

#### Install Command Line Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
gcc --version
clang --version
```

#### Alternative Installation via Xcode

```bash
# If you have Xcode installed, you can install command line tools via Xcode
# Open Xcode → Preferences → Locations → Command Line Tools
```

### Step 2: Install Rust

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

### Step 3: Install Focusrite Drivers

#### Download and Install Drivers

```bash
# Download Focusrite drivers
# Visit: https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-2i2

# Install the downloaded package
# Follow the installation wizard
```

#### Verify Driver Installation

```bash
# Check if Scarlett 2i2 is detected
system_profiler SPAudioDataType | grep -i scarlett

# Check audio devices
cargo run --release -- --list-devices
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

## 🔧 Audio Configuration

### Core Audio Integration

#### Core Audio Settings

```rust
fn setup_core_audio() -> Result<(), AudioProcessorError> {
    // Enable high-latency mode for stability
    set_audio_latency_mode(HighLatency);

    // Configure Core Audio for optimal performance
    configure_core_audio_buffer_size(512);
    configure_core_audio_sample_rate(48000);

    Ok(())
}
```

#### Device Detection

```rust
fn detect_macos_devices() -> Vec<AudioDevice> {
    let mut devices = Vec::new();

    // Priority: Focusrite/Scarlett devices
    if let Some(scarlett) = find_scarlett_device() {
        devices.push(scarlett);
    }

    // Fallback: Built-in audio
    if let Some(builtin) = find_builtin_audio() {
        devices.push(builtin);
    }

    // Additional: Other USB audio devices
    devices.extend(find_usb_audio_devices());

    devices
}

fn find_scarlett_device() -> Option<AudioDevice> {
    let device_names = vec![
        "Scarlett 2i2",
        "Focusrite Scarlett 2i2",
        "Scarlett 2i2 USB",
        "Focusrite USB Audio",
    ];

    for name in device_names {
        if let Some(device) = find_audio_device_by_name(name) {
            return Some(device);
        }
    }

    None
}
```

### macOS-Specific Optimizations

#### High-Latency Mode

```rust
fn configure_macos_audio() -> AudioConfig {
    AudioConfig {
        sample_rate: 48000,           // Higher sample rate for macOS
        buffer_size: 512,             // Smaller buffer for lower latency
        input_device: Some("Scarlett 2i2".to_string()),
        output_device: Some("Scarlett 2i2".to_string()),
        // ... other settings
    }
}
```

#### Performance Configuration

```bash
# Set audio buffer size
defaults write com.apple.audio.AudioServer "IOBufferSize" -int 512

# Restart audio system
sudo killall coreaudiod
```

## 🎛️ Configuration

### macOS-Specific Configuration

```json
{
  "sample_rate": 48000,
  "buffer_size": 512,
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
  },
  "macos": {
    "high_latency_mode": true,
    "core_audio_optimization": true,
    "scarlett_auto_detect": true
  }
}
```

### Environment Variables

```bash
# Set environment variables for optimal performance
export GUITAR_EFFECTS_SAMPLE_RATE=48000
export GUITAR_EFFECTS_BUFFER_SIZE=512
export GUITAR_EFFECTS_INPUT_DEVICE="Scarlett 2i2"
export GUITAR_EFFECTS_OUTPUT_DEVICE="Scarlett 2i2"

# Add to ~/.zshrc for persistence
echo 'export GUITAR_EFFECTS_SAMPLE_RATE=48000' >> ~/.zshrc
echo 'export GUITAR_EFFECTS_BUFFER_SIZE=512' >> ~/.zshrc
```

## 🧪 Testing

### Audio Testing

```bash
# Test audio system
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Test Core Audio
system_profiler SPAudioDataType

# Test Scarlett 2i2 specifically
cargo run --release -- --device "Scarlett 2i2" --test-audio
```

### Performance Testing

```bash
# Monitor system resources
top -o cpu

# Check audio processes
ps aux | grep audio

# Monitor memory usage
vm_stat

# Check CPU usage
iostat
```

## 🔍 Troubleshooting

### Common Issues

#### Permission Issues

```bash
# Grant microphone access
# System Preferences → Security & Privacy → Privacy → Microphone
# Add Terminal or your application to the list

# Reset microphone permissions
tccutil reset Microphone

# Reset audio permissions
sudo killall coreaudiod
```

#### Scarlett 2i2 Not Detected

```bash
# Check USB connection
system_profiler SPUSBDataType | grep -i focusrite

# Check audio devices
system_profiler SPAudioDataType | grep -i scarlett

# Restart audio system
sudo killall coreaudiod
sudo killall AudioServer

# Reinstall Focusrite drivers
# Download from: https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-2i2
```

#### High Latency

```bash
# Adjust buffer size
export GUITAR_EFFECTS_BUFFER_SIZE=256

# Enable high-latency mode
cargo run --release -- --high-latency

# Check system load
top -o cpu
```

#### Audio Dropouts

```bash
# Increase buffer size
export GUITAR_EFFECTS_BUFFER_SIZE=1024

# Enable high-latency mode
cargo run --release -- --high-latency

# Check for other audio applications
ps aux | grep audio
```

### Debug Commands

```bash
# Check system information
uname -a
system_profiler SPHardwareDataType

# Check audio devices
system_profiler SPAudioDataType

# Test Core Audio
cargo run --release -- --test-audio

# Check permissions
tccutil reset Microphone
```

## 📊 Performance Characteristics

### Latency Analysis

- **Input Latency**: 5-8ms
- **Processing Latency**: 1-2ms
- **Output Latency**: 5-8ms
- **Total Round-Trip**: 11-18ms

### CPU Usage

- **Idle State**: 1-2% CPU
- **Active Processing**: 3-5% CPU
- **Peak Processing**: 8-10% CPU

### Memory Usage

- **Base Memory**: 20-30MB
- **Active Memory**: 40-50MB
- **Peak Memory**: 60-70MB

## 🔧 Advanced Configuration

### Audio MIDI Setup

```bash
# Open Audio MIDI Setup
open -a "Audio MIDI Setup"

# Configure Scarlett 2i2 settings
# Set sample rate to 48000 Hz
# Set buffer size to 512 samples
```

### Core Audio Optimization

```bash
# Set optimal Core Audio settings
defaults write com.apple.audio.AudioServer "IOBufferSize" -int 512
defaults write com.apple.audio.AudioServer "SampleRate" -int 48000

# Restart audio system
sudo killall coreaudiod
```

### Performance Monitoring

```bash
# Monitor audio performance
sudo dtruss -p $(pgrep coreaudiod)

# Check audio buffer usage
sudo fs_usage | grep audio

# Monitor system performance
sudo powermetrics --samplers cpu_power -n 1
```

## 🎛️ Scarlett 2i2 Specific Setup

### Hardware Configuration

```bash
# Check Scarlett 2i2 hardware settings
system_profiler SPUSBDataType | grep -A 10 -i focusrite

# Verify USB power
system_profiler SPPowerDataType | grep -i usb
```

### Software Configuration

```bash
# Install Focusrite Control
# Download from: https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-2i2

# Configure Scarlett 2i2 settings
# Set sample rate to 48000 Hz
# Set buffer size to 512 samples
# Enable direct monitoring if needed
```

### Troubleshooting Scarlett 2i2

```bash
# Check if device is recognized
system_profiler SPAudioDataType | grep -i scarlett

# Test device functionality
cargo run --release -- --device "Scarlett 2i2" --test-audio

# Reset device settings
# Use Focusrite Control to reset to factory defaults
```

## 🔮 Advanced Features

### Headless Operation

```bash
# Run without GUI
cargo run --release -- --headless

# Run as background service
nohup cargo run --release > guitar-effects.log 2>&1 &
```

### Network Control

```bash
# Enable network control
cargo run --release -- --network-control

# Access web interface
# http://localhost:8080
```

### Remote Monitoring

```bash
# Enable remote monitoring
cargo run --release -- --remote-monitoring

# Monitor via SSH
ssh user@mac.local "top -o cpu"
```

## 📚 Additional Resources

### Related Documentation

- **[Platform Support](../platform-support.md)** - Cross-platform compatibility
- **[Installation Guide](../installation.md)** - General installation
  instructions
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

### External Resources

- **[macOS Developer Documentation](https://developer.apple.com/documentation/)**
- **[Core Audio Programming Guide](https://developer.apple.com/documentation/coreaudio)**
- **[Focusrite Support](https://focusrite.com/en/support)**

### Community Support

- **[Apple Developer Forums](https://developer.apple.com/forums/)**
- **[GitHub Issues](https://github.com/your-repo/guitar-effects/issues)**
- **[Discord Community](https://discord.gg/guitar-effects)**
