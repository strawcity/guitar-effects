use cpal::traits::{DeviceTrait, HostTrait};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔍 Audio Device Diagnostic Tool");
    println!("===============================\n");
    
    let host = cpal::default_host();
    println!("🎵 Using host: {}", host.name());
    
    // List all input devices
    println!("\n📋 Input Devices:");
    if let Ok(devices) = host.input_devices() {
        for (i, device) in devices.enumerate() {
            if let Ok(name) = device.name() {
                println!("  [{}] {}", i, name);
                
                // Try to get supported configs
                if let Ok(configs) = device.supported_input_configs() {
                    for config in configs {
                        println!("      - {:?}", config);
                    }
                }
            }
        }
    } else {
        println!("  ❌ Could not enumerate input devices");
    }
    
    // List all output devices
    println!("\n📋 Output Devices:");
    if let Ok(devices) = host.output_devices() {
        for (i, device) in devices.enumerate() {
            if let Ok(name) = device.name() {
                println!("  [{}] {}", i, name);
                
                // Try to get supported configs
                if let Ok(configs) = device.supported_output_configs() {
                    for config in configs {
                        println!("      - {:?}", config);
                    }
                }
            }
        }
    } else {
        println!("  ❌ Could not enumerate output devices");
    }
    
    // Test default devices
    println!("\n🎤 Default Input Device:");
    if let Some(device) = host.default_input_device() {
        if let Ok(name) = device.name() {
            println!("  {}", name);
            if let Ok(config) = device.default_input_config() {
                println!("  Default config: {:?}", config);
            }
        }
    } else {
        println!("  ❌ No default input device");
    }
    
    println!("\n🔊 Default Output Device:");
    if let Some(device) = host.default_output_device() {
        if let Ok(name) = device.name() {
            println!("  {}", name);
            if let Ok(config) = device.default_output_config() {
                println!("  Default config: {:?}", config);
            }
        }
    } else {
        println!("  ❌ No default output device");
    }
    
    // Test device access
    println!("\n🧪 Testing Device Access:");
    
    if let Some(input_device) = host.default_input_device() {
        println!("  Testing input device: {}", input_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        match input_device.default_input_config() {
            Ok(config) => println!("    ✅ Input config: {:?}", config),
            Err(e) => println!("    ❌ Input config error: {:?}", e),
        }
    }
    
    if let Some(output_device) = host.default_output_device() {
        println!("  Testing output device: {}", output_device.name().unwrap_or_else(|_| "Unknown".to_string()));
        match output_device.default_output_config() {
            Ok(config) => println!("    ✅ Output config: {:?}", config),
            Err(e) => println!("    ❌ Output config error: {:?}", e),
        }
    }
    
    println!("\n💡 If you see errors above, try:");
    println!("  1. Running the fix_audio_io.sh script");
    println!("  2. Checking USB device connections");
    println!("  3. Rebooting the Raspberry Pi");
    println!("  4. Checking dmesg for USB errors");
    
    Ok(())
}
