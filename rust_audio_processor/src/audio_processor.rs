use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use parking_lot::RwLock;
use crate::delay::BaseDelay;

use crate::config::AudioConfig;
use crate::delay::StereoDelay;
use crate::distortion::DistortionType;
use crate::error::AudioProcessorError;

/// Unified audio processor for guitar stereo delay effects system
pub struct AudioProcessor {
    config: AudioConfig,
    stereo_delay: Arc<Mutex<StereoDelay>>,
    is_running: Arc<RwLock<bool>>,
    audio_thread: Option<thread::JoinHandle<()>>,
}

impl AudioProcessor {
    /// Create a new audio processor with default configuration
    pub fn new() -> Result<Self, AudioProcessorError> {
        let config = AudioConfig::default();
        Self::with_config(config)
    }
    
    /// Create a new audio processor with custom configuration
    pub fn with_config(config: AudioConfig) -> Result<Self, AudioProcessorError> {
        // Validate configuration
        config.validate()?;
        
        // Create stereo delay effect
        let distortion_type = DistortionType::from(config.distortion.distortion_type.as_str());
        let stereo_delay = StereoDelay::new(
            config.sample_rate,
            config.stereo_delay.left_delay,
            config.stereo_delay.right_delay,
            config.stereo_delay.feedback,
            config.stereo_delay.wet_mix,
            config.stereo_delay.ping_pong,
            config.stereo_delay.stereo_width,
            config.stereo_delay.cross_feedback,
            config.distortion.enabled,
            distortion_type,
            config.distortion.drive,
            config.distortion.mix,
        );
        
        Ok(Self {
            config,
            stereo_delay: Arc::new(Mutex::new(stereo_delay)),
            is_running: Arc::new(RwLock::new(false)),
            audio_thread: None,
        })
    }
    
    /// Set stereo delay effect parameter
    pub fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> Result<(), AudioProcessorError> {
        let mut delay = self.stereo_delay.lock().map_err(|_| {
            AudioProcessorError::Threading("Failed to acquire stereo delay lock".to_string())
        })?;
        
        match param {
            "left_delay" => delay.set_left_delay(value),
            "right_delay" => delay.set_right_delay(value),
            "feedback" => delay.set_feedback(value),
            "wet_mix" => delay.set_wet_mix(value),
            "ping_pong" => delay.set_stereo_parameters(Some(value > 0.5), None, None),
            "stereo_width" => delay.set_stereo_parameters(None, Some(value), None),
            "cross_feedback" => delay.set_stereo_parameters(None, None, Some(value)),
            _ => {
                return Err(AudioProcessorError::InvalidParameter {
                    param: param.to_string(),
                    value,
                    min: 0.0,
                    max: 1.0,
                });
            }
        }
        
        Ok(())
    }
    
    /// Process audio through stereo delay effect
    pub fn process_audio(&self, input_audio: &[f32]) -> Result<Vec<f32>, AudioProcessorError> {
        if input_audio.is_empty() {
            return Ok(input_audio.to_vec());
        }
        
        let mut delay = self.stereo_delay.lock().map_err(|_| {
            AudioProcessorError::Threading("Failed to acquire stereo delay lock".to_string())
        })?;
        
        // Process through stereo delay effect
        let (left_output, right_output) = delay.process_mono_to_stereo(input_audio);
        
        // Convert back to mono for now (mix L+R)
        let output_audio: Vec<f32> = left_output
            .iter()
            .zip(right_output.iter())
            .map(|(l, r)| (l + r) * 0.5)
            .collect();
        
        Ok(output_audio)
    }
    
    /// Start audio processing
    pub fn start_audio(&mut self) -> Result<(), AudioProcessorError> {
        if *self.is_running.read() {
            return Err(AudioProcessorError::Processing("Audio already running".to_string()));
        }
        
        let config = self.config.clone();
        let stereo_delay = Arc::clone(&self.stereo_delay);
        let is_running = Arc::clone(&self.is_running);
        
        let thread_handle = thread::spawn(move || {
            if let Err(e) = Self::run_audio_stream(config, stereo_delay, is_running) {
                eprintln!("Audio stream error: {}", e);
            }
        });
        
        self.audio_thread = Some(thread_handle);
        *self.is_running.write() = true;
        
        Ok(())
    }
    
    /// Run the audio stream
    fn run_audio_stream(
        _config: AudioConfig,
        stereo_delay: Arc<Mutex<StereoDelay>>,
        is_running: Arc<RwLock<bool>>,
    ) -> Result<(), AudioProcessorError> {
        let host = cpal::default_host();
        
        println!("🎵 Initializing audio streams...");
        
        // List available devices for debugging
        println!("📋 Available input devices:");
        if let Ok(devices) = host.input_devices() {
            for (i, device) in devices.enumerate() {
                if let Ok(name) = device.name() {
                    println!("  [{}] {}", i, name);
                }
            }
        }
        
        println!("📋 Available output devices:");
        if let Ok(devices) = host.output_devices() {
            for (i, device) in devices.enumerate() {
                if let Ok(name) = device.name() {
                    println!("  [{}] {}", i, name);
                }
            }
        }
        
        // Try to find Scarlett 2i2 specifically with more flexible matching
        let input_device = if let Ok(mut devices) = host.input_devices() {
            devices.find(|device| {
                device.name().map(|name| {
                    let name_lower = name.to_lowercase();
                    println!("🔍 Checking input device: '{}'", name);
                    name_lower.contains("usb") || 
                    name_lower.contains("scarlett") ||
                    name_lower.contains("focusrite") ||
                    name_lower.contains("2i2") ||
                    name_lower.contains("card=usb") ||
                    name_lower.contains("hw:card=usb")
                }).unwrap_or(false)
            }).or_else(|| {
                println!("⚠️  No USB audio input device found, trying default...");
                host.default_input_device()
            })
        } else {
            println!("⚠️  Could not enumerate input devices, using default...");
            host.default_input_device()
        }.ok_or_else(|| {
            println!("❌ No input device available");
            AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
        })?;
            
        let output_device = if let Ok(mut devices) = host.output_devices() {
            devices.find(|device| {
                device.name().map(|name| {
                    let name_lower = name.to_lowercase();
                    println!("🔍 Checking output device: '{}'", name);
                    name_lower.contains("usb") || 
                    name_lower.contains("scarlett") ||
                    name_lower.contains("focusrite") ||
                    name_lower.contains("2i2") ||
                    name_lower.contains("card=usb") ||
                    name_lower.contains("hw:card=usb")
                }).unwrap_or(false)
            }).or_else(|| {
                println!("⚠️  No USB audio output device found, trying default...");
                host.default_output_device()
            })
        } else {
            println!("⚠️  Could not enumerate output devices, using default...");
            host.default_output_device()
        }.ok_or_else(|| {
            println!("❌ No output device available");
            AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
        })?;
        
        println!("🎤 Using input device: {}", input_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        println!("🔊 Using output device: {}", output_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        
        // Get supported configs and ensure format compatibility
        let input_config = input_device.default_input_config()
            .map_err(|e| {
                println!("❌ Failed to get input config: {:?}", e);
                AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
            })?;
        let output_config = output_device.default_output_config()
            .map_err(|e| {
                println!("❌ Failed to get output config: {:?}", e);
                AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
            })?;
        
        println!("🎤 Input config: {:?}", input_config);
        println!("🔊 Output config: {:?}", output_config);
        
        // Create a simple buffer for audio data with size limit
        let audio_buffer = Arc::new(Mutex::new(Vec::<f32>::with_capacity(4096)));
        let audio_buffer_clone = Arc::clone(&audio_buffer);
        
        // Create input stream with format conversion if needed
        let input_stream = if input_config.sample_format() == cpal::SampleFormat::I32 {
            println!("🔄 Converting I32 input to F32 for processing...");
            // Handle I32 input format
            input_device.build_input_stream(
                &input_config.into(),
                move |data: &[i32], _: &cpal::InputCallbackInfo| {
                    // Convert I32 to F32 and process
                    if let Ok(mut delay) = stereo_delay.lock() {
                        if let Ok(mut buffer) = audio_buffer_clone.lock() {
                            // Process stereo input (assuming interleaved LRLR...)
                            for i in (0..data.len()).step_by(2) {
                                let left_input = if i < data.len() { data[i] as f32 / i32::MAX as f32 } else { 0.0 };
                                let right_input = if i + 1 < data.len() { data[i + 1] as f32 / i32::MAX as f32 } else { left_input };
                                
                                let (left_output, right_output) = delay.process_sample(left_input, right_input);
                                
                                // Keep stereo separation and limit buffer size
                                if buffer.len() < 4096 {
                                    buffer.push(left_output);
                                    buffer.push(right_output);
                                }
                            }
                        }
                    }
                },
                move |err| {
                    eprintln!("Audio input error: {}", err);
                },
                None,
            ).map_err(AudioProcessorError::AudioDevice)?
        } else {
            println!("✅ Using F32 input format directly...");
            // Handle F32 input format
            input_device.build_input_stream(
                &input_config.into(),
                move |data: &[f32], _: &cpal::InputCallbackInfo| {
                    // Process input data and send to buffer
                    if let Ok(mut delay) = stereo_delay.lock() {
                        if let Ok(mut buffer) = audio_buffer_clone.lock() {
                            // Process stereo input (assuming interleaved LRLR...)
                            for i in (0..data.len()).step_by(2) {
                                let left_input = if i < data.len() { data[i] } else { 0.0 };
                                let right_input = if i + 1 < data.len() { data[i + 1] } else { left_input };
                                
                                let (left_output, right_output) = delay.process_sample(left_input, right_input);
                                
                                // Keep stereo separation and limit buffer size
                                if buffer.len() < 4096 {
                                    buffer.push(left_output);
                                    buffer.push(right_output);
                                }
                            }
                        }
                    }
                },
                move |err| {
                    eprintln!("Audio input error: {}", err);
                },
                None,
            ).map_err(AudioProcessorError::AudioDevice)?
        };
        
        // Create output stream
        let output_stream = output_device.build_output_stream(
            &output_config.into(),
            move |data: &mut [f32], _: &cpal::OutputCallbackInfo| {
                // Fill output buffer with processed audio from buffer
                if let Ok(mut buffer) = audio_buffer.lock() {
                    for sample in data.iter_mut() {
                        if let Some(processed_sample) = buffer.pop() {
                            *sample = processed_sample;
                        } else {
                            *sample = 0.0; // Silence if no data available
                        }
                    }
                }
            },
            move |err| {
                eprintln!("Audio output error: {}", err);
            },
            None,
        ).map_err(AudioProcessorError::AudioDevice)?;
        
        // Start both streams
        input_stream.play().map_err(AudioProcessorError::AudioStream)?;
        output_stream.play().map_err(AudioProcessorError::AudioStream)?;
        
        println!("🎵 Audio streams started - input and output are now active!");
        
        // Keep the streams alive while running
        while *is_running.read() {
            thread::sleep(Duration::from_millis(100));
        }
        
        Ok(())
    }
    
    /// Run the audio stream with the same device for input and output
    fn run_audio_stream_with_device(
        _config: AudioConfig,
        stereo_delay: Arc<Mutex<StereoDelay>>,
        is_running: Arc<RwLock<bool>>,
        input_device: cpal::Device,
        output_device: cpal::Device,
    ) -> Result<(), AudioProcessorError> {
        println!("🎵 Initializing audio streams with same device...");
        
        // List available devices for debugging
        println!("📋 Available input devices:");
        if let Ok(devices) = cpal::default_host().input_devices() {
            for device in devices {
                if let Ok(name) = device.name() {
                    println!("  - {}", name);
                }
            }
        }
        
        println!("📋 Available output devices:");
        if let Ok(devices) = cpal::default_host().output_devices() {
            for device in devices {
                if let Ok(name) = device.name() {
                    println!("  - {}", name);
                }
            }
        }
        
        println!("🎤 Using input device: {}", input_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        println!("🔊 Using output device: {}", output_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        
        // Get supported configs and ensure format compatibility
        let input_config = input_device.default_input_config()
            .map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        let output_config = output_device.default_output_config()
            .map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        
        println!("🎤 Input config: {:?}", input_config);
        println!("🔊 Output config: {:?}", output_config);
        
        // Create a simple buffer for audio data with size limit
        let audio_buffer = Arc::new(Mutex::new(Vec::<f32>::with_capacity(4096)));
        let audio_buffer_clone = Arc::clone(&audio_buffer);
        
        // Create input stream with format conversion if needed
        let input_stream = if input_config.sample_format() == cpal::SampleFormat::I32 {
            println!("🔄 Converting I32 input to F32 for processing...");
            // Handle I32 input format
            input_device.build_input_stream(
                &input_config.into(),
                move |data: &[i32], _: &cpal::InputCallbackInfo| {
                    // Convert I32 to F32 and process
                    if let Ok(mut delay) = stereo_delay.lock() {
                        if let Ok(mut buffer) = audio_buffer_clone.lock() {
                            // Process stereo input (assuming interleaved LRLR...)
                            for i in (0..data.len()).step_by(2) {
                                let left_input = if i < data.len() { data[i] as f32 / i32::MAX as f32 } else { 0.0 };
                                let right_input = if i + 1 < data.len() { data[i + 1] as f32 / i32::MAX as f32 } else { left_input };
                                
                                let (left_output, right_output) = delay.process_sample(left_input, right_input);
                                
                                // Keep stereo separation and limit buffer size
                                if buffer.len() < 4096 {
                                    buffer.push(left_output);
                                    buffer.push(right_output);
                                }
                            }
                        }
                    }
                },
                move |err| {
                    eprintln!("Audio input error: {}", err);
                },
                None,
            ).map_err(AudioProcessorError::AudioDevice)?
        } else {
            println!("✅ Using F32 input format directly...");
            // Handle F32 input format
            input_device.build_input_stream(
                &input_config.into(),
                move |data: &[f32], _: &cpal::InputCallbackInfo| {
                    // Process input data and send to buffer
                    if let Ok(mut delay) = stereo_delay.lock() {
                        if let Ok(mut buffer) = audio_buffer_clone.lock() {
                            // Process stereo input (assuming interleaved LRLR...)
                            for i in (0..data.len()).step_by(2) {
                                let left_input = if i < data.len() { data[i] } else { 0.0 };
                                let right_input = if i + 1 < data.len() { data[i + 1] } else { left_input };
                                
                                let (left_output, right_output) = delay.process_sample(left_input, right_input);
                                
                                // Keep stereo separation and limit buffer size
                                if buffer.len() < 4096 {
                                    buffer.push(left_output);
                                    buffer.push(right_output);
                                }
                            }
                        }
                    }
                },
                move |err| {
                    eprintln!("Audio input error: {}", err);
                },
                None,
            ).map_err(AudioProcessorError::AudioDevice)?
        };
        
        // Create output stream
        let output_stream = output_device.build_output_stream(
            &output_config.into(),
            move |data: &mut [f32], _: &cpal::OutputCallbackInfo| {
                // Fill output buffer with processed audio from buffer
                if let Ok(mut buffer) = audio_buffer.lock() {
                    for sample in data.iter_mut() {
                        if let Some(processed_sample) = buffer.pop() {
                            *sample = processed_sample;
                        } else {
                            *sample = 0.0; // Silence if no data available
                        }
                    }
                }
            },
            move |err| {
                eprintln!("Audio output error: {}", err);
            },
            None,
        ).map_err(AudioProcessorError::AudioDevice)?;
        
        // Start both streams
        input_stream.play().map_err(AudioProcessorError::AudioStream)?;
        output_stream.play().map_err(AudioProcessorError::AudioStream)?;
        
        println!("🎵 Audio streams started - input and output are now active!");
        
        // Keep the streams alive while running
        while *is_running.read() {
            thread::sleep(Duration::from_millis(100));
        }
        
        Ok(())
    }
    
    /// Stop audio processing
    pub fn stop_audio(&mut self) -> Result<(), AudioProcessorError> {
        *self.is_running.write() = false;
        
        if let Some(thread) = self.audio_thread.take() {
            thread.join().map_err(|_| {
                AudioProcessorError::Threading("Failed to join audio thread".to_string())
            })?;
        }
        
        Ok(())
    }
    
    /// Test audio system with a simple tone
    pub fn test_audio(&self) -> Result<(), AudioProcessorError> {
        // Generate test tone (440Hz A note)
        let duration = 1.0; // 1 second
        let sample_count = (duration * self.config.sample_rate as f32) as usize;
        let mut test_tone = Vec::with_capacity(sample_count);
        
        for i in 0..sample_count {
            let t = i as f32 / self.config.sample_rate as f32;
            let sample = 0.3 * (2.0 * std::f32::consts::PI * 440.0 * t).sin();
            test_tone.push(sample);
        }
        
        // Process through stereo delay effect
        let processed_tone = self.process_audio(&test_tone)?;
        
        // For now, just print that the test completed
        // In a real implementation, you would play the audio
        println!("Audio test completed - processed {} samples", processed_tone.len());
        
        Ok(())
    }
    
    /// Get overall system status
    pub fn get_status(&self) -> Result<std::collections::HashMap<String, String>, AudioProcessorError> {
        let mut status = std::collections::HashMap::new();
        
        status.insert("stereo_delay_active".to_string(), "true".to_string());
        status.insert("audio_running".to_string(), self.is_running.read().to_string());
        
        if let Ok(delay) = self.stereo_delay.lock() {
            status.insert("stereo_delay_info".to_string(), delay.get_info());
        }
        
        Ok(status)
    }
    
    /// Get the current configuration
    pub fn get_config(&self) -> &AudioConfig {
        &self.config
    }
    
    /// Update the configuration
    pub fn update_config(&mut self, new_config: AudioConfig) -> Result<(), AudioProcessorError> {
        new_config.validate()?;
        self.config = new_config;
        Ok(())
    }
}

impl Drop for AudioProcessor {
    fn drop(&mut self) {
        // Ensure audio is stopped when the processor is dropped
        let _ = self.stop_audio();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_audio_processor_creation() {
        let processor = AudioProcessor::new();
        assert!(processor.is_ok());
    }
    
    #[test]
    fn test_audio_processing() {
        let processor = AudioProcessor::new().unwrap();
        let input = vec![0.1, 0.2, 0.3, 0.4, 0.5];
        let output = processor.process_audio(&input).unwrap();
        assert_eq!(output.len(), input.len());
    }
    
    #[test]
    fn test_parameter_setting() {
        let processor = AudioProcessor::new().unwrap();
        let result = processor.set_stereo_delay_parameter("feedback", 0.5);
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_invalid_parameter() {
        let processor = AudioProcessor::new().unwrap();
        let result = processor.set_stereo_delay_parameter("invalid_param", 0.5);
        assert!(result.is_err());
    }
}
