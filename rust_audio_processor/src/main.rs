use rust_audio_processor::AudioProcessor;
use std::io::{self, Write};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎸 Rust Audio Processor for Guitar Stereo Delay Effects");
    println!("=====================================================\n");
    
    // Create audio processor with default configuration
    let mut processor = AudioProcessor::new()?;
    
    // Test the audio processing
    println!("Testing audio processing...");
    processor.test_audio()?;
    
    // Interactive parameter adjustment
    interactive_mode(&mut processor)?;
    
    Ok(())
}

fn interactive_mode(processor: &mut AudioProcessor) -> Result<(), Box<dyn std::error::Error>> {
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
            _ => {
                if let Some((param, value)) = parse_parameter(input) {
                    match processor.set_stereo_delay_parameter(param, value) {
                        Ok(_) => println!("✅ Set {} to {:.3}", param, value),
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
    println!("  quit/exit               - Exit the program");
    println!("\n🎛️  Parameter Settings (format: parameter=value):");
    println!("  left_delay=0.3          - Left channel delay time (seconds)");
    println!("  right_delay=0.6         - Right channel delay time (seconds)");
    println!("  feedback=0.3            - Feedback amount (0.0-0.9)");
    println!("  wet_mix=0.6             - Wet signal mix (0.0-1.0)");
    println!("  stereo_width=0.5        - Stereo width enhancement (0.0-1.0)");
    println!("  cross_feedback=0.2      - Cross-feedback between channels (0.0-0.5)");
    println!("\nExample: feedback=0.5");
}

fn show_status(processor: &AudioProcessor) -> Result<(), Box<dyn std::error::Error>> {
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
