//! Rust Audio Processor for Guitar Stereo Delay Effects System
//! 
//! This crate provides a high-performance audio processing system for guitar effects,
//! specifically designed for stereo delay effects with cross-feedback distortion.

pub mod audio_processor;
pub mod alsa_processor;
pub mod delay;
pub mod distortion;
pub mod config;
pub mod error;

pub use audio_processor::AudioProcessor;
pub use delay::StereoDelay;
pub use distortion::{DistortionType, CrossFeedbackDistortion};
pub use config::AudioConfig;
pub use error::AudioProcessorError;

/// Re-export commonly used types
pub type Result<T> = std::result::Result<T, AudioProcessorError>;
