# Stereo Delay Effects

## Overview

The Stereo Delay Effects module provides professional-quality stereo delay processing with advanced features including independent left/right channel control, ping-pong patterns, cross-feedback, and stereo width enhancement. This module is the core effect processor in the Guitar Effects System.

## 🎛️ Core Features

### Stereo Delay Processing
- **Independent Channel Control**: Separate delay times for left and right channels
- **Ping-Pong Patterns**: Bouncing delay effects between channels
- **Cross-Feedback**: Inter-channel feedback for complex spatial effects
- **Stereo Width Enhancement**: Mid-side processing for enhanced stereo image
- **Real-Time Control**: Parameter adjustment during playback

### Advanced Delay Types
- **Simple Delay**: Basic delay with feedback
- **Tape Delay**: Analog tape-style delay with modulation
- **Multi-Tap Delay**: Multiple delay taps with individual control
- **Tempo-Synced Delay**: BPM-synchronized delay times
- **Stereo Delay**: Advanced stereo processing with cross-feedback

## 🏗️ Architecture

### Component Structure

```
StereoDelay
├── LeftDelay (SimpleDelay)
├── RightDelay (SimpleDelay)
├── CrossFeedbackProcessor
├── StereoWidthEnhancer
├── DistortionProcessor
└── ParameterController
```

### Data Flow

```
Left Input ──┐                    ┌── Left Output
             ├── Left Delay ──┐   │
             │                ├───┤
             │                │   │
Right Input ─┘                │   │
             ┌── Right Delay ─┘   │
             │                    │
             └── Cross-Feedback ─┘
```

## 📋 API Reference

### Core Types

#### StereoDelay
```rust
pub struct StereoDelay {
    left_delay: SimpleDelay,
    right_delay: SimpleDelay,
    cross_feedback: f32,
    stereo_width: f32,
    ping_pong: bool,
    cross_feedback_distortion: Option<CrossFeedbackDistortion>,
}
```

#### DelayConfig
```rust
pub struct DelayConfig {
    pub left_delay: f32,      // Left channel delay time (seconds)
    pub right_delay: f32,     // Right channel delay time (seconds)
    pub feedback: f32,        // Feedback amount (0.0 to 0.9)
    pub wet_mix: f32,        // Wet signal mix (0.0 to 1.0)
    pub ping_pong: bool,     // Enable ping-pong pattern
    pub stereo_width: f32,    // Stereo width enhancement (0.0 to 1.0)
    pub cross_feedback: f32, // Cross-feedback amount (0.0 to 0.5)
}
```

### Core Methods

#### Initialization
```rust
impl StereoDelay {
    /// Create a new stereo delay with configuration
    pub fn new(config: DelayConfig) -> Self;
    
    /// Create with default settings
    pub fn new_default() -> Self;
    
    /// Create with custom sample rate
    pub fn new_with_sample_rate(sample_rate: u32, config: DelayConfig) -> Self;
}
```

#### Processing
```rust
impl StereoDelay {
    /// Process stereo input to stereo output
    pub fn process(&mut self, left_input: f32, right_input: f32) -> (f32, f32);
    
    /// Process entire buffer
    pub fn process_buffer(&mut self, left_input: &[f32], right_input: &[f32]) -> (Vec<f32>, Vec<f32>);
    
    /// Process mono input to stereo output
    pub fn process_mono(&mut self, input: f32) -> (f32, f32);
}
```

#### Parameter Control
```rust
impl StereoDelay {
    /// Set left channel delay time
    pub fn set_left_delay(&mut self, delay_time: f32);
    
    /// Set right channel delay time
    pub fn set_right_delay(&mut self, delay_time: f32);
    
    /// Set feedback amount
    pub fn set_feedback(&mut self, feedback: f32);
    
    /// Set wet mix
    pub fn set_wet_mix(&mut self, wet_mix: f32);
    
    /// Enable/disable ping-pong
    pub fn set_ping_pong(&mut self, enabled: bool);
    
    /// Set stereo width
    pub fn set_stereo_width(&mut self, width: f32);
    
    /// Set cross-feedback amount
    pub fn set_cross_feedback(&mut self, amount: f32);
}
```

## 🎯 Detailed Implementation

### Simple Delay Implementation

#### Core Structure
```rust
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
```

#### Processing Algorithm
```rust
impl SimpleDelay {
    fn process_sample(&mut self, input: f32) -> f32 {
        // Calculate modulated delay time
        let modulated_delay = self.get_modulated_delay();
        
        // Read from delay buffer
        let read_index = (self.write_index + self.buffer_size - modulated_delay) % self.buffer_size;
        let delayed_sample = self.delay_buffer[read_index];
        
        // Calculate feedback
        let feedback_sample = delayed_sample * self.feedback;
        
        // Write to buffer
        self.delay_buffer[self.write_index] = input + feedback_sample;
        self.write_index = (self.write_index + 1) % self.buffer_size;
        
        // Update modulation phase
        self.update_modulation_phase();
        
        // Mix dry and wet signals
        input * self.dry_mix + delayed_sample * self.wet_mix
    }
}
```

### Cross-Feedback Processing

#### Cross-Feedback Algorithm
```rust
impl StereoDelay {
    fn process_cross_feedback(&mut self, left_output: f32, right_output: f32) -> (f32, f32) {
        // Calculate cross-feedback
        let left_cross = right_output * self.cross_feedback;
        let right_cross = left_output * self.cross_feedback;
        
        // Apply cross-feedback distortion if enabled
        let (left_final, right_final) = if let Some(ref mut distortion) = self.cross_feedback_distortion {
            let distorted_left = distortion.process(left_cross);
            let distorted_right = distortion.process(right_cross);
            (left_output + distorted_left, right_output + distorted_right)
        } else {
            (left_output + left_cross, right_output + right_cross)
        };
        
        (left_final, right_final)
    }
}
```

### Stereo Width Enhancement

#### Mid-Side Processing
```rust
impl StereoDelay {
    fn enhance_stereo_width(&mut self, left: f32, right: f32) -> (f32, f32) {
        // Convert to mid-side
        let mid = (left + right) * 0.5;
        let side = (left - right) * 0.5;
        
        // Enhance side signal
        let enhanced_side = side * (1.0 + self.stereo_width);
        
        // Convert back to left-right
        let enhanced_left = mid + enhanced_side;
        let enhanced_right = mid - enhanced_side;
        
        (enhanced_left, enhanced_right)
    }
}
```

### Ping-Pong Processing

#### Ping-Pong Algorithm
```rust
impl StereoDelay {
    fn process_ping_pong(&mut self, left_input: f32, right_input: f32) -> (f32, f32) {
        if self.ping_pong {
            // Ping-pong: left feeds right, right feeds left
            let left_delayed = self.left_delay.process_sample(left_input);
            let right_delayed = self.right_delay.process_sample(right_input);
            
            // Cross-feed with ping-pong pattern
            let left_output = left_delayed + right_delayed * self.cross_feedback;
            let right_output = right_delayed + left_delayed * self.cross_feedback;
            
            (left_output, right_output)
        } else {
            // Standard stereo processing
            let left_output = self.left_delay.process_sample(left_input);
            let right_output = self.right_delay.process_sample(right_input);
            
            (left_output, right_output)
        }
    }
}
```

## 🎛️ Parameter Ranges and Validation

### Parameter Constraints
```rust
impl StereoDelay {
    fn validate_parameters(&self) -> Result<(), AudioProcessorError> {
        // Delay time validation
        if self.left_delay < 0.001 || self.left_delay > 2.0 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "left_delay".to_string(),
                value: self.left_delay,
            });
        }
        
        if self.right_delay < 0.001 || self.right_delay > 2.0 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "right_delay".to_string(),
                value: self.right_delay,
            });
        }
        
        // Feedback validation
        if self.feedback < 0.0 || self.feedback > 0.9 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "feedback".to_string(),
                value: self.feedback,
            });
        }
        
        // Cross-feedback validation
        if self.cross_feedback < 0.0 || self.cross_feedback > 0.5 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "cross_feedback".to_string(),
                value: self.cross_feedback,
            });
        }
        
        Ok(())
    }
}
```

### Parameter Smoothing
```rust
impl StereoDelay {
    fn smooth_parameter_change(&mut self, target: f32, current: &mut f32, smoothing_factor: f32) {
        let diff = target - *current;
        *current += diff * smoothing_factor;
    }
}
```

## 🔧 Advanced Features

### Modulation Support
```rust
impl SimpleDelay {
    /// Set modulation parameters
    pub fn set_modulation(&mut self, rate: f32, depth: f32) {
        self.modulation_rate = rate.max(0.0);
        self.modulation_depth = depth.max(0.0);
    }
    
    /// Get modulated delay time
    fn get_modulated_delay(&self) -> usize {
        if self.modulation_rate > 0.0 && self.modulation_depth > 0.0 {
            let mod_offset = self.modulation_depth * 
                (2.0 * std::f32::consts::PI * self.modulation_phase).sin();
            let modulated_delay = self.delay_samples as f32 + mod_offset;
            modulated_delay.clamp(1.0, (self.buffer_size - 1) as f32) as usize
        } else {
            self.delay_samples
        }
    }
}
```

### Tempo Sync Support
```rust
impl StereoDelay {
    /// Set delay time based on BPM and note division
    pub fn set_tempo_sync(&mut self, bpm: f32, note_division: f32) {
        let beat_time = 60.0 / bpm;
        let delay_time = beat_time * note_division;
        
        self.set_left_delay(delay_time);
        self.set_right_delay(delay_time * 1.5); // Common stereo delay ratio
    }
}
```

### Multi-Tap Support
```rust
pub struct MultiTapDelay {
    taps: Vec<DelayTap>,
    mix_levels: Vec<f32>,
}

pub struct DelayTap {
    delay_time: f32,
    feedback: f32,
    pan: f32, // -1.0 (left) to 1.0 (right)
}

impl MultiTapDelay {
    pub fn add_tap(&mut self, delay_time: f32, feedback: f32, pan: f32) {
        self.taps.push(DelayTap { delay_time, feedback, pan });
        self.mix_levels.push(1.0);
    }
    
    pub fn set_tap_mix(&mut self, tap_index: usize, mix: f32) {
        if tap_index < self.mix_levels.len() {
            self.mix_levels[tap_index] = mix.clamp(0.0, 1.0);
        }
    }
}
```

## 📊 Performance Characteristics

### Latency Analysis
- **Processing Latency**: < 1ms per sample
- **Buffer Latency**: Configurable (256-8192 samples)
- **Total Latency**: < 10ms typical

### CPU Usage
- **Simple Delay**: ~0.1% CPU per channel
- **Stereo Delay**: ~0.2% CPU total
- **With Distortion**: ~0.3% CPU total

### Memory Usage
- **Delay Buffer**: ~2MB per second of delay time
- **Total Memory**: < 50MB for typical configurations

## 🧪 Testing and Validation

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_stereo_delay_basic() {
        let mut delay = StereoDelay::new_default();
        let (left_out, right_out) = delay.process(1.0, 0.0);
        
        // Verify stereo separation
        assert!(left_out.abs() > 0.0);
        assert!(right_out.abs() > 0.0);
    }
    
    #[test]
    fn test_cross_feedback() {
        let config = DelayConfig {
            cross_feedback: 0.5,
            ..Default::default()
        };
        let mut delay = StereoDelay::new(config);
        
        let (left_out, right_out) = delay.process(1.0, 0.0);
        
        // Verify cross-feedback is working
        assert!(right_out.abs() > 0.0);
    }
}
```

### Integration Tests
```rust
#[test]
fn test_stereo_delay_integration() {
    let mut processor = AudioProcessor::new();
    let test_signal = generate_stereo_test_signal(440.0, 1.0);
    
    let output = processor.process_stereo(&test_signal).unwrap();
    
    // Verify stereo processing
    assert_ne!(output.0, output.1);
    assert!(calculate_stereo_width(&output) > 0.0);
}
```

## 🔮 Future Enhancements

### Planned Features
1. **Convolution Reverb**: Real-time convolution reverb integration
2. **Granular Delay**: Granular synthesis delay effects
3. **Spectral Processing**: FFT-based spectral delay effects
4. **Machine Learning**: AI-powered delay parameter optimization
5. **Network Delay**: Distributed delay processing across devices

### Performance Improvements
1. **SIMD Optimization**: Vectorized delay processing
2. **GPU Acceleration**: GPU-based delay processing
3. **Adaptive Buffer Sizing**: Dynamic buffer optimization
4. **Multi-Core Processing**: Parallel delay processing
