# Configuration System

## Overview

The Configuration System is responsible for managing system settings, platform
detection, audio device management, and effect parameter storage. This component
provides a centralized way to configure the Guitar Effects System across
different platforms and use cases.

## 🏗️ Architecture

### Core Structure

```
Configuration System
├── Platform Detection
│   ├── OS Detection
│   ├── Hardware Detection
│   └── Capability Assessment
├── Audio Device Management
│   ├── Device Detection
│   ├── Device Prioritization
│   └── Device Configuration
├── Effect Parameter Storage
│   ├── Stereo Delay Settings
│   ├── Distortion Settings
│   └── Performance Settings
└── Configuration Persistence
    ├── JSON Configuration Files
    ├── Environment Variables
    └── Platform-Specific Storage
```

### Configuration Flow

```
Platform Detection → Device Discovery → Parameter Loading → System Configuration
       ↓                    ↓                ↓                    ↓
   OS/Hardware         Audio Devices    Effect Settings      Audio Processor
   Detection           Prioritization   Validation         Initialization
```

## 📋 API Reference

### Core Types

#### AudioConfig

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioConfig {
    /// Sample rate in Hz
    pub sample_rate: u32,

    /// Buffer size for audio processing
    pub buffer_size: usize,

    /// Input device name (optional)
    pub input_device: Option<String>,

    /// Output device name (optional)
    pub output_device: Option<String>,

    /// Stereo delay configuration
    pub stereo_delay: StereoDelayConfig,

    /// Distortion configuration
    pub distortion: DistortionConfig,
}
```

#### StereoDelayConfig

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StereoDelayConfig {
    /// Left channel delay time in seconds
    pub left_delay: f32,

    /// Right channel delay time in seconds
    pub right_delay: f32,

    /// Feedback amount (0.0 to 0.9)
    pub feedback: f32,

    /// Wet signal mix (0.0 to 1.0)
    pub wet_mix: f32,

    /// Enable ping-pong delay pattern
    pub ping_pong: bool,

    /// Stereo width enhancement (0.0 to 1.0)
    pub stereo_width: f32,

    /// Cross-feedback between channels (0.0 to 0.5)
    pub cross_feedback: f32,
}
```

#### DistortionConfig

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DistortionConfig {
    /// Enable cross-feedback distortion
    pub enabled: bool,

    /// Type of distortion to apply
    pub distortion_type: String,

    /// Drive amount (0.0 to 1.0)
    pub drive: f32,

    /// Wet/dry mix (0.0 to 1.0)
    pub mix: f32,

    /// How much distortion affects feedback (0.0 to 1.0)
    pub feedback_intensity: f32,
}
```

### Core Methods

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

## 🎯 Detailed Implementation

### Platform Detection

#### OS Detection

```rust
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Platform {
    MacOS,
    Linux,
    RaspberryPi,
    Windows,
    Unknown,
}

impl Platform {
    pub fn detect() -> Self {
        if cfg!(target_os = "macos") {
            Self::MacOS
        } else if cfg!(target_os = "linux") {
            if Self::is_raspberry_pi() {
                Self::RaspberryPi
            } else {
                Self::Linux
            }
        } else if cfg!(target_os = "windows") {
            Self::Windows
        } else {
            Self::Unknown
        }
    }

    fn is_raspberry_pi() -> bool {
        // Check for Raspberry Pi specific files
        std::path::Path::new("/proc/cpuinfo").exists() &&
        std::fs::read_to_string("/proc/cpuinfo")
            .unwrap_or_default()
            .contains("Raspberry Pi")
    }
}
```

#### Platform-Specific Configuration

```rust
impl AudioConfig {
    fn get_platform_defaults(platform: Platform) -> Self {
        match platform {
            Platform::MacOS => Self {
                sample_rate: 48000,           // Higher sample rate for macOS
                buffer_size: 512,             // Smaller buffer for lower latency
                input_device: Some("Scarlett 2i2".to_string()),
                output_device: Some("Scarlett 2i2".to_string()),
                stereo_delay: StereoDelayConfig::default(),
                distortion: DistortionConfig::default(),
            },
            Platform::Linux => Self {
                sample_rate: 44100,           // Standard sample rate
                buffer_size: 256,             // Smaller buffer for low latency
                input_device: None,           // Auto-detect
                output_device: None,          // Auto-detect
                stereo_delay: StereoDelayConfig::default(),
                distortion: DistortionConfig::default(),
            },
            Platform::RaspberryPi => Self {
                sample_rate: 44100,           // Standard sample rate
                buffer_size: 1024,            // Larger buffer for stability
                input_device: Some("USB Audio Device".to_string()),
                output_device: Some("USB Audio Device".to_string()),
                stereo_delay: StereoDelayConfig::default(),
                distortion: DistortionConfig::default(),
            },
            Platform::Windows => Self {
                sample_rate: 44100,           // Standard sample rate
                buffer_size: 512,             // Balanced buffer size
                input_device: None,           // Auto-detect
                output_device: None,          // Auto-detect
                stereo_delay: StereoDelayConfig::default(),
                distortion: DistortionConfig::default(),
            },
            Platform::Unknown => Self::default(),
        }
    }
}
```

### Audio Device Management

#### Device Detection

```rust
impl AudioConfig {
    fn detect_audio_devices(&self, platform: Platform) -> Result<Vec<AudioDevice>, ConfigError> {
        match platform {
            Platform::MacOS => self.detect_macos_devices(),
            Platform::Linux => self.detect_linux_devices(),
            Platform::RaspberryPi => self.detect_pi_devices(),
            Platform::Windows => self.detect_windows_devices(),
            Platform::Unknown => self.detect_generic_devices(),
        }
    }

    fn detect_macos_devices(&self) -> Result<Vec<AudioDevice>, ConfigError> {
        let mut devices = Vec::new();

        // Priority: Focusrite/Scarlett devices
        if let Some(scarlett) = self.find_scarlett_device() {
            devices.push(scarlett);
        }

        // Fallback: Built-in audio
        if let Some(builtin) = self.find_builtin_audio() {
            devices.push(builtin);
        }

        // Additional: Other USB audio devices
        devices.extend(self.find_usb_audio_devices()?);

        Ok(devices)
    }

    fn detect_linux_devices(&self) -> Result<Vec<AudioDevice>, ConfigError> {
        let mut devices = Vec::new();

        // Check USB audio devices first
        if let Ok(usb_devices) = self.find_usb_audio_devices() {
            devices.extend(usb_devices);
        }

        // Add system default devices
        if let Ok(default_devices) = self.find_default_audio_devices() {
            devices.extend(default_devices);
        }

        // Add HDMI audio devices
        if let Ok(hdmi_devices) = self.find_hdmi_audio_devices() {
            devices.extend(hdmi_devices);
        }

        Ok(devices)
    }
}
```

#### Device Prioritization

```rust
impl AudioConfig {
    fn prioritize_devices(&self, devices: Vec<AudioDevice>, platform: Platform) -> Vec<AudioDevice> {
        let mut prioritized = devices;

        match platform {
            Platform::MacOS => {
                // Prioritize Scarlett devices
                prioritized.sort_by(|a, b| {
                    let a_score = self.get_device_priority_score(a, platform);
                    let b_score = self.get_device_priority_score(b, platform);
                    b_score.cmp(&a_score)
                });
            },
            Platform::Linux => {
                // Prioritize USB audio devices
                prioritized.sort_by(|a, b| {
                    let a_score = self.get_device_priority_score(a, platform);
                    let b_score = self.get_device_priority_score(b, platform);
                    b_score.cmp(&a_score)
                });
            },
            Platform::RaspberryPi => {
                // Prioritize USB audio devices
                prioritized.sort_by(|a, b| {
                    let a_score = self.get_device_priority_score(a, platform);
                    let b_score = self.get_device_priority_score(b, platform);
                    b_score.cmp(&a_score)
                });
            },
            _ => {
                // Use default ordering
            },
        }

        prioritized
    }

    fn get_device_priority_score(&self, device: &AudioDevice, platform: Platform) -> u32 {
        let mut score = 0;

        // Base score for device type
        match device.device_type {
            DeviceType::USB => score += 100,
            DeviceType::BuiltIn => score += 50,
            DeviceType::HDMI => score += 30,
            DeviceType::Unknown => score += 10,
        }

        // Platform-specific bonuses
        match platform {
            Platform::MacOS => {
                if device.name.contains("Scarlett") || device.name.contains("Focusrite") {
                    score += 200; // High priority for Scarlett devices
                }
            },
            Platform::Linux | Platform::RaspberryPi => {
                if device.name.contains("USB") {
                    score += 150; // High priority for USB devices
                }
            },
            _ => {},
        }

        // Quality score based on sample rate support
        if device.max_sample_rate >= 48000 {
            score += 50;
        }

        score
    }
}
```

### Configuration Persistence

#### JSON Configuration Files

```rust
impl AudioConfig {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let config: AudioConfig = serde_json::from_str(&content)?;
        Ok(config)
    }

    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> Result<(), Box<dyn std::error::Error>> {
        let json = serde_json::to_string_pretty(self)?;
        std::fs::write(path, json)?;
        Ok(())
    }

    pub fn load_or_default<P: AsRef<Path>>(path: P) -> Self {
        Self::from_file(path).unwrap_or_else(|_| Self::default())
    }
}
```

#### Environment Variables

```rust
impl AudioConfig {
    fn load_from_environment(&mut self) {
        // Load sample rate from environment
        if let Ok(sample_rate) = std::env::var("GUITAR_EFFECTS_SAMPLE_RATE") {
            if let Ok(rate) = sample_rate.parse::<u32>() {
                self.sample_rate = rate;
            }
        }

        // Load buffer size from environment
        if let Ok(buffer_size) = std::env::var("GUITAR_EFFECTS_BUFFER_SIZE") {
            if let Ok(size) = buffer_size.parse::<usize>() {
                self.buffer_size = size;
            }
        }

        // Load input device from environment
        if let Ok(input_device) = std::env::var("GUITAR_EFFECTS_INPUT_DEVICE") {
            self.input_device = Some(input_device);
        }

        // Load output device from environment
        if let Ok(output_device) = std::env::var("GUITAR_EFFECTS_OUTPUT_DEVICE") {
            self.output_device = Some(output_device);
        }
    }
}
```

#### Platform-Specific Storage

```rust
impl AudioConfig {
    fn get_config_path(platform: Platform) -> PathBuf {
        match platform {
            Platform::MacOS => {
                let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("~/.config"));
                path.push("guitar-effects");
                path.push("config.json");
                path
            },
            Platform::Linux => {
                let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("~/.config"));
                path.push("guitar-effects");
                path.push("config.json");
                path
            },
            Platform::RaspberryPi => {
                let mut path = PathBuf::from("/home/pi/.config");
                path.push("guitar-effects");
                path.push("config.json");
                path
            },
            Platform::Windows => {
                let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("C:\\Users\\%USERNAME%\\AppData\\Roaming"));
                path.push("guitar-effects");
                path.push("config.json");
                path
            },
            Platform::Unknown => {
                PathBuf::from("config.json")
            },
        }
    }
}
```

### Parameter Validation

#### Configuration Validation

```rust
impl AudioConfig {
    pub fn validate(&self) -> Result<(), ConfigError> {
        // Validate sample rate
        if !self.is_valid_sample_rate(self.sample_rate) {
            return Err(ConfigError::InvalidSampleRate(self.sample_rate));
        }

        // Validate buffer size
        if !self.is_valid_buffer_size(self.buffer_size) {
            return Err(ConfigError::InvalidBufferSize(self.buffer_size));
        }

        // Validate stereo delay configuration
        self.stereo_delay.validate()?;

        // Validate distortion configuration
        self.distortion.validate()?;

        Ok(())
    }

    fn is_valid_sample_rate(&self, sample_rate: u32) -> bool {
        matches!(sample_rate, 22050 | 44100 | 48000 | 96000 | 192000)
    }

    fn is_valid_buffer_size(&self, buffer_size: usize) -> bool {
        buffer_size >= 256 && buffer_size <= 8192 && buffer_size.is_power_of_two()
    }
}

impl StereoDelayConfig {
    pub fn validate(&self) -> Result<(), ConfigError> {
        // Validate delay times
        if self.left_delay < 0.001 || self.left_delay > 2.0 {
            return Err(ConfigError::InvalidDelayTime("left_delay".to_string(), self.left_delay));
        }

        if self.right_delay < 0.001 || self.right_delay > 2.0 {
            return Err(ConfigError::InvalidDelayTime("right_delay".to_string(), self.right_delay));
        }

        // Validate feedback
        if self.feedback < 0.0 || self.feedback > 0.9 {
            return Err(ConfigError::InvalidFeedback(self.feedback));
        }

        // Validate wet mix
        if self.wet_mix < 0.0 || self.wet_mix > 1.0 {
            return Err(ConfigError::InvalidWetMix(self.wet_mix));
        }

        // Validate cross-feedback
        if self.cross_feedback < 0.0 || self.cross_feedback > 0.5 {
            return Err(ConfigError::InvalidCrossFeedback(self.cross_feedback));
        }

        Ok(())
    }
}
```

## 🔧 Error Handling

### Configuration Errors

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

### Graceful Fallback

```rust
impl AudioConfig {
    fn load_with_fallback<P: AsRef<Path>>(path: P) -> Self {
        // Try to load from file
        if let Ok(config) = Self::from_file(&path) {
            if let Ok(()) = config.validate() {
                return config;
            }
        }

        // Try to load from environment
        let mut config = Self::default();
        config.load_from_environment();

        if let Ok(()) = config.validate() {
            return config;
        }

        // Use platform defaults
        let platform = Platform::detect();
        Self::get_platform_defaults(platform)
    }
}
```

## 📊 Configuration Examples

### Default Configuration

```json
{
  "sample_rate": 44100,
  "buffer_size": 1024,
  "input_device": null,
  "output_device": null,
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
```

### macOS Configuration

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
  }
}
```

### Raspberry Pi Configuration

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

## 🧪 Testing and Validation

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_platform_detection() {
        let platform = Platform::detect();
        assert_ne!(platform, Platform::Unknown);
    }

    #[test]
    fn test_configuration_validation() {
        let config = AudioConfig::default();
        assert!(config.validate().is_ok());
    }

    #[test]
    fn test_invalid_sample_rate() {
        let mut config = AudioConfig::default();
        config.sample_rate = 12345; // Invalid sample rate
        assert!(config.validate().is_err());
    }
}
```

### Integration Tests

```rust
#[test]
fn test_configuration_persistence() {
    let config = AudioConfig::default();
    let temp_path = std::env::temp_dir().join("test_config.json");

    // Save configuration
    config.save_to_file(&temp_path).unwrap();

    // Load configuration
    let loaded_config = AudioConfig::from_file(&temp_path).unwrap();

    // Verify configuration
    assert_eq!(config.sample_rate, loaded_config.sample_rate);
    assert_eq!(config.buffer_size, loaded_config.buffer_size);

    // Clean up
    std::fs::remove_file(temp_path).unwrap();
}
```

## 🔮 Future Enhancements

### Planned Features

1. **Dynamic Configuration**: Runtime configuration updates
2. **Configuration Profiles**: Multiple configuration profiles
3. **Remote Configuration**: Network-based configuration management
4. **Configuration Validation**: Advanced validation rules

### Performance Improvements

1. **Lazy Loading**: Load configuration on demand
2. **Caching**: Cache frequently accessed configuration values
3. **Compression**: Compress configuration files
4. **Incremental Updates**: Update only changed configuration values
