use thiserror::Error;

/// Custom error types for the audio processor
#[derive(Error, Debug)]
pub enum AudioProcessorError {
    #[error("Audio device error: {0}")]
    AudioDevice(#[from] cpal::BuildStreamError),
    
    #[error("Audio stream error: {0}")]
    AudioStream(#[from] cpal::PlayStreamError),
    
    #[error("Invalid parameter: {param} = {value} (expected range: {min}..={max})")]
    InvalidParameter {
        param: String,
        value: f32,
        min: f32,
        max: f32,
    },
    
    #[error("Buffer size error: {0}")]
    BufferSize(String),
    
    #[error("Sample rate error: {0}")]
    SampleRate(String),
    
    #[error("Threading error: {0}")]
    Threading(String),
    
    #[error("Configuration error: {0}")]
    Configuration(String),
    
    #[error("Processing error: {0}")]
    Processing(String),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

impl From<&str> for AudioProcessorError {
    fn from(err: &str) -> Self {
        AudioProcessorError::Unknown(err.to_string())
    }
}

impl From<String> for AudioProcessorError {
    fn from(err: String) -> Self {
        AudioProcessorError::Unknown(err)
    }
}
