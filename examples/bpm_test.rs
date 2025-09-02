use rust_audio_processor::{AudioProcessor, AudioConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 BPM Test - Demonstrating BPM-based delay timing");
    println!("==================================================\n");
    
    // Create a configuration with BPM
    let mut config = AudioConfig::default();
    
    // Test different BPM values
    let test_bpms = [60, 90, 120, 150, 180];
    
    for &bpm in &test_bpms {
        println!("🎵 Testing BPM: {}", bpm);
        
        // Set BPM and calculate delay times
        config.stereo_delay.set_bpm(bpm as f32);
        
        println!("  Left delay: {:.1}ms (1/4 note)", config.stereo_delay.left_delay * 1000.0);
        println!("  Right delay: {:.1}ms (1/2 note)", config.stereo_delay.right_delay * 1000.0);
        
        // Show all available note divisions for this BPM
        let delay_times = config.stereo_delay.get_delay_times_for_bpm(bpm as f32);
        println!("  Available note divisions:");
        for (note_name, delay_time) in delay_times {
            println!("    {}: {:.1}ms", note_name, delay_time * 1000.0);
        }
        println!();
    }
    
    // Test the audio processor with BPM
    println!("🎛️  Testing Audio Processor with BPM control:");
    let mut processor = AudioProcessor::with_config(config)?;
    
    // Set BPM to 120
    println!("  Setting BPM to 120...");
    processor.set_stereo_delay_parameter("bpm", 120.0)?;
    
    // Check status
    let status = processor.get_status()?;
    println!("  Current status:");
    for (key, value) in status {
        if key.contains("bpm") || key.contains("delay") || key.contains("note") {
            println!("    {}: {}", key, value);
        }
    }
    
    // Test changing BPM
    println!("\n🎵 Testing BPM changes:");
    for &bpm in &[60, 90, 120, 150] {
        println!("  Setting BPM to {}...", bpm);
        processor.set_stereo_delay_parameter("bpm", bpm as f32)?;
        
        let status = processor.get_status()?;
        if let Some(bpm_val) = status.get("bpm") {
            println!("    Current BPM: {}", bpm_val);
        }
        if let Some(left_delay) = status.get("left_delay_ms") {
            println!("    Left delay: {}ms", left_delay);
        }
        if let Some(right_delay) = status.get("right_delay_ms") {
            println!("    Right delay: {}ms", right_delay);
        }
        println!();
    }
    
    println!("✅ BPM test completed successfully!");
    println!("💡 Try running the interactive mode with 'cargo run' to use BPM control!");
    println!("   Use 'bpm=120' to set the tempo to 120 BPM");
    println!("   The left delay will be set to 1/4 note timing and right delay to 1/2 note timing");
    println!("   Individual delay parameters are now hidden from the CLI for simplicity");
    
    Ok(())
}
