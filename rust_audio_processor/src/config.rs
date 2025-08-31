use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

/// Audio configuration settings
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

/// Stereo delay effect configuration
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

/// Distortion effect configuration
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

impl Default for AudioConfig {
    fn default() -> Self {
        Self {
            sample_rate: 44100,
            buffer_size: 4096,
            input_device: None,
            output_device: None,
            stereo_delay: StereoDelayConfig::default(),
            distortion: DistortionConfig::default(),
        }
    }
}

impl AudioConfig {
    /// Load configuration from a JSON file
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, Box<dyn std::error::Error>> {
        let content = fs::read_to_string(path)?;
        let config: AudioConfig = serde_json::from_str(&content)?;
        Ok(config)
    }
    
    /// Load configuration from file or return default if file doesn't exist
    pub fn load_or_default<P: AsRef<Path>>(path: P) -> Self {
        Self::from_file(path).unwrap_or_else(|_| Self::default())
    }
}

impl Default for StereoDelayConfig {
    fn default() -> Self {
        Self {
            left_delay: 0.3,
            right_delay: 0.6,
            feedback: 0.3,
            wet_mix: 0.6,
            ping_pong: true,
            stereo_width: 0.5,
            cross_feedback: 0.2,
        }
    }
}

impl Default for DistortionConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            distortion_type: "soft_clip".to_string(),
            drive: 0.3,
            mix: 0.7,
            feedback_intensity: 0.5,
        }
    }
}

impl AudioConfig {
    /// Create a new audio configuration with default values
    pub fn new() -> Self {
        Self::default()
    }
    
    /// Create a configuration with custom sample rate
    pub fn with_sample_rate(sample_rate: u32) -> Self {
        Self {
            sample_rate,
            ..Default::default()
        }
    }
    
    /// Validate the configuration
    pub fn validate(&self) -> Result<(), crate::AudioProcessorError> {
        if self.sample_rate < 8000 || self.sample_rate > 192000 {
            return Err(crate::AudioProcessorError::SampleRate(
                format!("Sample rate {} Hz is out of range (8000-192000)", self.sample_rate)
            ));
        }
        
        if self.buffer_size < 64 || self.buffer_size > 16384 {
            return Err(crate::AudioProcessorError::BufferSize(
                format!("Buffer size {} is out of range (64-16384)", self.buffer_size)
            ));
        }
        
        self.stereo_delay.validate()?;
        self.distortion.validate()?;
        
        Ok(())
    }
}

impl StereoDelayConfig {
    /// Validate stereo delay configuration
    pub fn validate(&self) -> Result<(), crate::AudioProcessorError> {
        if !(0.001..=4.0).contains(&self.left_delay) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "left_delay".to_string(),
                value: self.left_delay,
                min: 0.001,
                max: 4.0,
            });
        }
        
        if !(0.001..=4.0).contains(&self.right_delay) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "right_delay".to_string(),
                value: self.right_delay,
                min: 0.001,
                max: 4.0,
            });
        }
        
        if !(0.0..=0.9).contains(&self.feedback) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "feedback".to_string(),
                value: self.feedback,
                min: 0.0,
                max: 0.9,
            });
        }
        
        if !(0.0..=1.0).contains(&self.wet_mix) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "wet_mix".to_string(),
                value: self.wet_mix,
                min: 0.0,
                max: 1.0,
            });
        }
        
        if !(0.0..=1.0).contains(&self.stereo_width) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "stereo_width".to_string(),
                value: self.stereo_width,
                min: 0.0,
                max: 1.0,
            });
        }
        
        if !(0.0..=0.5).contains(&self.cross_feedback) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "cross_feedback".to_string(),
                value: self.cross_feedback,
                min: 0.0,
                max: 0.5,
            });
        }
        
        Ok(())
    }
}

impl DistortionConfig {
    /// Validate distortion configuration
    pub fn validate(&self) -> Result<(), crate::AudioProcessorError> {
        if !(0.0..=1.0).contains(&self.drive) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "drive".to_string(),
                value: self.drive,
                min: 0.0,
                max: 1.0,
            });
        }
        
        if !(0.0..=1.0).contains(&self.mix) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "mix".to_string(),
                value: self.mix,
                min: 0.0,
                max: 1.0,
            });
        }
        
        if !(0.0..=1.0).contains(&self.feedback_intensity) {
            return Err(crate::AudioProcessorError::InvalidParameter {
                param: "feedback_intensity".to_string(),
                value: self.feedback_intensity,
                min: 0.0,
                max: 1.0,
            });
        }
        
        Ok(())
    }
}
