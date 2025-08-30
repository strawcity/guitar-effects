use rust_audio_processor::{AudioProcessor, AudioConfig, config::{StereoDelayConfig, DistortionConfig}};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 Rust Audio Processor - Basic Usage Example");
    println!("=============================================\n");
    
    // Create a custom configuration
    let config = AudioConfig {
        sample_rate: 48000,
        buffer_size: 2048,
        stereo_delay: StereoDelayConfig {
            left_delay: 0.2,
            right_delay: 0.4,
            feedback: 0.5,
            wet_mix: 0.8,
            ping_pong: true,
            stereo_width: 0.7,
            cross_feedback: 0.3,
        },
        distortion: DistortionConfig {
            enabled: true,
            distortion_type: "tube".to_string(),
            drive: 0.4,
            mix: 0.6,
            feedback_intensity: 0.8,
        },
        ..Default::default()
    };
    
    // Create audio processor with custom configuration
    let mut processor = AudioProcessor::with_config(config)?;
    
    println!("✅ Audio processor created successfully!");
    println!("📊 Configuration:");
    println!("  Sample Rate: {} Hz", processor.get_config().sample_rate);
    println!("  Buffer Size: {} samples", processor.get_config().buffer_size);
    println!("  Left Delay: {:.1}ms", processor.get_config().stereo_delay.left_delay * 1000.0);
    println!("  Right Delay: {:.1}ms", processor.get_config().stereo_delay.right_delay * 1000.0);
    println!("  Feedback: {:.0}%", processor.get_config().stereo_delay.feedback * 100.0);
    println!("  Wet Mix: {:.0}%", processor.get_config().stereo_delay.wet_mix * 100.0);
    println!("  Distortion: {}", processor.get_config().distortion.distortion_type);
    
    // Generate a test tone
    println!("\n🎵 Generating test tone...");
    let sample_count = 48000; // 1 second at 48kHz
    let mut test_tone = Vec::with_capacity(sample_count);
    
    for i in 0..sample_count {
        let t = i as f32 / 48000.0;
        // Mix of different frequencies for more interesting sound
        let sample = 0.2 * (2.0 * std::f32::consts::PI * 440.0 * t).sin() +  // A note
                    0.1 * (2.0 * std::f32::consts::PI * 880.0 * t).sin() +  // A octave
                    0.05 * (2.0 * std::f32::consts::PI * 220.0 * t).sin(); // A lower
        test_tone.push(sample);
    }
    
    // Process the audio
    println!("🔧 Processing audio through stereo delay...");
    let processed_audio = processor.process_audio(&test_tone)?;
    
    println!("✅ Audio processing completed!");
    println!("📈 Input samples: {}", test_tone.len());
    println!("📉 Output samples: {}", processed_audio.len());
    
    // Show some statistics
    let input_max = test_tone.iter().fold(0.0f32, |a, &b| a.max(b.abs()));
    let output_max = processed_audio.iter().fold(0.0f32, |a, &b| a.max(b.abs()));
    
    println!("📊 Statistics:");
    println!("  Input max amplitude: {:.3}", input_max);
    println!("  Output max amplitude: {:.3}", output_max);
    println!("  Amplitude change: {:.1}%", (output_max / input_max * 100.0 - 100.0));
    
    // Test parameter adjustment
    println!("\n🎛️  Testing parameter adjustment...");
    
    processor.set_stereo_delay_parameter("feedback", 0.7)?;
    println!("✅ Increased feedback to 70%");
    
    processor.set_stereo_delay_parameter("stereo_width", 0.9)?;
    println!("✅ Increased stereo width to 90%");
    
    // Process again with new parameters
    let processed_audio2 = processor.process_audio(&test_tone)?;
    let output_max2 = processed_audio2.iter().fold(0.0f32, |a, &b| a.max(b.abs()));
    
    println!("📊 After parameter change:");
    println!("  Output max amplitude: {:.3}", output_max2);
    println!("  Amplitude change: {:.1}%", (output_max2 / input_max * 100.0 - 100.0));
    
    // Show system status
    println!("\n📋 System Status:");
    let status = processor.get_status()?;
    for (key, value) in status {
        println!("  {}: {}", key, value);
    }
    
    println!("\n🎉 Example completed successfully!");
    println!("💡 Try running the interactive mode with 'cargo run' for real-time control!");
    
    Ok(())
}
