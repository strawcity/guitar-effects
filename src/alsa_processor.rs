use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use parking_lot::RwLock;
use crate::delay::BaseDelay;
use crate::config::AudioConfig;
use crate::delay::StereoDelay;
use crate::distortion::DistortionType;
use crate::error::AudioProcessorError;
#[cfg(target_os = "linux")]
use alsa::{pcm::{PCM, Format, HwParams}, Direction, ValueOr};

#[cfg(target_os = "linux")]
/// ALSA-based audio processor for direct hardware access
pub struct AlsaAudioProcessor {
    config: AudioConfig,
    stereo_delay: Arc<Mutex<StereoDelay>>,
    is_running: Arc<RwLock<bool>>,
    audio_thread: Option<thread::JoinHandle<()>>,
}

#[cfg(target_os = "linux")]
impl AlsaAudioProcessor {
    /// Create a new ALSA audio processor with default configuration
    pub fn new() -> Result<Self, AudioProcessorError> {
        let config = AudioConfig::default();
        Self::with_config(config)
    }
    
    /// Create a new ALSA audio processor with custom configuration
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
    
    /// Start ALSA audio processing
    pub fn start_audio(&mut self) -> Result<(), AudioProcessorError> {
        if *self.is_running.read() {
            return Err(AudioProcessorError::Processing("Audio already running".to_string()));
        }
        
        let config = self.config.clone();
        let stereo_delay = Arc::clone(&self.stereo_delay);
        let is_running = Arc::clone(&self.is_running);
        
        let thread_handle = thread::spawn(move || {
            if let Err(e) = Self::run_alsa_audio_stream(config, stereo_delay, is_running) {
                eprintln!("ALSA audio stream error: {}", e);
            }
        });
        
        self.audio_thread = Some(thread_handle);
        *self.is_running.write() = true;
        
        Ok(())
    }
    
    /// Stop ALSA audio processing
    pub fn stop_audio(&mut self) -> Result<(), AudioProcessorError> {
        if !*self.is_running.read() {
            return Err(AudioProcessorError::Processing("Audio not running".to_string()));
        }
        
        *self.is_running.write() = false;
        
        if let Some(thread_handle) = self.audio_thread.take() {
            thread_handle.join().map_err(|_| {
                AudioProcessorError::Threading("Failed to join audio thread".to_string())
            })?;
        }
        
        // Reset delay buffers to clear any lingering feedback
        self.reset_delay()?;
        
        Ok(())
    }
    
    /// Get overall system status
    pub fn get_status(&self) -> Result<std::collections::HashMap<String, String>, AudioProcessorError> {
        let mut status = std::collections::HashMap::new();
        
        // Stereo delay parameters (in seconds, not milliseconds)
        status.insert("left_delay".to_string(), format!("{:.3}", self.config.stereo_delay.left_delay));
        status.insert("right_delay".to_string(), format!("{:.3}", self.config.stereo_delay.right_delay));
        status.insert("feedback".to_string(), format!("{:.3}", self.config.stereo_delay.feedback));
        status.insert("wet_mix".to_string(), format!("{:.3}", self.config.stereo_delay.wet_mix));
        status.insert("ping_pong".to_string(), self.config.stereo_delay.ping_pong.to_string());
        status.insert("stereo_width".to_string(), format!("{:.3}", self.config.stereo_delay.stereo_width));
        status.insert("cross_feedback".to_string(), format!("{:.3}", self.config.stereo_delay.cross_feedback));
        
        // Distortion parameters
        status.insert("distortion_enabled".to_string(), self.config.distortion.enabled.to_string());
        status.insert("distortion_type".to_string(), self.config.distortion.distortion_type.clone());
        status.insert("distortion_drive".to_string(), format!("{:.3}", self.config.distortion.drive));
        status.insert("distortion_mix".to_string(), format!("{:.3}", self.config.distortion.mix));
        status.insert("distortion_feedback_intensity".to_string(), format!("{:.3}", self.config.distortion.feedback_intensity));
        
        // System parameters
        status.insert("sample_rate".to_string(), self.config.sample_rate.to_string());
        status.insert("buffer_size".to_string(), self.config.buffer_size.to_string());
        status.insert("is_running".to_string(), self.is_running.read().to_string());
        
        // Add BPM information if available
        if let Some(bpm) = self.config.stereo_delay.bpm {
            status.insert("bpm".to_string(), format!("{:.0}", bpm));
        }
        
        Ok(status)
    }
    
    /// Run the ALSA audio stream with direct hardware access
    fn run_alsa_audio_stream(
        config: AudioConfig,
        stereo_delay: Arc<Mutex<StereoDelay>>,
        is_running: Arc<RwLock<bool>>,
    ) -> Result<(), AudioProcessorError> {
        println!("🎵 Initializing ALSA audio streams with direct hardware access...");
        
        // Open input PCM device
        let input_device = config.input_device.as_deref().unwrap_or("hw:CARD=USB,DEV=0");
        println!("🎤 Opening input device: {}", input_device);
        
        let input_pcm = PCM::new(input_device, Direction::Capture, false)
            .map_err(|e| {
                println!("❌ Failed to open input device {}: {}", input_device, e);
                AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
            })?;
        
        println!("✅ Successfully opened input device: {}", input_device);
        
        // Open output PCM device
        let output_device = config.output_device.as_deref().unwrap_or("hw:CARD=USB,DEV=0");
        println!("🔊 Opening output device: {}", output_device);
        
        let output_pcm = PCM::new(output_device, Direction::Playback, false)
            .map_err(|e| {
                println!("❌ Failed to open output device {}: {}", output_device, e);
                AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable)
            })?;
        
        println!("✅ Successfully opened output device: {}", output_device);
        
        // Configure input PCM using the correct ALSA API
        let input_hwp = HwParams::any(&input_pcm).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_hwp.set_channels(2).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_hwp.set_rate(config.sample_rate, ValueOr::Nearest).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_hwp.set_format(Format::s32()).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_hwp.set_access(alsa::pcm::Access::RWInterleaved).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_pcm.hw_params(&input_hwp).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        input_pcm.prepare().map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        
        println!("🎤 Input configured: {} Hz, 2 channels, S32", config.sample_rate);
        
        // Configure output PCM using the correct ALSA API
        let output_hwp = HwParams::any(&output_pcm).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_hwp.set_channels(2).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_hwp.set_rate(config.sample_rate, ValueOr::Nearest).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_hwp.set_format(Format::s32()).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_hwp.set_access(alsa::pcm::Access::RWInterleaved).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_pcm.hw_params(&output_hwp).map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        output_pcm.prepare().map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        
        println!("🔊 Output configured: {} Hz, 2 channels, S32", config.sample_rate);
        
        // Audio processing loop
        let buffer_size = config.buffer_size;
        let mut input_buffer = vec![0i32; buffer_size * 2]; // Stereo
        let mut output_buffer = vec![0i32; buffer_size * 2]; // Stereo
        
        println!("🎵 Starting ALSA audio processing loop...");
        
        // Get I/O interfaces
        let input_io = input_pcm.io_i32().map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        let output_io = output_pcm.io_i32().map_err(|_e| AudioProcessorError::AudioDevice(cpal::BuildStreamError::DeviceNotAvailable))?;
        
        let mut frames_processed = 0;
        while *is_running.read() {
            // Read input using the correct ALSA API
            match input_io.readi(&mut input_buffer) {
                Ok(_) => {
                    // Process audio through stereo delay
                    if let Ok(mut delay) = stereo_delay.lock() {
                        for i in (0..input_buffer.len()).step_by(2) {
                            let left_input = input_buffer[i] as f32 / i32::MAX as f32;
                            let right_input = if i + 1 < input_buffer.len() { 
                                input_buffer[i + 1] as f32 / i32::MAX as f32 
                            } else { 
                                left_input 
                            };
                            
                            let (left_output, right_output) = delay.process_sample(left_input, right_input);
                            
                            // Convert back to S32
                            output_buffer[i] = (left_output * i32::MAX as f32) as i32;
                            if i + 1 < output_buffer.len() {
                                output_buffer[i + 1] = (right_output * i32::MAX as f32) as i32;
                            }
                        }
                    }
                    
                    // Write output using the correct ALSA API
                    if let Err(e) = output_io.writei(&output_buffer) {
                        eprintln!("Output write error: {}", e);
                    }
                    
                    frames_processed += 1;
                }
                Err(e) => {
                    eprintln!("Input read error: {}", e);
                    thread::sleep(Duration::from_millis(10));
                }
            }
        }
        
        println!("🎵 ALSA audio processing stopped - processed {} frames", frames_processed);
        Ok(())
    }
    
    /// Set stereo delay effect parameter
    pub fn set_stereo_delay_parameter(&mut self, param: &str, value: f32) -> Result<(), AudioProcessorError> {
        let mut delay = self.stereo_delay.lock().map_err(|_| {
            AudioProcessorError::Threading("Failed to acquire stereo delay lock".to_string())
        })?;
        
        match param {
            "left_delay" => delay.set_left_delay(value),
            "right_delay" => delay.set_right_delay(value),
            "bpm" => {
                // Set BPM and calculate delay times
                let mut config = self.config.clone();
                config.stereo_delay.set_bpm(value);
                delay.set_left_delay(config.stereo_delay.left_delay);
                delay.set_right_delay(config.stereo_delay.right_delay);
                // Update the stored config
                self.config.stereo_delay.bpm = config.stereo_delay.bpm;
                self.config.stereo_delay.left_delay = config.stereo_delay.left_delay;
                self.config.stereo_delay.right_delay = config.stereo_delay.right_delay;
            },
            "feedback" => delay.set_feedback(value),
            "wet_mix" => delay.set_wet_mix(value),
            "ping_pong" => delay.set_stereo_parameters(Some(value > 0.5), None, None),
            "stereo_width" => delay.set_stereo_parameters(None, Some(value), None),
            "cross_feedback" => delay.set_stereo_parameters(None, None, Some(value)),
            // Distortion parameters
            "distortion_enabled" => delay.set_cross_feedback_distortion(Some(value > 0.5), None, None, None, None),
            "distortion_drive" => delay.set_cross_feedback_distortion(None, None, Some(value), None, None),
            "distortion_mix" => delay.set_cross_feedback_distortion(None, None, None, Some(value), None),
            "distortion_feedback_intensity" => delay.set_cross_feedback_distortion(None, None, None, None, Some(value)),
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
    
    /// Set distortion type (string parameter)
    pub fn set_distortion_type(&self, distortion_type: &str) -> Result<(), AudioProcessorError> {
        let mut delay = self.stereo_delay.lock().map_err(|_| {
            AudioProcessorError::Threading("Failed to acquire stereo delay lock".to_string())
        })?;
        
        let dist_type = DistortionType::from(distortion_type);
        delay.set_cross_feedback_distortion(None, Some(dist_type), None, None, None);
        
        Ok(())
    }
    
    /// Reset the delay buffers to clear any lingering feedback
    pub fn reset_delay(&self) -> Result<(), AudioProcessorError> {
        let mut delay = self.stereo_delay.lock().map_err(|_| {
            AudioProcessorError::Threading("Failed to acquire stereo delay lock".to_string())
        })?;
        
        delay.reset();
        
        Ok(())
    }
    
    /// Test ALSA audio processing
    pub fn test_audio(&self) -> Result<(), AudioProcessorError> {
        println!("🧪 Testing ALSA audio processing...");
        
        // Create a simple test delay
        let test_delay = StereoDelay::new(
            self.config.sample_rate,
            0.1, // 100ms delay
            0.2, // 200ms delay
            0.3, // 30% feedback
            0.5, // 50% wet mix
            true, // ping pong
            0.5, // stereo width
            0.2, // cross feedback
            false, // no distortion for test
            DistortionType::SoftClip,
            0.0,
            0.0,
        );
        
        // Generate test audio (sine wave)
        let sample_rate = self.config.sample_rate as f32;
        let frequency = 440.0; // A4 note
        let duration = 1.0; // 1 second
        let num_samples = (sample_rate * duration) as usize;
        
        let mut input_audio = Vec::with_capacity(num_samples);
        for i in 0..num_samples {
            let t = i as f32 / sample_rate;
            let sample = (2.0 * std::f32::consts::PI * frequency * t).sin();
            input_audio.push(sample);
        }
        
        // Process through delay
        let mut delay = test_delay;
        for sample in &input_audio {
            let (_left, _right) = delay.process_sample(*sample, *sample);
            // Just process, don't need to store output for test
        }
        
        println!("✅ ALSA audio test completed - processed {} samples", num_samples);
        Ok(())
    }
}
