use rust_audio_processor::{AudioProcessor, AudioConfig, config::{StereoDelayConfig, DistortionConfig}};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 Rust Audio Processor - Distortion Demo");
    println!("=========================================\n");
    
    // Create configuration with distortion enabled
    let config = AudioConfig {
        sample_rate: 44100,
        buffer_size: 1024,
        input_device: None,
        output_device: None,
        stereo_delay: StereoDelayConfig {
            left_delay: 0.3,
            right_delay: 0.6,
            feedback: 0.3,
            wet_mix: 0.6,
            ping_pong: true,
            stereo_width: 0.5,
            cross_feedback: 0.2,
        },
        distortion: DistortionConfig {
            enabled: true,
            distortion_type: "soft_clip".to_string(),
            drive: 0.5,
            mix: 0.7,
            feedback_intensity: 0.3,
        },
    };
    
    // Create audio processor
    let processor = AudioProcessor::with_config(config)?;
    
    println!("📋 Initial Configuration:");
    println!("  Sample rate: {} Hz", processor.get_config().sample_rate);
    println!("  Left delay: {:.0}ms", processor.get_config().stereo_delay.left_delay * 1000.0);
    println!("  Right delay: {:.0}ms", processor.get_config().stereo_delay.right_delay * 1000.0);
    println!("  Feedback: {:.0}%", processor.get_config().stereo_delay.feedback * 100.0);
    println!("  Wet mix: {:.0}%", processor.get_config().stereo_delay.wet_mix * 100.0);
    println!("  Distortion: {}", processor.get_config().distortion.distortion_type);
    println!("  Distortion drive: {:.0}%", processor.get_config().distortion.drive * 100.0);
    println!("  Distortion mix: {:.0}%", processor.get_config().distortion.mix * 100.0);
    
    println!("\n🎛️  Demonstrating Distortion Controls:");
    
    // Test different distortion types
    let distortion_types = ["soft_clip", "hard_clip", "tube", "fuzz", "bit_crush", "waveshaper"];
    
    for dist_type in &distortion_types {
        println!("  Setting distortion type to: {}", dist_type);
        processor.set_distortion_type(dist_type)?;
        
        // Test distortion parameters
        println!("    - Setting drive to 70%");
        processor.set_stereo_delay_parameter("distortion_drive", 0.7)?;
        
        println!("    - Setting mix to 80%");
        processor.set_stereo_delay_parameter("distortion_mix", 0.8)?;
        
        println!("    - Setting feedback intensity to 50%");
        processor.set_stereo_delay_parameter("distortion_feedback_intensity", 0.5)?;
        
        println!("    ✅ {} distortion configured!", dist_type);
    }
    
    // Test enabling/disabling distortion
    println!("\n🎛️  Testing Distortion Enable/Disable:");
    println!("  Disabling distortion...");
    processor.set_stereo_delay_parameter("distortion_enabled", 0.0)?;
    println!("  ✅ Distortion disabled");
    
    println!("  Enabling distortion...");
    processor.set_stereo_delay_parameter("distortion_enabled", 1.0)?;
    println!("  ✅ Distortion enabled");
    
    // Test delay parameters
    println!("\n🎛️  Testing Delay Parameters:");
    println!("  Setting left delay to 400ms");
    processor.set_stereo_delay_parameter("left_delay", 0.4)?;
    
    println!("  Setting right delay to 800ms");
    processor.set_stereo_delay_parameter("right_delay", 0.8)?;
    
    println!("  Setting feedback to 50%");
    processor.set_stereo_delay_parameter("feedback", 0.5)?;
    
    println!("  Setting wet mix to 80%");
    processor.set_stereo_delay_parameter("wet_mix", 0.8)?;
    
    println!("  Setting stereo width to 70%");
    processor.set_stereo_delay_parameter("stereo_width", 0.7)?;
    
    println!("  Setting cross feedback to 30%");
    processor.set_stereo_delay_parameter("cross_feedback", 0.3)?;
    
    println!("\n✅ All distortion and delay controls working!");
    println!("\n📋 How to use distortion in the interactive CLI:");
    println!("  1. Start the interactive mode: cargo run --release");
    println!("  2. Use these commands to control distortion:");
    println!("     distortion_type=soft_clip    # Set distortion type");
    println!("     distortion_enabled=1         # Enable distortion (0/1)");
    println!("     distortion_drive=0.5         # Set drive amount (0.0-1.0)");
    println!("     distortion_mix=0.7           # Set wet/dry mix (0.0-1.0)");
    println!("     distortion_feedback_intensity=0.3 # Set feedback intensity (0.0-1.0)");
    println!("\n🎛️  Available distortion types:");
    println!("     soft_clip, hard_clip, tube, fuzz, bit_crush, waveshaper");
    
    Ok(())
}
