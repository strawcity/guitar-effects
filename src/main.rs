use rust_audio_processor::{config::AudioConfig, audio_processor::AudioProcessor, AudioProcessorTrait, web_server::WebServer};
#[cfg(target_os = "linux")]
use rust_audio_processor::alsa_processor::AlsaAudioProcessor;
use std::io::{self, Write};
use std::env;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use chrono;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 Rust Audio Processor for Guitar Stereo Delay Effects");
    println!("=====================================================\n");
    
    // Parse command line arguments
    let args: Vec<String> = env::args().collect();
    let is_daemon_mode = args.contains(&"--daemon".to_string());
    let enable_web = args.contains(&"--web".to_string());
    let web_port = args.iter().position(|arg| arg == "--web-port")
        .and_then(|i| args.get(i + 1))
        .and_then(|s| s.parse::<u16>().ok())
        .unwrap_or(1051);
    let _device_arg = args.iter().position(|arg| arg == "--device").map(|i| args.get(i + 1));
    
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
    let processor = AlsaAudioProcessor::with_config(config)?;
    #[cfg(not(target_os = "linux"))]
    let processor = AudioProcessor::with_config(config)?;
    
    // Wrap processor in Arc<Mutex> for sharing between threads
    let processor_arc = Arc::new(Mutex::new(Box::new(processor) as Box<dyn AudioProcessorTrait + Send>));
    
    // Test the audio processing
    println!("Testing audio processing...");
    {
        let processor_guard = processor_arc.lock().unwrap();
        match processor_guard.test_audio() {
            Ok(_) => println!("✅ Audio test completed successfully"),
            Err(e) => {
                println!("⚠️  Audio test failed: {}", e);
                println!("💡 This is normal if no audio devices are connected or configured.");
                println!("   The processor will still work for processing audio data.");
            }
        }
    }
    
    if is_daemon_mode {
        println!("🔧 Running in daemon mode - starting audio processing...");
        daemon_mode(processor_arc)?;
    } else if enable_web {
        println!("🌐 Running with web interface...");
        web_mode(processor_arc, web_port).await?;
    } else {
        println!("🎛️  Running in interactive mode...");
        interactive_mode(processor_arc)?;
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
    println!("  --web                Run with web interface");
    println!("  --web-port <port>    Web interface port (default: 1051)");
    println!("  --device <device>    Specify audio device (e.g., hw:2,0)");
    println!();
    println!("Examples:");
    println!("  cargo run --release                    # Interactive mode");
    println!("  cargo run --release --daemon           # Daemon mode");
    println!("  cargo run --release --web              # Web interface mode");
    println!("  cargo run --release --web --web-port 9090  # Custom port");
    println!("  cargo run --release --device hw:2,0    # Use specific device");
    println!();
    println!("Interactive Commands:");
    println!("  start               - Start real-time audio processing");
    println!("  stop                - Stop real-time audio processing");
    println!("  reset               - Reset delay buffers (clear feedback)");
    println!("  status              - Show current system status");
    println!("  test                - Run audio test");
    println!("  quit/exit           - Exit the program");
    println!();
    println!("Parameter Settings (format: parameter=value):");
    println!("  bpm=120              - Tempo in beats per minute (20-300 BPM)");
    println!("  feedback=0.3        - Feedback amount (0.0-0.9)");
    println!("  wet_mix=0.6         - Wet signal mix (0.0-1.0)");
    println!("  stereo_width=0.5    - Stereo width enhancement (0.0-1.0)");
    println!("  cross_feedback=0.2  - Cross-feedback between channels (0.0-0.5)");
}

fn daemon_mode(processor: Arc<Mutex<Box<dyn AudioProcessorTrait + Send>>>) -> Result<(), Box<dyn std::error::Error>> {
    println!("🎵 Starting audio processing daemon...");
    println!("📊 Initial status:");
    show_status(&**processor.lock().unwrap())?;
    
    // Start real-time audio processing
    println!("🎸 Starting real-time audio processing...");
    {
        let mut processor_guard = processor.lock().unwrap();
        match processor_guard.start_audio() {
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
        {
            let processor_guard = processor.lock().unwrap();
            if let Ok(status) = processor_guard.get_status() {
                if status.get("audio_running").map(|s| s == "true").unwrap_or(false) {
                    // Audio is running, continue
                } else {
                    println!("⚠️  Audio processing stopped, attempting restart...");
                    drop(processor_guard); // Release lock before calling start_audio
                    let mut processor_guard = processor.lock().unwrap();
                    if let Err(e) = processor_guard.start_audio() {
                        println!("⚠️  Audio restart failed: {}", e);
                        println!("💡 This is normal if no audio devices are available.");
                    } else {
                        println!("✅ Audio processing restarted successfully!");
                    }
                }
            }
        }
    }
}

async fn web_mode(processor: Arc<Mutex<Box<dyn AudioProcessorTrait + Send>>>, port: u16) -> Result<(), Box<dyn std::error::Error>> {
    println!("🌐 Starting web interface mode...");
    println!("📊 Initial status:");
    show_status(&**processor.lock().unwrap())?;
    
    // Start real-time audio processing
    println!("🎸 Starting real-time audio processing...");
    {
        let mut processor_guard = processor.lock().unwrap();
        match processor_guard.start_audio() {
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
    }
    
    println!("🌐 Starting web server...");
    println!("📱 Web interface will be available at:");
    println!("   http://localhost:{}", port);
    println!("   http://0.0.0.0:{} (from other devices on network)", port);
    
    // Create web server with the shared processor
    let web_server = WebServer::new(processor);
    web_server.start(port).await?;
    
    Ok(())
}

fn interactive_mode(processor: Arc<Mutex<Box<dyn AudioProcessorTrait + Send>>>) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🎛️  Interactive Parameter Control");
    println!("Type 'help' for available commands, 'quit' to exit");
    println!("📱 Web interface changes will be shown here\n");
    
    // Store last known parameter values for change detection
    let mut last_status: HashMap<String, f32> = HashMap::new();
    
    // Main interactive loop
    loop {
        print!("> ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let input = input.trim();
        
        // Check for parameter changes before processing input
        {
            let processor_guard = processor.lock().unwrap();
            if let Ok(status) = processor_guard.get_status() {
                for (key, value_str) in &status {
                    if let Ok(value) = value_str.parse::<f32>() {
                        if let Some(last_value) = last_status.get(key) {
                            if (value - last_value).abs() > 0.001 {
                                // Value changed! Show notification
                                show_parameter_change_notification(key, *last_value, value);
                            }
                        }
                        last_status.insert(key.clone(), value);
                    }
                }
            }
        }
        
        match input {
            "help" => show_help(),
            "quit" | "exit" => break,
            "status" => {
                let processor_guard = processor.lock().unwrap();
                show_status(&**processor_guard)?;
            }
            "test" => {
                println!("Running audio test...");
                let processor_guard = processor.lock().unwrap();
                processor_guard.test_audio()?;
            }
            "start" => {
                println!("Starting real-time audio processing...");
                let mut processor_guard = processor.lock().unwrap();
                match processor_guard.start_audio() {
                    Ok(_) => println!("✅ Real-time audio processing started!"),
                    Err(e) => println!("❌ Error: {}", e),
                }
            }
            "stop" => {
                println!("Stopping real-time audio processing...");
                let mut processor_guard = processor.lock().unwrap();
                match processor_guard.stop_audio() {
                    Ok(_) => println!("✅ Real-time audio processing stopped!"),
                    Err(e) => println!("❌ Error: {}", e),
                }
            }
            "reset" => {
                println!("Resetting delay buffers...");
                let mut processor_guard = processor.lock().unwrap();
                match processor_guard.reset_delay() {
                    Ok(_) => println!("✅ Delay buffers reset!"),
                    Err(e) => println!("❌ Error: {}", e),
                }
            }
            _ => {
                if let Some((param, value)) = parse_parameter(input) {
                    let mut processor_guard = processor.lock().unwrap();
                    match processor_guard.set_stereo_delay_parameter(param, value) {
                        Ok(_) => {
                            println!("✅ Set {} to {:.3}", param, value);
                            // Update last known value
                            last_status.insert(param.to_string(), value);
                        }
                        Err(e) => println!("❌ Error: {}", e),
                    }
                } else if input.starts_with("distortion_type=") {
                    // Handle distortion type command
                    let distortion_type = input.strip_prefix("distortion_type=").unwrap_or("");
                    let mut processor_guard = processor.lock().unwrap();
                    match processor_guard.set_distortion_type(distortion_type) {
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

fn show_parameter_change_notification(param: &str, old_value: f32, new_value: f32) {
    let timestamp = chrono::Local::now().format("%H:%M:%S");
    
    // Format the parameter name nicely
    let param_display = match param {
        "left_delay" => "Left Delay",
        "right_delay" => "Right Delay", 
        "feedback" => "Feedback",
        "wet_mix" => "Wet Mix",
        "stereo_width" => "Stereo Width",
        "cross_feedback" => "Cross Feedback",
        "bpm" => "BPM",
        "distortion_drive" => "Distortion Drive",
        "distortion_mix" => "Distortion Mix",
        "distortion_feedback_intensity" => "Distortion Feedback",
        _ => param,
    };
    
    // Format values appropriately
    let old_display = if param.contains("delay") || param == "bpm" {
        if param == "bpm" {
            format!("{:.0} BPM", old_value)
        } else {
            format!("{:.2}s", old_value)
        }
    } else {
        format!("{:.2}", old_value)
    };
    
    let new_display = if param.contains("delay") || param == "bpm" {
        if param == "bpm" {
            format!("{:.0} BPM", new_value)
        } else {
            format!("{:.2}s", new_value)
        }
    } else {
        format!("{:.2}", new_value)
    };
    
    println!("\n🌐 [{}] Web Interface: {} changed from {} to {}", 
             timestamp, param_display, old_display, new_display);
    print!("> "); // Restore prompt
    io::stdout().flush().unwrap();
}

fn show_help() {
    println!("\n📋 Available Commands:");
    println!("  help                    - Show this help message");
    println!("  status                  - Show current system status");
    println!("  test                    - Run audio test");
    println!("  start                   - Start real-time audio processing");
    println!("  stop                    - Stop real-time audio processing");
    println!("  reset                   - Reset delay buffers (clear feedback)");
    println!("  quit/exit               - Exit the program");
    println!("\n🎛️  Parameter Settings (format: parameter=value):");
    println!("  bpm=120              - Tempo in beats per minute (20-300 BPM)");
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
    println!("\n📱 Web Interface:");
    println!("  Changes from web interface will be shown as notifications");
    println!("  Perfect for remote control via Pi-Connect!");
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
