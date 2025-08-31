use rust_audio_processor::{config::AudioConfig, audio_processor::AudioProcessor, AudioProcessorTrait};
#[cfg(target_os = "linux")]
use rust_audio_processor::alsa_processor::AlsaAudioProcessor;
use std::io::{self, Write};
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 Rust Audio Processor for Guitar Stereo Delay Effects");
    println!("=====================================================\n");
    
    // Parse command line arguments
    let args: Vec<String> = env::args().collect();
    let is_daemon_mode = args.contains(&"--daemon".to_string());
    let device_arg = args.iter().position(|arg| arg == "--device").map(|i| args.get(i + 1));
    
    // Show help if requested
    if args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
        show_cli_help();
        return Ok(());
    }
    
    // Load configuration from file or use default
    let config = AudioConfig::load_or_default("pi_config.json");
    println!("📋 Loaded configuration:");
    println!("   Sample rate: {} Hz", config.sample_rate);
    println!("   Buffer size: {}", config.buffer_size);
    println!("   Input device: {:?}", config.input_device);
    println!("   Output device: {:?}", config.output_device);
    
    // Create audio processor with loaded configuration
    #[cfg(target_os = "linux")]
    let mut processor = AlsaAudioProcessor::with_config(config)?;
    #[cfg(not(target_os = "linux"))]
    let mut processor = AudioProcessor::with_config(config)?;
    
    // Test the audio processing
    println!("Testing audio processing...");
    match processor.test_audio() {
        Ok(_) => println!("✅ Audio test completed successfully"),
        Err(e) => {
            println!("⚠️  Audio test failed: {}", e);
            println!("💡 This is normal if no audio devices are connected or configured.");
            println!("   The processor will still work for processing audio data.");
        }
    }
    
    if is_daemon_mode {
        println!("🔧 Running in daemon mode - starting audio processing...");
        daemon_mode(&mut processor)?;
    } else {
        println!("🎛️  Running in interactive mode...");
        interactive_mode(&mut processor)?;
    }
    
    Ok(())
}

fn show_cli_help() {
    println!("🎸 Rust Audio Processor - Command Line Options");
    println!("===============================================");
    println!();
    println!("Usage: cargo run --release [OPTIONS]");
    println!();
    println!("Options:");
    println!("  --help, -h           Show this help message");
    println!("  --daemon             Run in daemon mode (non-interactive)");
    println!("  --device <device>    Specify audio device (e.g., hw:2,0)");
    println!();
    println!("Examples:");
    println!("  cargo run --release                    # Interactive mode");
    println!("  cargo run --release --daemon           # Daemon mode");
    println!("  cargo run --release --device hw:2,0    # Use specific device");
    println!();
    println!("Interactive Commands:");
    println!("  start               - Start real-time audio processing");
    println!("  stop                - Stop real-time audio processing");
    println!("  status              - Show current system status");
    println!("  test                - Run audio test");
    println!("  quit/exit           - Exit the program");
    println!();
    println!("Parameter Settings (format: parameter=value):");
    println!("  left_delay=0.3      - Left channel delay time (seconds)");
    println!("  right_delay=0.6     - Right channel delay time (seconds)");
    println!("  feedback=0.3        - Feedback amount (0.0-0.9)");
    println!("  wet_mix=0.6         - Wet signal mix (0.0-1.0)");
    println!("  stereo_width=0.5    - Stereo width enhancement (0.0-1.0)");
    println!("  cross_feedback=0.2  - Cross-feedback between channels (0.0-0.5)");
}

fn daemon_mode(processor: &mut dyn AudioProcessorTrait) -> Result<(), Box<dyn std::error::Error>> {
    println!("🎵 Starting audio processing daemon...");
    println!("📊 Initial status:");
    show_status(processor)?;
    
    // Start real-time audio processing
    println!("🎸 Starting real-time audio processing...");
    match processor.start_audio() {
        Ok(_) => {
            println!("✅ Real-time audio processing started successfully!");
            println!("🎵 Audio is now running and processing input from your audio device.");
        }
        Err(e) => {
            println!("⚠️  Failed to start real-time audio processing: {}", e);
            println!("💡 This is normal if no audio devices are connected or configured.");
            println!("   The processor will still work for processing audio data.");
        }
    }
    
    println!("🎸 Audio processor daemon running. Use systemctl to control the service.");
    println!("📋 Available commands:");
    println!("  sudo systemctl stop rust-audio-processor    - Stop the service");
    println!("  sudo systemctl restart rust-audio-processor - Restart the service");
    println!("  sudo journalctl -u rust-audio-processor -f  - View logs");
    
    // Keep the daemon running
    loop {
        std::thread::sleep(std::time::Duration::from_secs(60));
        
        // Optional: periodic status check
        if let Ok(status) = processor.get_status() {
            if status.get("audio_running").map(|s| s == "true").unwrap_or(false) {
                // Audio is running, continue
            } else {
                println!("⚠️  Audio processing stopped, attempting restart...");
                if let Err(e) = processor.start_audio() {
                    println!("⚠️  Audio restart failed: {}", e);
                    println!("💡 This is normal if no audio devices are available.");
                } else {
                    println!("✅ Audio processing restarted successfully!");
                }
            }
        }
    }
}

fn interactive_mode(processor: &mut dyn AudioProcessorTrait) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🎛️  Interactive Parameter Control");
    println!("Type 'help' for available commands, 'quit' to exit\n");
    
    loop {
        print!("> ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();
        
        match input {
            "help" => show_help(),
            "quit" | "exit" => break,
            "status" => show_status(processor)?,
            "test" => {
                println!("Running audio test...");
                processor.test_audio()?;
            }
            "start" => {
                println!("Starting real-time audio processing...");
                match processor.start_audio() {
                    Ok(_) => println!("✅ Real-time audio processing started!"),
                    Err(e) => println!("❌ Error: {}", e),
                }
            }
            "stop" => {
                println!("Stopping real-time audio processing...");
                match processor.stop_audio() {
                    Ok(_) => println!("✅ Real-time audio processing stopped!"),
                    Err(e) => println!("❌ Error: {}", e),
                }
            }
            _ => {
                if let Some((param, value)) = parse_parameter(input) {
                    match processor.set_stereo_delay_parameter(param, value) {
                        Ok(_) => println!("✅ Set {} to {:.3}", param, value),
                        Err(e) => println!("❌ Error: {}", e),
                    }
                } else if input.starts_with("distortion_type=") {
                    // Handle distortion type command
                    let distortion_type = input.strip_prefix("distortion_type=").unwrap_or("");
                    match processor.set_distortion_type(distortion_type) {
                        Ok(_) => println!("✅ Set distortion type to {}", distortion_type),
                        Err(e) => println!("❌ Error: {}", e),
                    }
                } else {
                    println!("❓ Unknown command. Type 'help' for available commands.");
                }
            }
        }
    }
    
    Ok(())
}

fn show_help() {
    println!("\n📋 Available Commands:");
    println!("  help                    - Show this help message");
    println!("  status                  - Show current system status");
    println!("  test                    - Run audio test");
    println!("  start                   - Start real-time audio processing");
    println!("  stop                    - Stop real-time audio processing");
    println!("  quit/exit               - Exit the program");
    println!("\n🎛️  Parameter Settings (format: parameter=value):");
    println!("  left_delay=0.3          - Left channel delay time (seconds)");
    println!("  right_delay=0.6         - Right channel delay time (seconds)");
    println!("  feedback=0.3            - Feedback amount (0.0-0.9)");
    println!("  wet_mix=0.6             - Wet signal mix (0.0-1.0)");
    println!("  stereo_width=0.5        - Stereo width enhancement (0.0-1.0)");
    println!("  cross_feedback=0.2      - Cross-feedback between channels (0.0-0.5)");
    println!("\n🎸 Distortion Commands:");
    println!("  distortion_type=soft_clip    - Set distortion type");
    println!("  distortion_enabled=1        - Enable/disable distortion (0/1)");
    println!("  distortion_drive=0.5        - Distortion drive amount (0.0-1.0)");
    println!("  distortion_mix=0.7          - Distortion wet/dry mix (0.0-1.0)");
    println!("  distortion_feedback_intensity=0.3 - How much distortion affects feedback (0.0-1.0)");
    println!("\n🎛️  Available Distortion Types:");
    println!("  soft_clip, hard_clip, tube, fuzz, bit_crush, waveshaper");
    println!("\nExample: feedback=0.5");
}

fn show_status(processor: &dyn AudioProcessorTrait) -> Result<(), Box<dyn std::error::Error>> {
    let status = processor.get_status()?;
    println!("\n📊 System Status:");
    for (key, value) in status {
        println!("  {}: {}", key, value);
    }
    Ok(())
}

fn parse_parameter(input: &str) -> Option<(&str, f32)> {
    if let Some(pos) = input.find('=') {
        let param = &input[..pos];
        if let Ok(value) = input[pos + 1..].parse::<f32>() {
            return Some((param, value));
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parameter_parsing() {
        assert_eq!(parse_parameter("feedback=0.5"), Some(("feedback", 0.5)));
        assert_eq!(parse_parameter("wet_mix=0.8"), Some(("wet_mix", 0.8)));
        assert_eq!(parse_parameter("invalid"), None);
        assert_eq!(parse_parameter("param=invalid"), None);
    }
}
