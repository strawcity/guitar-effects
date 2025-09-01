use crate::distortion::{DistortionType, CrossFeedbackDistortion};

/// Base delay effect trait
pub trait BaseDelay {
    /// Get the name of this delay effect
    fn get_effect_name(&self) -> &str;
    
    /// Process a single sample through the delay effect
    fn process_sample(&mut self, input_sample: f32) -> (f32, f32);
    
    /// Process an entire buffer through the delay effect
    fn process_buffer(&mut self, input_buffer: &[f32]) -> Vec<(f32, f32)>;
    
    /// Reset the delay buffer and internal state
    fn reset(&mut self);
    
    /// Set the delay time in seconds
    fn set_delay_time(&mut self, delay_time: f32);
    
    /// Set the feedback amount (0.0 to 0.9)
    fn set_feedback(&mut self, feedback: f32);
    
    /// Set the wet signal mix (0.0 to 1.0)
    fn set_wet_mix(&mut self, wet_mix: f32);
}

/// Simple delay line implementation
pub struct SimpleDelay {
    sample_rate: u32,
    max_delay_time: f32,
    feedback: f32,
    wet_mix: f32,
    dry_mix: f32,
    
    // Buffer management
    buffer_size: usize,
    delay_buffer: Vec<f32>,
    write_index: usize,
    
    // Current delay time
    delay_time: f32,
    delay_samples: usize,
    
    // Modulation parameters
    modulation_rate: f32,
    modulation_depth: f32,
    modulation_phase: f32,
}

impl SimpleDelay {
    /// Create a new simple delay
    pub fn new(
        sample_rate: u32,
        max_delay_time: f32,
        feedback: f32,
        wet_mix: f32,
    ) -> Self {
        let buffer_size = (max_delay_time * sample_rate as f32) as usize;
        let delay_samples = (0.5 * sample_rate as f32) as usize; // Default 500ms
        
        Self {
            sample_rate,
            max_delay_time,
            feedback: feedback.clamp(0.0, 0.9),
            wet_mix: wet_mix.clamp(0.0, 1.0),
            dry_mix: 1.0 - wet_mix.clamp(0.0, 1.0),
            buffer_size,
            delay_buffer: vec![0.0; buffer_size],
            write_index: 0,
            delay_time: 0.5,
            delay_samples,
            modulation_rate: 0.0,
            modulation_depth: 0.0,
            modulation_phase: 0.0,
        }
    }
    
    /// Set modulation parameters for the delay time
    pub fn set_modulation(&mut self, rate: f32, depth: f32) {
        self.modulation_rate = rate.max(0.0);
        self.modulation_depth = depth.max(0.0);
    }
    
    /// Get the current delay time with modulation applied
    fn get_modulated_delay(&self) -> usize {
        if self.modulation_rate > 0.0 && self.modulation_depth > 0.0 {
            let mod_offset = self.modulation_depth * (2.0 * std::f32::consts::PI * self.modulation_phase).sin();
            let modulated_delay = self.delay_samples as f32 + mod_offset;
            modulated_delay.clamp(1.0, (self.buffer_size - 1) as f32) as usize
        } else {
            self.delay_samples
        }
    }
    
    /// Update the modulation phase
    fn update_modulation_phase(&mut self) {
        if self.modulation_rate > 0.0 {
            self.modulation_phase += self.modulation_rate / self.sample_rate as f32;
            if self.modulation_phase >= 1.0 {
                self.modulation_phase -= 1.0;
            }
        }
    }
    
    /// Read from the delay buffer at the current read position
    fn read_delay_buffer(&self) -> f32 {
        let read_index = (self.write_index + self.buffer_size - self.get_modulated_delay()) % self.buffer_size;
        self.delay_buffer[read_index]
    }
    
    /// Write to the delay buffer at the current write position
    fn write_delay_buffer(&mut self, sample: f32) {
        self.delay_buffer[self.write_index] = sample;
        self.write_index = (self.write_index + 1) % self.buffer_size;
    }
}

impl BaseDelay for SimpleDelay {
    fn get_effect_name(&self) -> &str {
        "Simple Delay"
    }
    
    fn process_sample(&mut self, input_sample: f32) -> (f32, f32) {
        // Read delayed signal
        let delayed_sample = self.read_delay_buffer();
        
        // Calculate output (dry + wet)
        let output_sample = self.dry_mix * input_sample + self.wet_mix * delayed_sample;
        
        // Write to buffer with feedback
        let feedback_sample = input_sample + self.feedback * delayed_sample;
        self.write_delay_buffer(feedback_sample);
        
        // Update modulation phase
        self.update_modulation_phase();
        
        // Return stereo output (same signal on both channels)
        (output_sample, output_sample)
    }
    
    fn process_buffer(&mut self, input_buffer: &[f32]) -> Vec<(f32, f32)> {
        let mut output = Vec::with_capacity(input_buffer.len());
        
        for &input_sample in input_buffer {
            output.push(self.process_sample(input_sample));
        }
        
        output
    }
    
    fn reset(&mut self) {
        self.delay_buffer.fill(0.0);
        self.write_index = 0;
        self.modulation_phase = 0.0;
    }
    
    fn set_delay_time(&mut self, delay_time: f32) {
        self.delay_time = delay_time.clamp(0.001, self.max_delay_time);
        self.delay_samples = (self.delay_time * self.sample_rate as f32) as usize;
    }
    
    fn set_feedback(&mut self, feedback: f32) {
        self.feedback = feedback.clamp(0.0, 0.9);
    }
    
    fn set_wet_mix(&mut self, wet_mix: f32) {
        self.wet_mix = wet_mix.clamp(0.0, 1.0);
        self.dry_mix = 1.0 - self.wet_mix;
    }
}

/// Stereo delay effect with ping-pong and stereo enhancement
pub struct StereoDelay {
    sample_rate: u32,
    max_delay_time: f32,
    feedback: f32,
    wet_mix: f32,
    dry_mix: f32,
    
    // Stereo-specific parameters
    left_delay: f32,
    right_delay: f32,
    ping_pong: bool,
    stereo_width: f32,
    cross_feedback: f32,
    
    // Separate buffers for left and right channels
    _left_buffer_size: usize,
    _right_buffer_size: usize,
    left_buffer: Vec<f32>,
    right_buffer: Vec<f32>,
    left_write_index: usize,
    right_write_index: usize,
    
    // Stereo enhancement
    mid_side_enabled: bool,
    
    // Cross-feedback distortion
    cross_feedback_distortion: CrossFeedbackDistortion,
}

impl StereoDelay {
    /// Create a new stereo delay effect
    pub fn new(
        sample_rate: u32,
        left_delay: f32,
        right_delay: f32,
        feedback: f32,
        wet_mix: f32,
        ping_pong: bool,
        stereo_width: f32,
        cross_feedback: f32,
        cross_feedback_distortion: bool,
        distortion_type: DistortionType,
        distortion_drive: f32,
        distortion_mix: f32,
    ) -> Self {
        let left_buffer_size = (left_delay * sample_rate as f32) as usize;
        let right_buffer_size = (right_delay * sample_rate as f32) as usize;
        
        Self {
            sample_rate,
            max_delay_time: 4.0,
            feedback: feedback.clamp(0.0, 0.9),
            wet_mix: wet_mix.clamp(0.0, 1.0),
            dry_mix: 1.0 - wet_mix.clamp(0.0, 1.0),
            left_delay,
            right_delay,
            ping_pong,
            stereo_width: stereo_width.clamp(0.0, 1.0),
            cross_feedback: cross_feedback.clamp(0.0, 0.5),
            _left_buffer_size: left_buffer_size,
            _right_buffer_size: right_buffer_size,
            left_buffer: vec![0.0; left_buffer_size],
            right_buffer: vec![0.0; right_buffer_size],
            left_write_index: 0,
            right_write_index: 0,
            mid_side_enabled: stereo_width > 0.0,
            cross_feedback_distortion: CrossFeedbackDistortion::new(
                cross_feedback_distortion,
                distortion_type,
                distortion_drive,
                distortion_mix,
                sample_rate,
            ),
        }
    }
    
    /// Set the left channel delay time
    pub fn set_left_delay(&mut self, delay_time: f32) {
        self.left_delay = delay_time.clamp(0.001, self.max_delay_time);
        let new_buffer_size = (self.left_delay * self.sample_rate as f32) as usize;
        
        if new_buffer_size != self.left_buffer.len() {
            self.left_buffer = vec![0.0; new_buffer_size];
            self.left_write_index = 0;
        }
    }
    
    /// Set the right channel delay time
    pub fn set_right_delay(&mut self, delay_time: f32) {
        self.right_delay = delay_time.clamp(0.001, self.max_delay_time);
        let new_buffer_size = (self.right_delay * self.sample_rate as f32) as usize;
        
        if new_buffer_size != self.right_buffer.len() {
            self.right_buffer = vec![0.0; new_buffer_size];
            self.right_write_index = 0;
        }
    }
    
    /// Set stereo-specific parameters
    pub fn set_stereo_parameters(&mut self, ping_pong: Option<bool>, stereo_width: Option<f32>, cross_feedback: Option<f32>) {
        if let Some(ping_pong) = ping_pong {
            self.ping_pong = ping_pong;
        }
        if let Some(stereo_width) = stereo_width {
            self.stereo_width = stereo_width.clamp(0.0, 1.0);
            self.mid_side_enabled = self.stereo_width > 0.0;
        }
        if let Some(cross_feedback) = cross_feedback {
            self.cross_feedback = cross_feedback.clamp(0.0, 0.5);
        }
    }
    
    /// Set cross-feedback distortion parameters
    pub fn set_cross_feedback_distortion(&mut self, enabled: Option<bool>, distortion_type: Option<DistortionType>, drive: Option<f32>, mix: Option<f32>, feedback_intensity: Option<f32>) {
        if let Some(enabled) = enabled {
            self.cross_feedback_distortion.set_enabled(enabled);
        }
        if let Some(distortion_type) = distortion_type {
            self.cross_feedback_distortion.set_distortion_type(distortion_type);
        }
        if let Some(drive) = drive {
            self.cross_feedback_distortion.set_drive(drive);
        }
        if let Some(mix) = mix {
            self.cross_feedback_distortion.set_mix(mix);
        }
        if let Some(feedback_intensity) = feedback_intensity {
            self.cross_feedback_distortion.set_feedback_intensity(feedback_intensity);
        }
    }
    
    /// Read delayed signals from both channels
    fn read_stereo_delays(&self) -> (f32, f32) {
        let left_read_idx = (self.left_write_index + self.left_buffer.len() - (self.left_delay * self.sample_rate as f32) as usize) % self.left_buffer.len();
        let left_delayed = self.left_buffer[left_read_idx];
        
        let right_read_idx = (self.right_write_index + self.right_buffer.len() - (self.right_delay * self.sample_rate as f32) as usize) % self.right_buffer.len();
        let right_delayed = self.right_buffer[right_read_idx];
        
        (left_delayed, right_delayed)
    }
    
    /// Apply ping-pong delay pattern
    fn apply_ping_pong(&self, left_delayed: f32, right_delayed: f32) -> (f32, f32) {
        if self.ping_pong {
            (right_delayed, left_delayed)
        } else {
            (left_delayed, right_delayed)
        }
    }
    
    /// Apply stereo width enhancement using mid-side processing
    fn apply_stereo_enhancement(&self, left_sample: f32, right_sample: f32) -> (f32, f32) {
        if !self.mid_side_enabled {
            return (left_sample, right_sample);
        }
        
        // Convert to mid-side
        let mid = (left_sample + right_sample) * 0.5;
        let side = (left_sample - right_sample) * 0.5;
        
        // Enhance side signal
        let enhanced_side = side * (1.0 + self.stereo_width);
        
        // Convert back to left-right
        let enhanced_left = mid + enhanced_side;
        let enhanced_right = mid - enhanced_side;
        
        (enhanced_left, enhanced_right)
    }
    
    /// Write to both stereo buffers with cross-feedback and distortion
    fn write_stereo_buffers(&mut self, left_sample: f32, right_sample: f32) {
        // Calculate cross-feedback
        let left_feedback = left_sample + self.cross_feedback * right_sample;
        let right_feedback = right_sample + self.cross_feedback * left_sample;
        
        // Apply distortion to cross-feedback signals
        let (left_feedback, right_feedback) = self.cross_feedback_distortion.process_cross_feedback(left_feedback, right_feedback);
        
        // Write to buffers
        self.left_buffer[self.left_write_index] = left_feedback;
        self.right_buffer[self.right_write_index] = right_feedback;
        
        // Update write indices
        self.left_write_index = (self.left_write_index + 1) % self.left_buffer.len();
        self.right_write_index = (self.right_write_index + 1) % self.right_buffer.len();
    }
    
    /// Process stereo audio samples through the stereo delay effect
    pub fn process_sample(&mut self, left_input: f32, right_input: f32) -> (f32, f32) {
        // Read delayed signals
        let (left_delayed, right_delayed) = self.read_stereo_delays();
        
        // Apply ping-pong if enabled
        let (left_delayed, right_delayed) = self.apply_ping_pong(left_delayed, right_delayed);
        
        // Apply stereo enhancement
        let (left_delayed, right_delayed) = self.apply_stereo_enhancement(left_delayed, right_delayed);
        
        // Calculate outputs (dry + wet)
        let left_output = self.dry_mix * left_input + self.wet_mix * left_delayed;
        let right_output = self.dry_mix * right_input + self.wet_mix * right_delayed;
        
        // Write to buffers with feedback
        let left_feedback_sample = left_input + self.feedback * left_delayed;
        let right_feedback_sample = right_input + self.feedback * right_delayed;
        
        self.write_stereo_buffers(left_feedback_sample, right_feedback_sample);
        
        (left_output, right_output)
    }
    
    /// Process mono input to stereo output with stereo delay effect
    pub fn process_mono_to_stereo(&mut self, input_buffer: &[f32]) -> (Vec<f32>, Vec<f32>) {
        let mut left_output = vec![0.0; input_buffer.len()];
        let mut right_output = vec![0.0; input_buffer.len()];
        
        for (i, &input_sample) in input_buffer.iter().enumerate() {
            let (left_sample, right_sample) = self.process_sample(input_sample, input_sample);
            left_output[i] = left_sample;
            right_output[i] = right_sample;
        }
        
        (left_output, right_output)
    }
    
    /// Get stereo-specific information
    pub fn get_stereo_info(&self) -> String {
        let base_info = format!(
            "Left: {:.0}ms, Right: {:.0}ms, Ping-pong: {}, Width: {:.0}%",
            self.left_delay * 1000.0,
            self.right_delay * 1000.0,
            if self.ping_pong { "On" } else { "Off" },
            self.stereo_width * 100.0
        );
        
        let distortion_info = self.cross_feedback_distortion.get_info();
        format!("{} | {}", base_info, distortion_info)
    }
    
    /// Get current parameter values including stereo-specific ones
    pub fn get_parameters(&self) -> std::collections::HashMap<String, f32> {
        let mut params = std::collections::HashMap::new();
        params.insert("feedback".to_string(), self.feedback);
        params.insert("wet_mix".to_string(), self.wet_mix);
        params.insert("left_delay".to_string(), self.left_delay);
        params.insert("right_delay".to_string(), self.right_delay);
        params.insert("stereo_width".to_string(), self.stereo_width);
        params.insert("cross_feedback".to_string(), self.cross_feedback);
        params
    }
    
    /// Get a human-readable description of current settings
    pub fn get_info(&self) -> String {
        format!(
            "{}: L={:.0}ms, R={:.0}ms, Feedback={:.0}%, Wet={:.0}%",
            self.get_effect_name(),
            self.left_delay * 1000.0,
            self.right_delay * 1000.0,
            self.feedback * 100.0,
            self.wet_mix * 100.0
        )
    }
}

impl BaseDelay for StereoDelay {
    fn get_effect_name(&self) -> &str {
        "Stereo Delay"
    }
    
    fn process_sample(&mut self, input_sample: f32) -> (f32, f32) {
        self.process_sample(input_sample, input_sample)
    }
    
    fn process_buffer(&mut self, input_buffer: &[f32]) -> Vec<(f32, f32)> {
        let mut output = Vec::with_capacity(input_buffer.len());
        
        for &input_sample in input_buffer {
            output.push(self.process_sample(input_sample, input_sample));
        }
        
        output
    }
    
    fn reset(&mut self) {
        self.left_buffer.fill(0.0);
        self.right_buffer.fill(0.0);
        self.left_write_index = 0;
        self.right_write_index = 0;
    }
    
    fn set_delay_time(&mut self, delay_time: f32) {
        self.set_left_delay(delay_time);
        self.set_right_delay(delay_time);
    }
    
    fn set_feedback(&mut self, feedback: f32) {
        self.feedback = feedback.clamp(0.0, 0.9);
    }
    
    fn set_wet_mix(&mut self, wet_mix: f32) {
        self.wet_mix = wet_mix.clamp(0.0, 1.0);
        self.dry_mix = 1.0 - self.wet_mix;
    }
}
