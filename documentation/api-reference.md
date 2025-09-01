# API Reference

## Overview

This document provides a comprehensive API reference for the Guitar Effects
System, including all public interfaces, types, and methods available for
developers.

## 📋 Core Types

### AudioProcessor

```rust
pub struct AudioProcessor {
    // Private fields
}

impl AudioProcessor {
    /// Create a new audio processor with configuration
    pub fn new(config: AudioConfig) -> Result<Self, AudioProcessorError>;

    /// Create with default settings
    pub fn new_default() -> Result<Self, AudioProcessorError>;

    /// Create with platform-specific optimizations
    pub fn new_with_platform(platform: Platform) -> Result<Self, AudioProcessorError>;
}
```

### StereoDelay

```rust
pub struct StereoDelay {
    // Private fields
}

impl StereoDelay {
    /// Create a new stereo delay with configuration
    pub fn new(config: DelayConfig) -> Self;

    /// Create with default settings
    pub fn new_default() -> Self;

    /// Create with custom sample rate
    pub fn new_with_sample_rate(sample_rate: u32, config: DelayConfig) -> Self;
}
```

### DistortionEffect

```rust
pub struct DistortionEffect {
    // Private fields
}

impl DistortionEffect {
    /// Create a new distortion effect
    pub fn new(distortion_type: DistortionType, drive: f32, mix: f32, sample_rate: u32) -> Self;

    /// Create with default settings
    pub fn new_default(sample_rate: u32) -> Self;
}
```

## 🎛️ Audio Control API

### AudioProcessor Methods

#### Initialization and Control

```rust
impl AudioProcessor {
    /// Start audio processing
    pub fn start_audio(&mut self) -> Result<(), AudioProcessorError>;

    /// Stop audio processing
    pub fn stop_audio(&mut self) -> Result<(), AudioProcessorError>;

    /// Test audio system
    pub fn test_audio(&self) -> Result<(), AudioProcessorError>;

    /// Get system status
    pub fn get_status(&self) -> Result<HashMap<String, String>, AudioProcessorError>;

    /// Reset all effects
    pub fn reset_effects(&mut self) -> Result<(), AudioProcessorError>;
}
```

#### Parameter Control

```rust
impl AudioProcessor {
    /// Set stereo delay parameter
    pub fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> Result<(), AudioProcessorError>;

    /// Get stereo delay parameter
    pub fn get_stereo_delay_parameter(&self, param: &str) -> Result<f32, AudioProcessorError>;

    /// Set distortion type
    pub fn set_distortion_type(&self, distortion_type: &str) -> Result<(), AudioProcessorError>;

    /// Get distortion type
    pub fn get_distortion_type(&self) -> Result<String, AudioProcessorError>;

    /// Set distortion drive
    pub fn set_distortion_drive(&self, drive: f32) -> Result<(), AudioProcessorError>;

    /// Get distortion drive
    pub fn get_distortion_drive(&self) -> Result<f32, AudioProcessorError>;

    /// Reset delay buffers
    pub fn reset_delay(&self) -> Result<(), AudioProcessorError>;

    /// Update all parameters
    pub fn update_parameters(&mut self) -> Result<(), AudioProcessorError>;
}
```

#### Device Management

```rust
impl AudioProcessor {
    /// List available audio devices
    pub fn list_devices(&self) -> Result<Vec<AudioDevice>, AudioProcessorError>;

    /// Set input device
    pub fn set_input_device(&mut self, device_name: &str) -> Result<(), AudioProcessorError>;

    /// Set output device
    pub fn set_output_device(&mut self, device_name: &str) -> Result<(), AudioProcessorError>;

    /// Get current input device
    pub fn get_input_device(&self) -> Result<Option<String>, AudioProcessorError>;

    /// Get current output device
    pub fn get_output_device(&self) -> Result<Option<String>, AudioProcessorError>;
}
```

## 🎛️ Stereo Delay API

### StereoDelay Methods

#### Processing

```rust
impl StereoDelay {
    /// Process stereo input to stereo output
    pub fn process(&mut self, left_input: f32, right_input: f32) -> (f32, f32);

    /// Process entire buffer
    pub fn process_buffer(&mut self, left_input: &[f32], right_input: &[f32]) -> (Vec<f32>, Vec<f32>);

    /// Process mono input to stereo output
    pub fn process_mono(&mut self, input: f32) -> (f32, f32);

    /// Reset delay buffers
    pub fn reset(&mut self);
}
```

#### Parameter Control

```rust
impl StereoDelay {
    /// Set left channel delay time
    pub fn set_left_delay(&mut self, delay_time: f32);

    /// Set right channel delay time
    pub fn set_right_delay(&mut self, delay_time: f32);

    /// Get left channel delay time
    pub fn get_left_delay(&self) -> f32;

    /// Get right channel delay time
    pub fn get_right_delay(&self) -> f32;

    /// Set feedback amount
    pub fn set_feedback(&mut self, feedback: f32);

    /// Get feedback amount
    pub fn get_feedback(&self) -> f32;

    /// Set wet mix
    pub fn set_wet_mix(&mut self, wet_mix: f32);

    /// Get wet mix
    pub fn get_wet_mix(&self) -> f32;

    /// Enable/disable ping-pong
    pub fn set_ping_pong(&mut self, enabled: bool);

    /// Get ping-pong status
    pub fn get_ping_pong(&self) -> bool;

    /// Set stereo width
    pub fn set_stereo_width(&mut self, width: f32);

    /// Get stereo width
    pub fn get_stereo_width(&self) -> f32;

    /// Set cross-feedback amount
    pub fn set_cross_feedback(&mut self, amount: f32);

    /// Get cross-feedback amount
    pub fn get_cross_feedback(&self) -> f32;
}
```

#### Advanced Features

```rust
impl StereoDelay {
    /// Set tempo-synchronized delay
    pub fn set_tempo_sync(&mut self, bpm: f32, note_division: f32);

    /// Set modulation parameters
    pub fn set_modulation(&mut self, rate: f32, depth: f32);

    /// Get modulation rate
    pub fn get_modulation_rate(&self) -> f32;

    /// Get modulation depth
    pub fn get_modulation_depth(&self) -> f32;
}
```

## 🎛️ Distortion API

### DistortionEffect Methods

#### Processing

```rust
impl DistortionEffect {
    /// Process a single sample through distortion
    pub fn process(&mut self, input: f32) -> f32;

    /// Process entire buffer
    pub fn process_buffer(&mut self, input: &[f32]) -> Vec<f32>;

    /// Process stereo input
    pub fn process_stereo(&mut self, left: f32, right: f32) -> (f32, f32);

    /// Reset distortion state
    pub fn reset(&mut self);
}
```

#### Parameter Control

```rust
impl DistortionEffect {
    /// Set the type of distortion
    pub fn set_distortion_type(&mut self, distortion_type: DistortionType);

    /// Get the type of distortion
    pub fn get_distortion_type(&self) -> DistortionType;

    /// Set the drive amount
    pub fn set_drive(&mut self, drive: f32);

    /// Get the drive amount
    pub fn get_drive(&self) -> f32;

    /// Set the wet/dry mix
    pub fn set_mix(&mut self, mix: f32);

    /// Get the wet/dry mix
    pub fn get_mix(&self) -> f32;

    /// Set bit crushing parameters
    pub fn set_bit_crush_parameters(&mut self, bit_depth: u8, sample_rate_reduction: f32);

    /// Get bit depth
    pub fn get_bit_depth(&self) -> u8;

    /// Get sample rate reduction
    pub fn get_sample_rate_reduction(&self) -> f32;
}
```

## 🎛️ Configuration API

### AudioConfig Methods

#### Configuration Management

```rust
impl AudioConfig {
    /// Load configuration from a JSON file
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, Box<dyn std::error::Error>>;

    /// Load configuration from file or return default if file doesn't exist
    pub fn load_or_default<P: AsRef<Path>>(path: P) -> Self;

    /// Save configuration to a JSON file
    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> Result<(), Box<dyn std::error::Error>>;

    /// Validate configuration parameters
    pub fn validate(&self) -> Result<(), ConfigError>;
}
```

#### Platform Detection

```rust
impl AudioConfig {
    /// Detect platform and apply platform-specific settings
    pub fn detect_platform() -> Platform;

    /// Get platform-specific default configuration
    pub fn get_platform_defaults(platform: Platform) -> Self;

    /// Apply platform-specific optimizations
    pub fn apply_platform_optimizations(&mut self, platform: Platform);
}
```

## 🎛️ Error Types

### AudioProcessorError

```rust
#[derive(Debug, thiserror::Error)]
pub enum AudioProcessorError {
    #[error("Device not found: {0}")]
    DeviceNotFound(String),

    #[error("Stream initialization failed: {0}")]
    StreamInitError(String),

    #[error("Buffer underrun: {0}")]
    BufferUnderrun(String),

    #[error("Buffer overrun: {0}")]
    BufferOverrun(String),

    #[error("Invalid parameter: {param} = {value}")]
    InvalidParameter { param: String, value: f32 },

    #[error("Platform error: {0}")]
    PlatformError(String),
}
```

### ConfigError

```rust
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("Invalid sample rate: {0}")]
    InvalidSampleRate(u32),

    #[error("Invalid buffer size: {0}")]
    InvalidBufferSize(usize),

    #[error("Invalid delay time for {param}: {value}")]
    InvalidDelayTime { param: String, value: f32 },

    #[error("Invalid feedback amount: {0}")]
    InvalidFeedback(f32),

    #[error("Invalid wet mix: {0}")]
    InvalidWetMix(f32),

    #[error("Invalid cross-feedback: {0}")]
    InvalidCrossFeedback(f32),

    #[error("Device not found: {0}")]
    DeviceNotFound(String),

    #[error("Configuration file error: {0}")]
    FileError(String),
}
```

## 🎛️ Enums and Constants

### DistortionType

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DistortionType {
    SoftClip,
    HardClip,
    Tube,
    Fuzz,
    BitCrush,
    Waveshaper,
    None,
}
```

### Platform

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Platform {
    MacOS,
    Linux,
    RaspberryPi,
    Windows,
    Unknown,
}
```

### Constants

```rust
// Sample rates
pub const SAMPLE_RATE_22050: u32 = 22050;
pub const SAMPLE_RATE_44100: u32 = 44100;
pub const SAMPLE_RATE_48000: u32 = 48000;
pub const SAMPLE_RATE_96000: u32 = 96000;
pub const SAMPLE_RATE_192000: u32 = 192000;

// Buffer sizes
pub const BUFFER_SIZE_256: usize = 256;
pub const BUFFER_SIZE_512: usize = 512;
pub const BUFFER_SIZE_1024: usize = 1024;
pub const BUFFER_SIZE_2048: usize = 2048;
pub const BUFFER_SIZE_4096: usize = 4096;

// Parameter ranges
pub const MIN_DELAY_TIME: f32 = 0.001;
pub const MAX_DELAY_TIME: f32 = 2.0;
pub const MIN_FEEDBACK: f32 = 0.0;
pub const MAX_FEEDBACK: f32 = 0.9;
pub const MIN_WET_MIX: f32 = 0.0;
pub const MAX_WET_MIX: f32 = 1.0;
pub const MIN_CROSS_FEEDBACK: f32 = 0.0;
pub const MAX_CROSS_FEEDBACK: f32 = 0.5;
```

## 🎛️ Traits

### AudioProcessorTrait

```rust
pub trait AudioProcessorTrait {
    fn start_audio(&mut self) -> Result<(), AudioProcessorError>;
    fn stop_audio(&mut self) -> Result<(), AudioProcessorError>;
    fn test_audio(&self) -> Result<(), AudioProcessorError>;
    fn get_status(&self) -> Result<HashMap<String, String>, AudioProcessorError>;
    fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> Result<(), AudioProcessorError>;
    fn set_distortion_type(&self, distortion_type: &str) -> Result<(), AudioProcessorError>;
    fn reset_delay(&self) -> Result<(), AudioProcessorError>;
}
```

### BaseDelay

```rust
pub trait BaseDelay {
    fn get_effect_name(&self) -> &str;
    fn process_sample(&mut self, input_sample: f32) -> (f32, f32);
    fn process_buffer(&mut self, input_buffer: &[f32]) -> Vec<(f32, f32)>;
    fn reset(&mut self);
    fn set_delay_time(&mut self, delay_time: f32);
    fn set_feedback(&mut self, feedback: f32);
    fn set_wet_mix(&mut self, wet_mix: f32);
}
```

## 🎛️ Utility Functions

### Device Management

```rust
/// List all available audio devices
pub fn list_audio_devices() -> Result<Vec<AudioDevice>, AudioProcessorError>;

/// Find audio device by name
pub fn find_audio_device_by_name(name: &str) -> Option<AudioDevice>;

/// Get default audio device
pub fn get_default_audio_device() -> Result<AudioDevice, AudioProcessorError>;
```

### Platform Utilities

```rust
/// Detect current platform
pub fn detect_platform() -> Platform;

/// Get platform-specific configuration path
pub fn get_config_path(platform: Platform) -> PathBuf;

/// Apply platform-specific optimizations
pub fn apply_platform_optimizations(platform: Platform) -> Result<(), AudioProcessorError>;
```

### Performance Monitoring

```rust
/// Get current latency
pub fn get_current_latency() -> Duration;

/// Get CPU usage percentage
pub fn get_cpu_usage() -> f32;

/// Get memory usage in bytes
pub fn get_memory_usage() -> usize;

/// Get performance statistics
pub fn get_performance_stats() -> PerformanceStats;
```

## 🎛️ Examples

### Basic Usage

```rust
use rust_audio_processor::{AudioProcessor, AudioConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create configuration
    let config = AudioConfig::default();

    // Create audio processor
    let mut processor = AudioProcessor::new(config)?;

    // Start audio processing
    processor.start_audio()?;

    // Set parameters
    processor.set_stereo_delay_parameter("left_delay", 0.3)?;
    processor.set_stereo_delay_parameter("feedback", 0.4)?;

    // Stop audio processing
    processor.stop_audio()?;

    Ok(())
}
```

### Advanced Usage

```rust
use rust_audio_processor::{StereoDelay, DelayConfig, DistortionEffect, DistortionType};

fn main() {
    // Create stereo delay
    let config = DelayConfig {
        left_delay: 0.3,
        right_delay: 0.6,
        feedback: 0.3,
        wet_mix: 0.6,
        ping_pong: true,
        stereo_width: 0.3,
        cross_feedback: 0.2,
    };

    let mut stereo_delay = StereoDelay::new(config);

    // Create distortion effect
    let mut distortion = DistortionEffect::new(
        DistortionType::Tube,
        0.4,
        0.7,
        44100,
    );

    // Process audio
    let (left_out, right_out) = stereo_delay.process(0.5, 0.3);
    let distorted_left = distortion.process(left_out);
    let distorted_right = distortion.process(right_out);

    println!("Output: left={}, right={}", distorted_left, distorted_right);
}
```

## 📚 Additional Resources

### Related Documentation

- **[Examples & Tutorials](examples.md)** - Code examples and usage tutorials
- **[System Architecture](architecture.md)** - System design and component
  relationships
- **[Installation Guide](installation.md)** - Installation instructions

### External Resources

- **[Rust Documentation](https://doc.rust-lang.org/)**
- **[CPAL Documentation](https://docs.rs/cpal/)**
- **[Serde Documentation](https://serde.rs/)**
