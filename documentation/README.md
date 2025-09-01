# Guitar Effects System Documentation

Welcome to the comprehensive documentation for the Guitar Stereo Delay Effects
System. This documentation provides detailed information about the architecture,
features, and usage of this professional real-time audio processing system.

## 📚 Documentation Structure

### Architecture & Design

- **[System Architecture](architecture.md)** - High-level system design and
  component relationships
- **[Audio Processing Pipeline](audio-pipeline.md)** - Detailed audio processing
  flow and algorithms
- **[Platform Support](platform-support.md)** - Cross-platform compatibility and
  optimizations

### Core Components

- **[Audio Processor](components/audio-processor.md)** - Main audio processing
  engine
- **[Stereo Delay Effects](components/stereo-delay.md)** - Advanced stereo delay
  implementation
- **[Distortion Effects](components/distortion.md)** - Cross-feedback distortion
  algorithms
- **[Configuration System](components/configuration.md)** - System configuration
  and platform detection

### Development & Usage

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples & Tutorials](examples.md)** - Code examples and usage tutorials
- **[Performance & Benchmarks](performance.md)** - Performance characteristics
  and optimization
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### Platform-Specific

- **[Raspberry Pi Setup](platforms/raspberry-pi.md)** - Pi-specific setup and
  GPIO integration
- **[macOS Setup](platforms/macos.md)** - macOS audio backend and optimization

## 🎯 Quick Start

For immediate setup and usage, see:

- **[Quick Start Guide](../QUICKSTART.md)** - Get up and running in minutes
- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Basic Usage Examples](examples.md#basic-usage)** - Simple code examples

## 🎛️ Key Features

- **Professional Stereo Delay**: Advanced stereo delay with independent
  left/right channel control
- **Cross-Feedback Distortion**: Musical distortion applied to cross-feedback
  signals
- **Real-Time Processing**: Ultra-low latency audio processing
- **Cross-Platform Support**: Full compatibility with macOS, Linux, and
  Raspberry Pi
- **GPIO Integration**: Physical button controls on Raspberry Pi
- **Interactive CLI**: Menu-driven interface for parameter control

## 🏗️ System Overview

The Guitar Effects System is built with a modular architecture designed for:

- **High Performance**: Optimized Rust implementation for real-time audio
  processing
- **Extensibility**: Modular design allowing easy addition of new effects
- **Cross-Platform**: Unified API across different operating systems
- **Professional Quality**: Studio-grade audio processing algorithms

## 📖 How to Use This Documentation

1. **New Users**: Start with [Quick Start Guide](../QUICKSTART.md) and
   [Basic Usage Examples](examples.md#basic-usage)
2. **Developers**: Review [System Architecture](architecture.md) and
   [API Reference](api-reference.md)
3. **Platform Setup**: See platform-specific guides in the
   [platforms/](platforms/) directory
4. **Troubleshooting**: Check [Troubleshooting](troubleshooting.md) for common
   issues

## 🔗 Related Resources

- **[Main README](../README.md)** - Project overview and quick start
- **[API Documentation](../target/doc/rust_audio_processor/)** - Generated Rust
  documentation
- **[Examples Directory](../examples/)** - Code examples and demonstrations
- **[Benchmarks](../benches/)** - Performance benchmarks

---

_This documentation is maintained alongside the codebase. For the latest
updates, check the
[GitHub repository](https://github.com/your-repo/guitar-effects)._
