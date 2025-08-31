//! Rust Audio Processor for Guitar Stereo Delay Effects System
//! 
//! This crate provides a high-performance audio processing system for guitar effects,
//! specifically designed for stereo delay effects with cross-feedback distortion.

pub mod audio_processor;
pub mod config;
pub mod delay;
pub mod distortion;
pub mod error;
#[cfg(target_os = "linux")]
pub mod alsa_processor;



/// Common trait for audio processors
pub trait AudioProcessorTrait {
    fn start_audio(&mut self) -> std::result::Result<(), AudioProcessorError>;
    fn stop_audio(&mut self) -> std::result::Result<(), AudioProcessorError>;
    fn test_audio(&self) -> std::result::Result<(), AudioProcessorError>;
    fn get_status(&self) -> std::result::Result<std::collections::HashMap<String, String>, AudioProcessorError>;
    fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> std::result::Result<(), AudioProcessorError>;
}

// Implement the trait for AudioProcessor
impl AudioProcessorTrait for audio_processor::AudioProcessor {
    fn start_audio(&mut self) -> std::result::Result<(), AudioProcessorError> {
        self.start_audio()
    }
    
    fn stop_audio(&mut self) -> std::result::Result<(), AudioProcessorError> {
        self.stop_audio()
    }
    
    fn test_audio(&self) -> std::result::Result<(), AudioProcessorError> {
        self.test_audio()
    }
    
    fn get_status(&self) -> std::result::Result<std::collections::HashMap<String, String>, AudioProcessorError> {
        self.get_status()
    }
    
    fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> std::result::Result<(), AudioProcessorError> {
        self.set_stereo_delay_parameter(param, value)
    }
}

// Implement the trait for AlsaAudioProcessor (Linux only)
#[cfg(target_os = "linux")]
impl AudioProcessorTrait for alsa_processor::AlsaAudioProcessor {
    fn start_audio(&mut self) -> std::result::Result<(), AudioProcessorError> {
        self.start_audio()
    }
    
    fn stop_audio(&mut self) -> std::result::Result<(), AudioProcessorError> {
        self.stop_audio()
    }
    
    fn test_audio(&self) -> std::result::Result<(), AudioProcessorError> {
        self.test_audio()
    }
    
    fn get_status(&self) -> std::result::Result<std::collections::HashMap<String, String>, AudioProcessorError> {
        // Simple status for ALSA processor
        let mut status = std::collections::HashMap::new();
        status.insert("processor_type".to_string(), "ALSA".to_string());
        status.insert("audio_running".to_string(), "false".to_string()); // We'll need to track this
        Ok(status)
    }
    
    fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> std::result::Result<(), AudioProcessorError> {
        self.set_stereo_delay_parameter(param, value)
    }
    
    fn set_distortion_type(&self, distortion_type: &str) -> std::result::Result<(), AudioProcessorError> {
        self.set_distortion_type(distortion_type)
    }
}

// Re-export commonly used types
pub use audio_processor::AudioProcessor;
pub use delay::StereoDelay;
pub use distortion::{DistortionType, CrossFeedbackDistortion};
pub use config::AudioConfig;
pub use error::AudioProcessorError;
