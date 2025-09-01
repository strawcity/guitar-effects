# Examples & Tutorials

## Overview

This document provides comprehensive examples and tutorials for using the Guitar
Effects System. From basic usage to advanced configurations, these examples
demonstrate the full capabilities of the stereo delay effects system.

## 🚀 Quick Start Examples

### Basic Stereo Delay

#### Simple Stereo Delay Setup

```rust
use rust_audio_processor::{StereoDelay, DelayConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create basic stereo delay configuration
    let config = DelayConfig {
        left_delay: 0.3,      // 300ms left delay
        right_delay: 0.6,     // 600ms right delay
        feedback: 0.3,        // 30% feedback
        wet_mix: 0.6,         // 60% wet signal
        ping_pong: false,     // No ping-pong
        stereo_width: 0.2,    // 20% stereo width enhancement
        cross_feedback: 0.1,  // 10% cross-feedback
    };

    let mut stereo_delay = StereoDelay::new(config);

    // Process audio samples
    let (left_output, right_output) = stereo_delay.process(0.5, 0.3);

    println!("Left output: {}, Right output: {}", left_output, right_output);
    Ok(())
}
```

#### Real-Time Parameter Control

```rust
use rust_audio_processor::{StereoDelay, DelayConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut stereo_delay = StereoDelay::new_default();

    // Real-time parameter adjustment
    stereo_delay.set_left_delay(0.4);    // 400ms left delay
    stereo_delay.set_right_delay(0.8);   // 800ms right delay
    stereo_delay.set_feedback(0.5);       // 50% feedback
    stereo_delay.set_wet_mix(0.7);        // 70% wet signal
    stereo_delay.set_ping_pong(true);     // Enable ping-pong
    stereo_delay.set_stereo_width(0.3);    // 30% stereo width
    stereo_delay.set_cross_feedback(0.2); // 20% cross-feedback

    Ok(())
}
```

### Cross-Feedback Distortion

#### Basic Distortion Setup

```rust
use rust_audio_processor::{StereoDelay, DelayConfig, DistortionType};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = DelayConfig {
        left_delay: 0.3,
        right_delay: 0.6,
        feedback: 0.4,
        wet_mix: 0.6,
        ping_pong: true,
        stereo_width: 0.2,
        cross_feedback: 0.3,
    };

    let mut stereo_delay = StereoDelay::new(config);

    // Enable cross-feedback distortion
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Tube,  // Tube-style distortion
        0.4,                   // Drive amount
        0.8,                   // Mix amount
        0.6,                   // Feedback intensity
    );

    Ok(())
}
```

#### Multiple Distortion Types

```rust
use rust_audio_processor::{StereoDelay, DistortionType};

fn distortion_examples() {
    let mut stereo_delay = StereoDelay::new_default();

    // Soft clipping for subtle saturation
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::SoftClip,
        0.2,  // Subtle drive
        0.5,  // Moderate mix
        0.3,  // Low feedback intensity
    );

    // Tube distortion for vintage character
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Tube,
        0.5,  // Medium drive
        0.7,  // Higher mix
        0.5,  // Medium feedback intensity
    );

    // Fuzz distortion for aggressive effects
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Fuzz,
        0.8,  // High drive
        0.9,  // High mix
        0.7,  // High feedback intensity
    );

    // Bit crushing for lo-fi effects
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::BitCrush,
        0.6,  // Medium drive
        0.6,  // Medium mix
        0.4,  // Medium feedback intensity
    );
}
```

## 🎛️ Advanced Examples

### Ping-Pong Delay Patterns

#### Classic Ping-Pong

```rust
fn ping_pong_example() {
    let mut stereo_delay = StereoDelay::new_default();

    // Classic ping-pong setup
    stereo_delay.set_left_delay(0.3);     // 300ms left
    stereo_delay.set_right_delay(0.6);    // 600ms right (2x left)
    stereo_delay.set_ping_pong(true);     // Enable ping-pong
    stereo_delay.set_cross_feedback(0.4); // Strong cross-feedback
    stereo_delay.set_feedback(0.3);       // Moderate feedback
    stereo_delay.set_wet_mix(0.7);        // High wet mix
}
```

#### Rhythmic Ping-Pong

```rust
fn rhythmic_ping_pong() {
    let mut stereo_delay = StereoDelay::new_default();

    // Rhythmic ping-pong with tempo sync
    let bpm = 120.0;
    let beat_time = 60.0 / bpm; // 0.5 seconds per beat

    stereo_delay.set_left_delay(beat_time * 0.5);  // Eighth note
    stereo_delay.set_right_delay(beat_time * 1.0); // Quarter note
    stereo_delay.set_ping_pong(true);
    stereo_delay.set_cross_feedback(0.5);
    stereo_delay.set_feedback(0.4);
}
```

### Stereo Width Enhancement

#### Mid-Side Processing

```rust
fn stereo_width_example() {
    let mut stereo_delay = StereoDelay::new_default();

    // Enhanced stereo width
    stereo_delay.set_stereo_width(0.5);   // 50% enhancement
    stereo_delay.set_left_delay(0.3);
    stereo_delay.set_right_delay(0.6);
    stereo_delay.set_cross_feedback(0.2);

    // Process stereo signal
    let (left_input, right_input) = (0.5, 0.3);
    let (left_output, right_output) = stereo_delay.process(left_input, right_input);

    // Calculate stereo width
    let stereo_width = (left_output - right_output).abs();
    println!("Stereo width: {}", stereo_width);
}
```

### Tempo-Synchronized Delays

#### BPM Sync Setup

```rust
fn tempo_sync_example() {
    let mut stereo_delay = StereoDelay::new_default();

    let bpm = 140.0;
    let beat_time = 60.0 / bpm;

    // Common delay ratios
    let eighth_note = beat_time * 0.5;
    let quarter_note = beat_time * 1.0;
    let dotted_eighth = beat_time * 0.75;
    let half_note = beat_time * 2.0;

    // Set up rhythmic delays
    stereo_delay.set_left_delay(eighth_note);
    stereo_delay.set_right_delay(dotted_eighth);
    stereo_delay.set_feedback(0.3);
    stereo_delay.set_wet_mix(0.6);
}
```

#### Dynamic Tempo Changes

```rust
fn dynamic_tempo_example() {
    let mut stereo_delay = StereoDelay::new_default();

    // Function to update delays based on tempo
    fn update_tempo_delays(delay: &mut StereoDelay, bpm: f32) {
        let beat_time = 60.0 / bpm;

        delay.set_left_delay(beat_time * 0.5);
        delay.set_right_delay(beat_time * 0.75);
    }

    // Update delays for different tempos
    update_tempo_delays(&mut stereo_delay, 120.0); // 120 BPM
    update_tempo_delays(&mut stereo_delay, 140.0); // 140 BPM
    update_tempo_delays(&mut stereo_delay, 160.0); // 160 BPM
}
```

## 🎸 Guitar-Specific Examples

### Electric Guitar Setup

#### Clean Guitar Delay

```rust
fn clean_guitar_delay() {
    let mut stereo_delay = StereoDelay::new_default();

    // Clean guitar delay settings
    stereo_delay.set_left_delay(0.4);     // 400ms left
    stereo_delay.set_right_delay(0.8);    // 800ms right
    stereo_delay.set_feedback(0.2);        // Light feedback
    stereo_delay.set_wet_mix(0.4);         // Subtle wet mix
    stereo_delay.set_ping_pong(true);      // Enable ping-pong
    stereo_delay.set_stereo_width(0.3);   // Moderate stereo width
    stereo_delay.set_cross_feedback(0.1); // Light cross-feedback
}
```

#### Overdriven Guitar Delay

```rust
fn overdriven_guitar_delay() {
    let mut stereo_delay = StereoDelay::new_default();

    // Overdriven guitar delay settings
    stereo_delay.set_left_delay(0.3);     // Shorter delays
    stereo_delay.set_right_delay(0.6);
    stereo_delay.set_feedback(0.4);       // More feedback
    stereo_delay.set_wet_mix(0.6);         // Higher wet mix
    stereo_delay.set_ping_pong(true);
    stereo_delay.set_stereo_width(0.4);
    stereo_delay.set_cross_feedback(0.2);

    // Add tube distortion to cross-feedback
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Tube,
        0.5,  // Medium drive
        0.7,  // Higher mix
        0.5,  // Medium feedback intensity
    );
}
```

### Acoustic Guitar Setup

#### Acoustic Guitar Delay

```rust
fn acoustic_guitar_delay() {
    let mut stereo_delay = StereoDelay::new_default();

    // Acoustic guitar delay settings
    stereo_delay.set_left_delay(0.5);     // Longer delays
    stereo_delay.set_right_delay(1.0);     // Even longer right
    stereo_delay.set_feedback(0.15);      // Very light feedback
    stereo_delay.set_wet_mix(0.3);         // Subtle wet mix
    stereo_delay.set_ping_pong(false);     // No ping-pong for natural sound
    stereo_delay.set_stereo_width(0.2);    // Light stereo width
    stereo_delay.set_cross_feedback(0.05); // Minimal cross-feedback
}
```

## 🎛️ Effect Chain Examples

### Stereo Delay with Multiple Effects

#### Basic Effect Chain

```rust
fn basic_effect_chain() {
    let mut stereo_delay = StereoDelay::new_default();

    // Set up stereo delay
    stereo_delay.set_left_delay(0.3);
    stereo_delay.set_right_delay(0.6);
    stereo_delay.set_feedback(0.3);
    stereo_delay.set_wet_mix(0.6);
    stereo_delay.set_ping_pong(true);

    // Add cross-feedback distortion
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::SoftClip,
        0.3,
        0.6,
        0.4,
    );

    // Process audio chain
    let input_samples = vec![0.5, 0.3, 0.7, 0.2];
    let mut output_samples = Vec::new();

    for &input in &input_samples {
        let (left_out, right_out) = stereo_delay.process(input, input);
        output_samples.push((left_out, right_out));
    }
}
```

### Advanced Effect Chain

#### Complex Stereo Processing

```rust
fn complex_stereo_processing() {
    let mut stereo_delay = StereoDelay::new_default();

    // Complex stereo delay setup
    stereo_delay.set_left_delay(0.25);     // 250ms left
    stereo_delay.set_right_delay(0.75);    // 750ms right
    stereo_delay.set_feedback(0.5);        // High feedback
    stereo_delay.set_wet_mix(0.8);         // High wet mix
    stereo_delay.set_ping_pong(true);
    stereo_delay.set_stereo_width(0.6);    // High stereo width
    stereo_delay.set_cross_feedback(0.4);  // High cross-feedback

    // Add fuzz distortion to cross-feedback
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Fuzz,
        0.7,  // High drive
        0.8,  // High mix
        0.6,  // High feedback intensity
    );

    // Process stereo input
    let left_input = vec![0.5, 0.3, 0.7, 0.2];
    let right_input = vec![0.4, 0.6, 0.3, 0.8];

    let mut left_output = Vec::new();
    let mut right_output = Vec::new();

    for i in 0..left_input.len() {
        let (left_out, right_out) = stereo_delay.process(left_input[i], right_input[i]);
        left_output.push(left_out);
        right_output.push(right_out);
    }
}
```

## 🔧 Configuration Examples

### Platform-Specific Configuration

#### macOS Configuration

```rust
fn macos_config() {
    use rust_audio_processor::config::AudioConfig;

    let config = AudioConfig {
        sample_rate: 48000,           // Higher sample rate for macOS
        buffer_size: 512,             // Smaller buffer for lower latency
        input_device: Some("Scarlett 2i2".to_string()),
        output_device: Some("Scarlett 2i2".to_string()),
        stereo_delay: StereoDelayConfig {
            left_delay: 0.3,
            right_delay: 0.6,
            feedback: 0.3,
            wet_mix: 0.6,
            ping_pong: true,
            stereo_width: 0.3,
            cross_feedback: 0.2,
        },
        distortion: DistortionConfig {
            enabled: true,
            distortion_type: "tube".to_string(),
            drive: 0.4,
            mix: 0.7,
            feedback_intensity: 0.5,
        },
    };
}
```

#### Raspberry Pi Configuration

```rust
fn raspberry_pi_config() {
    use rust_audio_processor::config::AudioConfig;

    let config = AudioConfig {
        sample_rate: 44100,           // Standard sample rate
        buffer_size: 1024,            // Larger buffer for stability
        input_device: Some("USB Audio Device".to_string()),
        output_device: Some("USB Audio Device".to_string()),
        stereo_delay: StereoDelayConfig {
            left_delay: 0.3,
            right_delay: 0.6,
            feedback: 0.3,
            wet_mix: 0.6,
            ping_pong: true,
            stereo_width: 0.3,
            cross_feedback: 0.2,
        },
        distortion: DistortionConfig {
            enabled: true,
            distortion_type: "soft_clip".to_string(),
            drive: 0.3,
            mix: 0.6,
            feedback_intensity: 0.4,
        },
    };
}
```

### Performance Optimization

#### Low Latency Configuration

```rust
fn low_latency_config() {
    let mut stereo_delay = StereoDelay::new_default();

    // Low latency settings
    stereo_delay.set_left_delay(0.1);     // Very short delays
    stereo_delay.set_right_delay(0.2);
    stereo_delay.set_feedback(0.2);        // Light feedback
    stereo_delay.set_wet_mix(0.5);         // Moderate wet mix
    stereo_delay.set_ping_pong(false);     // No ping-pong for lower latency
    stereo_delay.set_stereo_width(0.2);    // Light stereo width
    stereo_delay.set_cross_feedback(0.1);  // Light cross-feedback
}
```

#### High Quality Configuration

```rust
fn high_quality_config() {
    let mut stereo_delay = StereoDelay::new_default();

    // High quality settings
    stereo_delay.set_left_delay(0.5);     // Longer delays
    stereo_delay.set_right_delay(1.0);
    stereo_delay.set_feedback(0.4);        // More feedback
    stereo_delay.set_wet_mix(0.7);         // Higher wet mix
    stereo_delay.set_ping_pong(true);      // Enable ping-pong
    stereo_delay.set_stereo_width(0.5);    // Higher stereo width
    stereo_delay.set_cross_feedback(0.3);  // More cross-feedback

    // Add high-quality distortion
    stereo_delay.set_cross_feedback_distortion(
        DistortionType::Tube,
        0.5,
        0.8,
        0.6,
    );
}
```

## 🧪 Testing Examples

### Unit Test Examples

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use rust_audio_processor::{StereoDelay, DelayConfig};

    #[test]
    fn test_basic_stereo_delay() {
        let mut delay = StereoDelay::new_default();
        let (left_out, right_out) = delay.process(1.0, 0.0);

        // Verify stereo processing
        assert!(left_out.abs() > 0.0);
        assert!(right_out.abs() > 0.0);
        assert_ne!(left_out, right_out);
    }

    #[test]
    fn test_ping_pong_delay() {
        let config = DelayConfig {
            ping_pong: true,
            cross_feedback: 0.5,
            ..Default::default()
        };
        let mut delay = StereoDelay::new(config);

        let (left_out, right_out) = delay.process(1.0, 0.0);

        // Verify ping-pong behavior
        assert!(right_out.abs() > 0.0);
    }

    #[test]
    fn test_parameter_validation() {
        let mut delay = StereoDelay::new_default();

        // Test valid parameters
        delay.set_feedback(0.5);
        delay.set_wet_mix(0.7);
        delay.set_cross_feedback(0.3);

        // Test invalid parameters (should be clamped)
        delay.set_feedback(1.5);  // Should be clamped to 0.9
        delay.set_wet_mix(1.5);   // Should be clamped to 1.0
        delay.set_cross_feedback(0.8); // Should be clamped to 0.5
    }
}
```

### Integration Test Examples

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

#[test]
fn test_real_time_parameter_changes() {
    let mut stereo_delay = StereoDelay::new_default();

    // Test real-time parameter changes
    stereo_delay.set_left_delay(0.3);
    let (left1, right1) = stereo_delay.process(1.0, 0.0);

    stereo_delay.set_left_delay(0.6);
    let (left2, right2) = stereo_delay.process(1.0, 0.0);

    // Verify parameter changes take effect
    assert_ne!(left1, left2);
}
```

## 🔮 Advanced Usage Examples

### Custom Effect Chains

```rust
fn custom_effect_chain() {
    let mut stereo_delay = StereoDelay::new_default();

    // Custom effect chain with multiple stages
    fn process_custom_chain(delay: &mut StereoDelay, input: f32) -> (f32, f32) {
        // Stage 1: Basic stereo delay
        let (left1, right1) = delay.process(input, input);

        // Stage 2: Apply cross-feedback distortion
        delay.set_cross_feedback_distortion(
            DistortionType::Tube,
            0.4,
            0.7,
            0.5,
        );

        // Stage 3: Enhanced stereo width
        delay.set_stereo_width(0.6);

        delay.process(left1, right1)
    }

    // Process audio through custom chain
    let input_samples = vec![0.5, 0.3, 0.7, 0.2];
    let mut output_samples = Vec::new();

    for &input in &input_samples {
        let output = process_custom_chain(&mut stereo_delay, input);
        output_samples.push(output);
    }
}
```

### Dynamic Effect Control

```rust
fn dynamic_effect_control() {
    let mut stereo_delay = StereoDelay::new_default();

    // Dynamic effect control based on input level
    fn process_with_dynamic_control(delay: &mut StereoDelay, input: f32) -> (f32, f32) {
        let input_level = input.abs();

        // Adjust feedback based on input level
        let dynamic_feedback = (0.2 + input_level * 0.4).clamp(0.0, 0.9);
        delay.set_feedback(dynamic_feedback);

        // Adjust distortion drive based on input level
        let dynamic_drive = (0.3 + input_level * 0.4).clamp(0.0, 1.0);
        delay.set_cross_feedback_distortion(
            DistortionType::Tube,
            dynamic_drive,
            0.7,
            0.5,
        );

        delay.process(input, input)
    }

    // Process audio with dynamic control
    let input_samples = vec![0.1, 0.5, 0.9, 0.3];
    let mut output_samples = Vec::new();

    for &input in &input_samples {
        let output = process_with_dynamic_control(&mut stereo_delay, input);
        output_samples.push(output);
    }
}
```

## 📚 Additional Resources

### Related Documentation

- **[System Architecture](architecture.md)** - Understanding the overall system
  design
- **[Audio Processing Pipeline](audio-pipeline.md)** - Detailed audio processing
  flow
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Performance Guide](performance.md)** - Performance optimization tips

### Example Files

- **[Basic Usage Example](../examples/basic_usage.rs)** - Simple stereo delay
  example
- **[Distortion Demo](../examples/distortion_demo.rs)** - Distortion effect
  demonstrations
- **[Audio Device Test](../examples/test_audio_devices.rs)** - Audio device
  testing

### Best Practices

1. **Start Simple**: Begin with basic stereo delay before adding complexity
2. **Test Parameters**: Always validate parameter ranges and test edge cases
3. **Monitor Performance**: Watch CPU usage and latency during development
4. **Use Real Audio**: Test with real guitar input for best results
5. **Document Configurations**: Keep track of successful parameter combinations
