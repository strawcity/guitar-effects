# 🎸 Guitar Stereo Delay Effects System

A professional real-time guitar stereo delay effects processing system featuring
advanced stereo delay algorithms. This system provides rich, spatial delay
effects with independent left/right channel control and ultra-low latency
processing.

**Project Structure:**

- `src/` - Rust source code and audio processing implementation
- `examples/` - Example applications and demonstrations
- `benches/` - Performance benchmarks
- `Cargo.toml` - Rust project configuration and dependencies

## Features

### 🎛️ **Professional Stereo Delay Effect**

- **Stereo Delay**: Advanced stereo delay with independent left/right channel
  control, ping-pong patterns, and stereo width enhancement
- **Cross-feedback**: Allows delays to feed back between left and right channels
  for complex spatial effects
- **Cross-feedback Distortion**: Applies various distortion types to
  cross-feedback signals for musical feedback patterns
- **Real-time Control**: Adjust all parameters during playback for dynamic
  performance

### ⚙️ **System Features**

- **Configurable Parameters**: Adjustable delay time (0.1-2.0s), feedback
  (0.0-0.9), and wet mix (0.0-1.0)
- **Stereo Processing**: All effects output in stereo with spatial separation
  and width control
- **Cross-Platform Support**: Full compatibility with macOS, Linux, and
  Raspberry Pi
- **Real-time Audio Processing**: Ultra-low-latency audio processing using
  optimized audio processor
- **Smart Audio Detection**: Platform-specific audio device detection and
  optimization
- **Interactive CLI**: Menu-driven interface for easy effect control and
  parameter adjustment

## System Architecture

The project features a high-performance Rust implementation optimized for
real-time audio processing:

### 🦀 **Rust Audio Processor**

A high-performance Rust implementation offering:

- **Ultra-low latency** audio processing
- **Optimized performance** for real-time applications
- **Cross-platform audio I/O** using CPAL
- **Professional-grade** audio processing algorithms
- **Production-ready** implementation

### 🎯 **Core Components**

1. **Audio Processor** (`src/audio_processor.rs`): Main audio processing engine
2. **Delay Effects** (`src/delay.rs`): Stereo delay implementation
3. **Distortion Effects** (`src/distortion.rs`): Various distortion algorithms
4. **Configuration** (`src/config.rs`): System configuration and platform
   detection
5. **Main Application** (`src/main.rs`): Application entry point and CLI
   interface

## Installation

### Prerequisites

- **Rust 1.70+** (latest stable recommended)
- **Audio Interface**: USB audio interface (e.g., Focusrite Scarlett 2i2) for
  best results
- **Raspberry Pi**: Pi 3B+ or Pi 4 recommended for optimal performance
- **System Dependencies**: ALSA (Linux/Pi), Core Audio (macOS), or WASAPI
  (Windows)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guitar-effects
```

### 2. Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 3. Build the Project

```bash
cargo build --release
```

### 4. Raspberry Pi Specific Setup

If running on Raspberry Pi, additional setup is required:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libasound2-dev

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Build the project
cargo build --release

# Add user to audio group
sudo usermod -a -G audio $USER

# Fix USB audio issues (IMPORTANT for Scarlett 2i2)
sudo nano /boot/firmware/cmdline.txt
# Add "dwc_otg.fiq_fsm_enable=0" to the end of the line

# Reboot to apply all changes
sudo reboot
```

## Stereo Delay Effects

The guitar effects system includes a professional-quality stereo delay effect
with advanced features:

### 🎯 **Stereo Delay Effect**

```rust
use rust_audio_processor::delay::{StereoDelay, DelayConfig};

// Advanced stereo delay with ping-pong, width enhancement, and cross-feedback distortion
let config = DelayConfig {
    left_delay: 0.3,      // Left channel delay time
    right_delay: 0.6,     // Right channel delay time
    feedback: 0.3,        // Feedback amount
    wet_mix: 0.6,         // Wet signal mix
    ping_pong: true,      // Enable ping-pong pattern
    stereo_width: 0.5,    // Stereo width enhancement
    cross_feedback: 0.2,  // Cross-feedback between channels
    cross_feedback_distortion: true,  // Enable distortion on cross-feedback
    distortion_type: DistortionType::SoftClip,  // Type of distortion
    distortion_drive: 0.3,  // Distortion drive amount
    distortion_mix: 0.7     // Distortion wet/dry mix
};

let mut stereo_delay = StereoDelay::new(config);

// Process stereo input to stereo output
let (left_output, right_output) = stereo_delay.process(left_input, right_input);
```

### 🎛️ **Cross-Feedback Distortion**

The stereo delay includes advanced cross-feedback distortion that applies
various distortion types to the cross-feedback signals, creating musical and
interesting feedback patterns:

```rust
use rust_audio_processor::delay::{StereoDelay, DelayConfig, DistortionType};

// Create stereo delay with cross-feedback distortion
let config = DelayConfig {
    // ... other parameters ...
    cross_feedback_distortion: true,
    distortion_type: DistortionType::Tube,  // Available: SoftClip, HardClip, Tube, Fuzz, BitCrush, Waveshaper
    distortion_drive: 0.4,  // Drive amount (0.0 to 1.0)
    distortion_mix: 0.8     // Wet/dry mix (0.0 to 1.0)
};

let mut stereo_delay = StereoDelay::new(config);

// Control distortion parameters in real-time
stereo_delay.set_cross_feedback_distortion(
    DistortionType::Fuzz,
    0.6,  // drive
    0.9,  // mix
    0.7   // feedback_intensity
);
```

**Available Distortion Types:**

- **SoftClip**: Musical tanh-based soft clipping
- **HardClip**: Aggressive hard clipping with threshold control
- **Tube**: Asymmetric tube-style distortion simulation
- **Fuzz**: Aggressive fuzz with harmonic enhancement
- **BitCrush**: Digital bit depth and sample rate reduction
- **Waveshaper**: Custom cubic polynomial waveshaping

### 🚀 **Quick Start**

```bash
# Build the project
cargo build --release

# Run the main application
cargo run --release

# Run examples
cargo run --example distortion_demo
cargo run --example basic_usage
```

### 📚 **Documentation**

- **API Documentation**: `cargo doc --open`
- **Examples**: See `examples/`
- **Real-time Control**: Parameter adjustment during playback

## Platform-Specific Features

### macOS

- **Audio Backend**: Core Audio with Scarlett 2i2 auto-detection
- **Optimizations**: High-latency mode for stability
- **Device Priority**: Focusrite/Scarlett audio interfaces

### Raspberry Pi

- **Audio Backend**: ALSA with hardware acceleration
- **Optimizations**: Performance CPU governor, audio group permissions
- **Device Priority**: USB audio devices, built-in audio

### Linux (Other)

- **Audio Backend**: Default system audio
- **Optimizations**: Standard audio settings
- **Device Priority**: System default devices

## Usage

### Basic Usage

#### Interactive Mode (with screen)

Run the main system:

```bash
cargo run --release
```

Or use the interactive CLI (keyboard control on a connected monitor):

```bash
cargo run --release -- --interactive
```

Interactive CLI commands:

```
start | stop | status
delay <type>   (basic, tape, multi, tempo, stereo)
time <seconds> | feedback <0-0.9> | wet <0-1.0>
effects | demo
quit
```

The system will:

1. **Auto-detect platform** and apply optimizations
2. **Detect audio devices** based on platform priorities
3. **Start stereo delay processing** immediately
4. **Begin real-time processing** with guitar input

### Platform-Specific Behavior

#### macOS

- Automatically detects Scarlett 2i2 or similar audio interfaces
- Uses Core Audio with high-latency mode for stability
- Maintains all existing functionality

#### Raspberry Pi

- **Audio Optimization**: ALSA backend with hardware acceleration

### Interactive Commands

Once running, you can use these commands:

```bash
# Start the application
cargo run --release

# Use interactive mode
cargo run --release -- --interactive

# Set parameters via command line
cargo run --release -- --left-delay 0.4 --right-delay 0.8 --feedback 0.5
```

### CLI Options

```bash
# Available command line options
cargo run --release -- --help

# Example with all parameters
cargo run --release -- \
  --left-delay 0.3 \
  --right-delay 0.6 \
  --feedback 0.4 \
  --wet-mix 0.7 \
  --ping-pong \
  --cross-feedback 0.2 \
  --distortion-type tube \
  --distortion-drive 0.5
```

### Stereo Delay Features

- **Independent left/right delays**: Set different delay times for each channel
- **Ping-pong patterns**: Creates bouncing delay effects between channels
- **Stereo width enhancement**: Expands the stereo image using mid-side
  processing
- **Cross-feedback**: Allows delays to feed back between left and right channels
- **Real-time control**: Adjust all parameters during playback

## Testing

Run the test suite to verify all components work correctly:

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_stereo_delay

# Run benchmarks
cargo bench
```

### 🧪 **Test Coverage**

**Unit Tests**:

- Configuration and platform detection
- Audio device detection and initialization
- Stereo delay effect functionality
- Distortion algorithms
- Parameter validation and clipping

**Integration Tests**:

- End-to-end audio processing pipeline
- Real-time parameter adjustment
- Cross-platform compatibility
- Performance benchmarks

## Audio Setup

### Device Detection

The system automatically detects and prioritizes audio devices based on
platform:

**macOS Priority:**

1. Focusrite/Scarlett audio interfaces
2. Built-in audio
3. Other USB audio devices

**Raspberry Pi Priority:**

1. USB audio devices (Scarlett 2i2, etc.)
2. Built-in audio
3. HDMI audio

**Linux Priority:**

1. System default devices
2. USB audio devices
3. Built-in audio

### Troubleshooting

#### Common Issues

**No Audio Output:**

```bash
# Check audio devices
cargo run --release -- --list-devices

# Test audio system
cargo run --release -- --test-audio

# Check audio group membership (Linux/Pi)
groups $USER
```

**High Latency:**

```bash
# Run with optimized settings
cargo run --release -- --low-latency

# Check system audio settings
# (Platform-specific audio configuration)
```

### Platform-Specific Debugging

#### Raspberry Pi

```bash
# Test audio system
cargo run --release -- --list-devices

# Check audio group membership
groups $USER

# Test audio processing
cargo run --release -- --test-audio
```

#### macOS

```bash
# Check audio devices
cargo run --release -- --list-devices

# Test Core Audio
cargo run --release -- --test-audio

# Run with verbose output
cargo run --release -- --verbose
```

#### Linux

```bash
# Check ALSA devices
cargo run --release -- --list-devices

# Test audio system
cargo run --release -- --test-audio

# Run with debug output
RUST_LOG=debug cargo run --release
```

## Development

### Adding New Effects

To add a new effect:

1. Create a new module in `src/effects/`
2. Implement the `Effect` trait
3. Add the effect to the main system's effect selection
4. Update the CLI to support the new effect

## Future Development

The guitar stereo delay effects system is designed for continuous expansion and
enhancement:

### 🚀 **Planned Effects Packages**

- **Reverb Effects**: Room, hall, plate, and spring reverb algorithms
- **Distortion & Overdrive**: Tube, fuzz, and modern distortion models
- **Modulation Effects**: Chorus, flanger, phaser, and tremolo
- **Filtering & EQ**: Dynamic filters, parametric EQ, and envelope followers
- **Compression & Dynamics**: Multi-band compression and limiting

### 🎛️ **System Enhancements**

- **Effect Chains**: Configurable effect routing and signal flow
- **MIDI Integration**: External MIDI control and synchronization
- **Preset Management**: Save and recall effect configurations
- **Real-time Visualization**: Audio spectrum and effect parameter displays
- **Multi-channel Processing**: Support for stereo and surround sound

### 🔧 **Integration Features**

- **Plugin Architecture**: Modular effect loading system
- **Audio Interface Support**: Extended device compatibility
- **Network Control**: Remote control via web interface or mobile app
- **Recording Integration**: Direct-to-DAW recording capabilities

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
