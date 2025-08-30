

/// Types of distortion available
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

impl From<&str> for DistortionType {
    fn from(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "soft_clip" => DistortionType::SoftClip,
            "hard_clip" => DistortionType::HardClip,
            "tube" => DistortionType::Tube,
            "fuzz" => DistortionType::Fuzz,
            "bit_crush" => DistortionType::BitCrush,
            "waveshaper" => DistortionType::Waveshaper,
            _ => DistortionType::None,
        }
    }
}

impl ToString for DistortionType {
    fn to_string(&self) -> String {
        match self {
            DistortionType::SoftClip => "soft_clip",
            DistortionType::HardClip => "hard_clip",
            DistortionType::Tube => "tube",
            DistortionType::Fuzz => "fuzz",
            DistortionType::BitCrush => "bit_crush",
            DistortionType::Waveshaper => "waveshaper",
            DistortionType::None => "none",
        }.to_string()
    }
}

/// Distortion effect that can be applied to cross-feedback signals
pub struct DistortionEffect {
    distortion_type: DistortionType,
    drive: f32,
    mix: f32,
    sample_rate: u32,
    
    // Distortion-specific parameters
    bit_depth: u8,
    sample_rate_reduction: f32,
    last_sample: f32,
}

impl DistortionEffect {
    /// Create a new distortion effect
    pub fn new(
        distortion_type: DistortionType,
        drive: f32,
        mix: f32,
        sample_rate: u32,
    ) -> Self {
        Self {
            distortion_type,
            drive: drive.clamp(0.0, 1.0),
            mix: mix.clamp(0.0, 1.0),
            sample_rate,
            bit_depth: 8,
            sample_rate_reduction: 0.5,
            last_sample: 0.0,
        }
    }
    
    /// Set the type of distortion
    pub fn set_distortion_type(&mut self, distortion_type: DistortionType) {
        self.distortion_type = distortion_type;
    }
    
    /// Set the drive amount (0.0 to 1.0)
    pub fn set_drive(&mut self, drive: f32) {
        self.drive = drive.clamp(0.0, 1.0);
    }
    
    /// Set the wet/dry mix (0.0 to 1.0)
    pub fn set_mix(&mut self, mix: f32) {
        self.mix = mix.clamp(0.0, 1.0);
    }
    
    /// Set bit crushing parameters
    pub fn set_bit_crush_parameters(&mut self, bit_depth: u8, sample_rate_reduction: f32) {
        self.bit_depth = bit_depth.clamp(1, 16);
        self.sample_rate_reduction = sample_rate_reduction.clamp(0.0, 1.0);
    }
    
    /// Apply soft clipping distortion
    fn soft_clip(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 10.0;
        sample.tanh() / drive_factor
    }
    
    /// Apply hard clipping distortion
    fn hard_clip(&self, sample: f32) -> f32 {
        let threshold = 1.0 - self.drive;
        if sample.abs() > threshold {
            sample.signum() * threshold
        } else {
            sample
        }
    }
    
    /// Apply tube-style distortion
    fn tube_distortion(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 5.0;
        if sample > 0.0 {
            sample.tanh() / drive_factor
        } else {
            -(-sample).tanh() / (drive_factor * 0.7)
        }
    }
    
    /// Apply fuzz-style distortion
    fn fuzz_distortion(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 20.0;
        let distorted = sample * drive_factor;
        
        if distorted.abs() > 0.8 {
            distorted.signum() * (0.8 + 0.2 * ((distorted.abs() - 0.8) * 5.0).tanh())
        } else {
            distorted
        }
    }
    
    /// Apply bit crushing distortion
    fn bit_crush(&mut self, sample: f32) -> f32 {
        let max_value = (2i32.pow(self.bit_depth as u32 - 1) - 1) as f32;
        let quantized = (sample * max_value).round() / max_value;
        
        // Simple sample rate reduction simulation
        if fastrand::f32() < self.sample_rate_reduction {
            self.last_sample = quantized;
            quantized
        } else {
            self.last_sample
        }
    }
    
    /// Apply waveshaper distortion
    fn waveshaper(&self, sample: f32) -> f32 {
        let driven = sample * (1.0 + self.drive * 3.0);
        driven - (driven.powi(3)) / 3.0
    }
    
    /// Process a single sample through the distortion effect
    pub fn process_sample(&mut self, sample: f32) -> f32 {
        if self.distortion_type == DistortionType::None {
            return sample;
        }
        
        // Apply drive
        let driven_sample = sample * (1.0 + self.drive * 5.0);
        
        // Apply distortion based on type
        let distorted = match self.distortion_type {
            DistortionType::SoftClip => self.soft_clip(driven_sample),
            DistortionType::HardClip => self.hard_clip(driven_sample),
            DistortionType::Tube => self.tube_distortion(driven_sample),
            DistortionType::Fuzz => self.fuzz_distortion(driven_sample),
            DistortionType::BitCrush => self.bit_crush(driven_sample),
            DistortionType::Waveshaper => self.waveshaper(driven_sample),
            DistortionType::None => driven_sample,
        };
        
        // Apply mix
        sample * (1.0 - self.mix) + distorted * self.mix
    }
    
    /// Process an entire buffer through the distortion effect
    pub fn process_buffer(&mut self, buffer: &mut [f32]) {
        for sample in buffer.iter_mut() {
            *sample = self.process_sample(*sample);
        }
    }
    
    /// Get a human-readable description of current settings
    pub fn get_info(&self) -> String {
        format!(
            "Distortion: {}, Drive: {:.0}%, Mix: {:.0}%",
            self.distortion_type.to_string(),
            self.drive * 100.0,
            self.mix * 100.0
        )
    }
}

/// Specialized distortion for cross-feedback signals in stereo delay
pub struct CrossFeedbackDistortion {
    enabled: bool,
    distortion: DistortionEffect,
    feedback_intensity: f32,
    frequency_dependent: bool,
}

impl CrossFeedbackDistortion {
    /// Create a new cross-feedback distortion
    pub fn new(
        enabled: bool,
        distortion_type: DistortionType,
        drive: f32,
        mix: f32,
        sample_rate: u32,
    ) -> Self {
        Self {
            enabled,
            distortion: DistortionEffect::new(distortion_type, drive, mix, sample_rate),
            feedback_intensity: 0.5,
            frequency_dependent: true,
        }
    }
    
    /// Enable or disable cross-feedback distortion
    pub fn set_enabled(&mut self, enabled: bool) {
        self.enabled = enabled;
    }
    
    /// Set the type of distortion
    pub fn set_distortion_type(&mut self, distortion_type: DistortionType) {
        self.distortion.set_distortion_type(distortion_type);
    }
    
    /// Set the drive amount
    pub fn set_drive(&mut self, drive: f32) {
        self.distortion.set_drive(drive);
    }
    
    /// Set the wet/dry mix
    pub fn set_mix(&mut self, mix: f32) {
        self.distortion.set_mix(mix);
    }
    
    /// Set how much the distortion affects feedback (0.0 to 1.0)
    pub fn set_feedback_intensity(&mut self, intensity: f32) {
        self.feedback_intensity = intensity.clamp(0.0, 1.0);
    }
    
    /// Process cross-feedback signals with distortion
    pub fn process_cross_feedback(&mut self, left_sample: f32, right_sample: f32) -> (f32, f32) {
        if !self.enabled {
            return (left_sample, right_sample);
        }
        
        // Apply distortion to cross-feedback signals
        let distorted_left = self.distortion.process_sample(left_sample);
        let distorted_right = self.distortion.process_sample(right_sample);
        
        // Blend with original based on feedback intensity
        let left_output = left_sample * (1.0 - self.feedback_intensity) 
            + distorted_left * self.feedback_intensity;
        let right_output = right_sample * (1.0 - self.feedback_intensity) 
            + distorted_right * self.feedback_intensity;
        
        (left_output, right_output)
    }
    
    /// Get a human-readable description of current settings
    pub fn get_info(&self) -> String {
        if !self.enabled {
            "Cross-feedback Distortion: Disabled".to_string()
        } else {
            format!("Cross-feedback Distortion: {}", self.distortion.get_info())
        }
    }
}

// Simple random number generator for bit crushing
mod fastrand {
    use std::sync::Once;
    use std::cell::RefCell;
    
    static INIT: Once = Once::new();
    thread_local!(static RNG: RefCell<u64> = RefCell::new(0));
    
    fn init_rng() {
        INIT.call_once(|| {
            RNG.with(|rng| {
                *rng.borrow_mut() = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos() as u64;
            });
        });
    }
    
    pub fn f32() -> f32 {
        init_rng();
        RNG.with(|rng| {
            let mut x = rng.borrow_mut();
            *x ^= *x >> 12;
            *x ^= *x << 25;
            *x ^= *x >> 27;
            (*x as f32) / (u64::MAX as f32)
        })
    }
}
