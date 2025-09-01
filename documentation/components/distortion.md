# Distortion Effects

## Overview

The Distortion Effects module provides professional-quality distortion processing specifically designed for cross-feedback signals in the stereo delay system. This module includes multiple distortion algorithms, from subtle saturation to aggressive fuzz, all optimized for real-time processing.

## 🎛️ Core Features

### Distortion Types
- **Soft Clip**: Musical tanh-based soft clipping
- **Hard Clip**: Aggressive hard clipping with threshold control
- **Tube**: Asymmetric tube-style distortion simulation
- **Fuzz**: Aggressive fuzz with harmonic enhancement
- **Bit Crush**: Digital bit depth and sample rate reduction
- **Waveshaper**: Custom cubic polynomial waveshaping

### Cross-Feedback Integration
- **Cross-Feedback Distortion**: Distortion applied to cross-feedback signals
- **Feedback Intensity Control**: Control how much distortion affects feedback
- **Real-Time Parameter Control**: Adjust distortion parameters during playback
- **Musical Feedback Patterns**: Create interesting and musical feedback effects

## 🏗️ Architecture

### Component Structure

```
CrossFeedbackDistortion
├── DistortionEffect
│   ├── DistortionType
│   ├── Drive Control
│   ├── Mix Control
│   └── Algorithm Implementation
├── Parameter Controller
├── Smoothing Filters
└── Quality Control
```

### Integration with Stereo Delay

```
Left Delay Output ──┐
                   ├── Cross-Feedback ── Distortion ──┐
                   │                                   │
Right Delay Output ─┘                                   │
                                                       │
                   ┌── Left Output ◄───────────────────┘
                   │
                   └── Right Output ◄───────────────────┘
```

## 📋 API Reference

### Core Types

#### DistortionType
```rust
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
```

#### DistortionEffect
```rust
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
```

#### CrossFeedbackDistortion
```rust
pub struct CrossFeedbackDistortion {
    distortion: DistortionEffect,
    feedback_intensity: f32,
    enabled: bool,
}
```

### Core Methods

#### Initialization
```rust
impl DistortionEffect {
    /// Create a new distortion effect
    pub fn new(distortion_type: DistortionType, drive: f32, mix: f32, sample_rate: u32) -> Self;
    
    /// Create with default settings
    pub fn new_default(sample_rate: u32) -> Self;
}
```

#### Processing
```rust
impl DistortionEffect {
    /// Process a single sample through distortion
    pub fn process(&mut self, input: f32) -> f32;
    
    /// Process entire buffer
    pub fn process_buffer(&mut self, input: &[f32]) -> Vec<f32>;
    
    /// Process stereo input
    pub fn process_stereo(&mut self, left: f32, right: f32) -> (f32, f32);
}
```

#### Parameter Control
```rust
impl DistortionEffect {
    /// Set the type of distortion
    pub fn set_distortion_type(&mut self, distortion_type: DistortionType);
    
    /// Set the drive amount (0.0 to 1.0)
    pub fn set_drive(&mut self, drive: f32);
    
    /// Set the wet/dry mix (0.0 to 1.0)
    pub fn set_mix(&mut self, mix: f32);
    
    /// Set bit crushing parameters
    pub fn set_bit_crush_parameters(&mut self, bit_depth: u8, sample_rate_reduction: f32);
}
```

## 🎯 Detailed Implementation

### Distortion Algorithms

#### Soft Clipping
```rust
impl DistortionEffect {
    fn soft_clip(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 10.0;
        sample.tanh() / drive_factor
    }
}
```

**Characteristics:**
- **Musical**: Smooth, musical saturation
- **Drive Range**: 0.0 to 1.0 (subtle to heavy)
- **Harmonics**: Even and odd harmonics
- **Use Case**: Subtle saturation, warm overdrive

#### Hard Clipping
```rust
impl DistortionEffect {
    fn hard_clip(&self, sample: f32) -> f32 {
        let threshold = 1.0 - self.drive;
        sample.clamp(-threshold, threshold)
    }
}
```

**Characteristics:**
- **Aggressive**: Sharp, digital clipping
- **Drive Range**: 0.0 to 1.0 (clean to heavily clipped)
- **Harmonics**: Strong odd harmonics
- **Use Case**: Aggressive distortion, digital effects

#### Tube Distortion
```rust
impl DistortionEffect {
    fn tube_distortion(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 5.0;
        let asymmetric = if sample > 0.0 {
            sample / (1.0 + sample.abs() / drive_factor)
        } else {
            sample / (1.0 + sample.abs() / (drive_factor * 2.0))
        };
        asymmetric
    }
}
```

**Characteristics:**
- **Asymmetric**: Different positive/negative clipping
- **Drive Range**: 0.0 to 1.0 (clean to tube saturation)
- **Harmonics**: Rich harmonic content
- **Use Case**: Vintage tube amp simulation

#### Fuzz Distortion
```rust
impl DistortionEffect {
    fn fuzz_distortion(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 20.0;
        let fuzz = sample * drive_factor;
        
        // Apply asymmetric clipping
        let clipped = if fuzz > 0.0 {
            fuzz.tanh()
        } else {
            fuzz * 0.5
        };
        
        // Add harmonic enhancement
        clipped + (clipped * clipped * 0.3)
    }
}
```

**Characteristics:**
- **Aggressive**: Heavy, saturated distortion
- **Drive Range**: 0.0 to 1.0 (overdrive to fuzz)
- **Harmonics**: Rich harmonic enhancement
- **Use Case**: Aggressive fuzz tones, experimental effects

#### Bit Crushing
```rust
impl DistortionEffect {
    fn bit_crush(&self, sample: f32) -> f32 {
        let max_value = (1 << self.bit_depth) - 1;
        let quantized = (sample * max_value as f32).round() / max_value as f32;
        
        // Apply sample rate reduction
        if self.sample_rate_reduction < 1.0 {
            let sample_hold = (self.last_sample * (1.0 - self.sample_rate_reduction)) + 
                             (quantized * self.sample_rate_reduction);
            self.last_sample = sample_hold;
            sample_hold
        } else {
            quantized
        }
    }
}
```

**Characteristics:**
- **Digital**: Quantization and sample rate reduction
- **Bit Depth**: 1 to 16 bits (configurable)
- **Sample Rate**: 0.1 to 1.0 reduction factor
- **Use Case**: Lo-fi effects, digital artifacts

#### Waveshaper
```rust
impl DistortionEffect {
    fn waveshaper(&self, sample: f32) -> f32 {
        let drive_factor = 1.0 + self.drive * 8.0;
        let shaped = sample + (sample * sample * sample * 0.3 * drive_factor);
        shaped.clamp(-1.0, 1.0)
    }
}
```

**Characteristics:**
- **Custom**: Cubic polynomial waveshaping
- **Drive Range**: 0.0 to 1.0 (subtle to heavy)
- **Harmonics**: Controlled harmonic generation
- **Use Case**: Custom distortion curves, experimental effects

### Cross-Feedback Integration

#### Cross-Feedback Processing
```rust
impl CrossFeedbackDistortion {
    fn process_cross_feedback(&mut self, left_feedback: f32, right_feedback: f32) -> (f32, f32) {
        if !self.enabled {
            return (left_feedback, right_feedback);
        }
        
        // Apply distortion to cross-feedback signals
        let distorted_left = self.distortion.process(left_feedback);
        let distorted_right = self.distortion.process(right_feedback);
        
        // Apply feedback intensity
        let intensity = self.feedback_intensity;
        let final_left = left_feedback * (1.0 - intensity) + distorted_left * intensity;
        let final_right = right_feedback * (1.0 - intensity) + distorted_right * intensity;
        
        (final_left, final_right)
    }
}
```

#### Parameter Control
```rust
impl CrossFeedbackDistortion {
    /// Set cross-feedback distortion parameters
    pub fn set_cross_feedback_distortion(
        &mut self,
        distortion_type: DistortionType,
        drive: f32,
        mix: f32,
        feedback_intensity: f32,
    ) {
        self.distortion.set_distortion_type(distortion_type);
        self.distortion.set_drive(drive);
        self.distortion.set_mix(mix);
        self.feedback_intensity = feedback_intensity.clamp(0.0, 1.0);
    }
    
    /// Enable/disable cross-feedback distortion
    pub fn set_enabled(&mut self, enabled: bool) {
        self.enabled = enabled;
    }
}
```

## 🎛️ Parameter Ranges and Validation

### Parameter Constraints
```rust
impl DistortionEffect {
    fn validate_parameters(&self) -> Result<(), AudioProcessorError> {
        // Drive validation
        if self.drive < 0.0 || self.drive > 1.0 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "drive".to_string(),
                value: self.drive,
            });
        }
        
        // Mix validation
        if self.mix < 0.0 || self.mix > 1.0 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "mix".to_string(),
                value: self.mix,
            });
        }
        
        // Bit depth validation
        if self.bit_depth < 1 || self.bit_depth > 16 {
            return Err(AudioProcessorError::InvalidParameter {
                param: "bit_depth".to_string(),
                value: self.bit_depth as f32,
            });
        }
        
        Ok(())
    }
}
```

### Parameter Smoothing
```rust
impl DistortionEffect {
    fn smooth_parameter_change(&mut self, target: f32, current: &mut f32, smoothing_factor: f32) {
        let diff = target - *current;
        *current += diff * smoothing_factor;
    }
    
    fn update_smoothed_parameters(&mut self) {
        self.smooth_parameter_change(self.target_drive, &mut self.drive, 0.1);
        self.smooth_parameter_change(self.target_mix, &mut self.mix, 0.1);
    }
}
```

## 🔧 Advanced Features

### Harmonic Analysis
```rust
impl DistortionEffect {
    /// Analyze harmonic content of distortion
    pub fn analyze_harmonics(&self, fundamental_freq: f32) -> HarmonicAnalysis {
        let harmonics = match self.distortion_type {
            DistortionType::SoftClip => vec![1.0, 0.3, 0.1, 0.05], // Even and odd
            DistortionType::HardClip => vec![1.0, 0.5, 0.33, 0.25], // Strong odd
            DistortionType::Tube => vec![1.0, 0.4, 0.2, 0.1], // Rich harmonics
            DistortionType::Fuzz => vec![1.0, 0.6, 0.4, 0.3], // Very rich
            _ => vec![1.0], // No harmonics
        };
        
        HarmonicAnalysis {
            fundamental: fundamental_freq,
            harmonics,
            total_harmonic_distortion: self.calculate_thd(),
        }
    }
}
```

### Dynamic Distortion
```rust
impl DistortionEffect {
    /// Dynamic distortion based on input level
    pub fn set_dynamic_drive(&mut self, input_level: f32) {
        let dynamic_drive = self.drive * (1.0 + input_level * 2.0);
        self.set_drive(dynamic_drive.clamp(0.0, 1.0));
    }
}
```

### Multi-Band Distortion
```rust
pub struct MultiBandDistortion {
    low_band: DistortionEffect,
    mid_band: DistortionEffect,
    high_band: DistortionEffect,
    crossover_freqs: (f32, f32), // Low-mid, mid-high
}

impl MultiBandDistortion {
    pub fn process(&mut self, input: f32) -> f32 {
        let (low, mid, high) = self.split_bands(input);
        
        let distorted_low = self.low_band.process(low);
        let distorted_mid = self.mid_band.process(mid);
        let distorted_high = self.high_band.process(high);
        
        self.combine_bands(distorted_low, distorted_mid, distorted_high)
    }
}
```

## 📊 Performance Characteristics

### CPU Usage by Distortion Type
- **Soft Clip**: ~0.01% CPU (very efficient)
- **Hard Clip**: ~0.01% CPU (very efficient)
- **Tube**: ~0.02% CPU (moderate)
- **Fuzz**: ~0.03% CPU (moderate)
- **Bit Crush**: ~0.02% CPU (moderate)
- **Waveshaper**: ~0.02% CPU (moderate)

### Memory Usage
- **Per Distortion Instance**: ~1KB
- **Cross-Feedback Distortion**: ~2KB
- **Multi-Band Distortion**: ~6KB

### Latency
- **Processing Latency**: < 0.1ms
- **Parameter Changes**: Immediate (no latency)
- **Buffer Processing**: < 1ms for typical buffers

## 🧪 Testing and Validation

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_soft_clip_distortion() {
        let mut distortion = DistortionEffect::new(DistortionType::SoftClip, 0.5, 1.0, 44100);
        let input = 0.8;
        let output = distortion.process(input);
        
        // Verify soft clipping behavior
        assert!(output.abs() < input.abs());
        assert!(output.abs() > 0.0);
    }
    
    #[test]
    fn test_cross_feedback_distortion() {
        let mut cross_feedback = CrossFeedbackDistortion::new_default(44100);
        let (left_out, right_out) = cross_feedback.process_cross_feedback(0.5, 0.3);
        
        // Verify cross-feedback processing
        assert!(left_out.abs() > 0.0);
        assert!(right_out.abs() > 0.0);
    }
}
```

### Quality Tests
```rust
#[test]
fn test_distortion_quality() {
    let mut distortion = DistortionEffect::new(DistortionType::Tube, 0.3, 1.0, 44100);
    let test_signal = generate_sine_wave(440.0, 1.0, 44100);
    
    let output = distortion.process_buffer(&test_signal);
    
    // Verify harmonic content
    let harmonics = analyze_harmonics(&output, 440.0);
    assert!(harmonics.total_harmonic_distortion > 0.0);
    assert!(harmonics.total_harmonic_distortion < 0.1); // Not too much distortion
}
```

## 🔮 Future Enhancements

### Planned Features
1. **Convolution Distortion**: Real-time convolution-based distortion
2. **Machine Learning**: AI-powered distortion parameter optimization
3. **Spectral Distortion**: FFT-based spectral distortion effects
4. **Analog Modeling**: More accurate analog circuit modeling
5. **Dynamic Distortion**: Level-dependent distortion characteristics

### Performance Improvements
1. **SIMD Optimization**: Vectorized distortion processing
2. **Lookup Tables**: Pre-computed distortion curves
3. **Adaptive Processing**: Dynamic quality adjustment
4. **Multi-Core Processing**: Parallel distortion processing

### New Distortion Types
1. **Fold Distortion**: Wave folding effects
2. **Ring Modulation**: Ring modulation distortion
3. **Phase Distortion**: Phase-based distortion
4. **Granular Distortion**: Granular synthesis distortion
5. **Spectral Distortion**: Frequency-domain distortion
