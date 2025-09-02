# Troubleshooting

## Overview

This document provides solutions for common issues encountered when using the
Guitar Effects System. It covers platform-specific problems, audio issues,
performance problems, and general troubleshooting steps.

## 🔍 Quick Diagnostic Steps

### Basic System Check

```bash
# Check if the system is running
cargo run --release -- --status

# Test audio system
cargo run --release -- --test-audio

# List available audio devices
cargo run --release -- --list-devices

# Check system resources
htop
free -h
```

### Audio Device Check

```bash
# Check audio devices (macOS)
system_profiler SPAudioDataType

# Check audio devices (Linux)
aplay -l

# Check audio devices (Raspberry Pi)
lsusb
aplay -l
```

## 🍎 macOS Issues

### No Audio Output

#### Problem: No sound from Scarlett 2i2

**Symptoms**: Device detected but no audio output

**Solutions**:

1. **Check System Preferences**:

   ```bash
   # Open System Preferences > Sound
   open /System/Library/PreferencePanes/Sound.prefPane
   ```

2. **Reset Audio Permissions**:

   ```bash
   # Reset microphone permissions
   tccutil reset Microphone

   # Reset audio permissions
   sudo killall coreaudiod
   ```

3. **Check USB Connection**:

   - Disconnect and reconnect USB cable
   - Try different USB port
   - Check USB power supply

4. **Update Focusrite Drivers**:
   - Download latest drivers from Focusrite website
   - Install and restart system

#### Problem: High Latency

**Symptoms**: Delayed audio response, audio dropouts

**Solutions**:

1. **Adjust Buffer Size**:

   ```rust
   // Use smaller buffer for lower latency
   let config = AudioConfig {
       buffer_size: 256,  // Reduce from 512
       sample_rate: 48000,
       // ... other settings
   };
   ```

2. **Enable High-Latency Mode**:

   ```rust
   // Enable high-latency mode for stability
   set_audio_latency_mode(HighLatency);
   ```

3. **Check System Load**:

   ```bash
   # Monitor CPU usage
   top -o cpu

   # Check audio processes
   ps aux | grep audio
   ```

### Device Not Found

#### Problem: Scarlett 2i2 Not Detected

**Solutions**:

1. **Check Device List**:

   ```bash
   cargo run --release -- --list-devices
   ```

2. **Reset Audio System**:

   ```bash
   sudo killall coreaudiod
   sudo killall AudioServer
   ```

3. **Check USB Power**:
   - Ensure device has adequate power
   - Try powered USB hub if needed

## 🐧 Linux Issues

### Permission Problems

#### Problem: "Permission denied" for audio devices

**Symptoms**: Cannot access audio devices, ALSA errors

**Solutions**:

1. **Add User to Audio Group**:

   ```bash
   # Add user to audio group
   sudo usermod -a -G audio $USER

   # Add user to plugdev group
   sudo usermod -a -G plugdev $USER

   # Log out and log back in
   ```

2. **Fix Device Permissions**:

   ```bash
   # Fix audio device permissions
   sudo chmod 666 /dev/snd/*

   # Make permissions persistent
   echo 'KERNEL=="snd*", MODE="0666"' | sudo tee /etc/udev/rules.d/99-audio.rules
   ```

3. **Restart Audio Services**:

   ```bash
   # Restart PulseAudio
   pulseaudio --kill
   pulseaudio --start

   # Or restart ALSA
   sudo systemctl restart alsa-state
   ```

### ALSA Configuration Issues

#### Problem: ALSA device not found

**Solutions**:

1. **Check ALSA Devices**:

   ```bash
   # List ALSA devices
   aplay -l

   # List ALSA cards
   cat /proc/asound/cards
   ```

2. **Test ALSA**:

   ```bash
   # Test playback
   speaker-test -c 2 -t sine

   # Test with specific device
   aplay -D hw:0,0 /dev/zero
   ```

3. **Configure ALSA**:

   ```bash
   # Create ALSA configuration
   sudo nano ~/.asoundrc

   # Add device configuration
   pcm.!default {
       type hw
       card 0
       device 0
   }
   ```

### Real-Time Scheduling Issues

#### Problem: Audio dropouts, high latency

**Solutions**:

1. **Set Real-Time Priority**:

   ```bash
   # Set real-time priority limit
   ulimit -r 95

   # Make permanent
   echo '* soft rtprio 95' | sudo tee -a /etc/security/limits.conf
   echo '* hard rtprio 95' | sudo tee -a /etc/security/limits.conf
   ```

2. **Configure CPU Governor**:

   ```bash
   # Set performance governor
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

   # Make permanent
   echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
   ```

3. **Disable CPU Frequency Scaling**:
   ```bash
   # Disable frequency scaling
   sudo systemctl disable ondemand
   sudo systemctl enable performance
   ```

## 🍓 Raspberry Pi Issues

### USB Audio Problems

#### Problem: USB audio device not working

**Solutions**:

1. **Check USB Power**:

   ```bash
   # Check USB devices
   lsusb

   # Check USB power
   cat /sys/bus/usb/devices/*/power/runtime_status
   ```

2. **Fix USB Audio Issues**:

   ```bash
   # Add USB audio fix to cmdline.txt
   echo 'dwc_otg.fiq_fsm_enable=0' | sudo tee -a /boot/firmware/cmdline.txt

   # Reboot to apply changes
   sudo reboot
   ```

3. **Check Audio Group**:

   ```bash
   # Add user to audio group
   sudo usermod -a -G audio $USER

   # Check group membership
   groups $USER
   ```

### Performance Issues

#### Problem: High CPU usage, audio dropouts

**Solutions**:

1. **Optimize CPU Settings**:

   ```bash
   # Set performance governor
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

   # Disable CPU scaling
   sudo systemctl disable ondemand
   ```

2. **Increase Buffer Size**:

   ```rust
   // Use larger buffer for stability
   let config = AudioConfig {
       buffer_size: 2048,  // Increase from 1024
       sample_rate: 44100,
       // ... other settings
   };
   ```

3. **Monitor System Resources**:

   ```bash
   # Monitor CPU usage
   htop

   # Monitor memory usage
   free -h

   # Check temperature
   vcgencmd measure_temp
   ```

## 🔧 General Audio Issues

### No Sound Output

#### Problem: System running but no audio

**Solutions**:

1. **Check Audio Routing**:

   ```rust
   // Verify audio device selection
   let config = AudioConfig {
       input_device: Some("Scarlett 2i2".to_string()),
       output_device: Some("Scarlett 2i2".to_string()),
       // ... other settings
   };
   ```

2. **Test Audio System**:

   ```bash
   # Test with simple audio
   cargo run --release -- --test-audio

   # Check audio levels
   cargo run --release -- --status
   ```

3. **Check System Volume**:
   - Ensure system volume is not muted
   - Check application volume settings
   - Verify audio device is not muted

### Audio Dropouts

#### Problem: Intermittent audio dropouts

**Solutions**:

1. **Reduce Buffer Size**:

   ```rust
   // Use smaller buffer for lower latency
   let config = AudioConfig {
       buffer_size: 256,  // Reduce buffer size
       // ... other settings
   };
   ```

2. **Check System Load**:

   ```bash
   # Monitor system resources
   htop

   # Check for other audio processes
   ps aux | grep audio
   ```

3. **Optimize System Settings**:

   ```bash
   # Set real-time priority
   sudo nice -n -20 cargo run --release

   # Disable power management
   sudo systemctl disable power-management
   ```

### High Latency

#### Problem: Delayed audio response

**Solutions**:

1. **Optimize Buffer Settings**:

   ```rust
   // Use optimal buffer size for your system
   let config = AudioConfig {
       buffer_size: 512,   // Balance between latency and stability
       sample_rate: 48000, // Higher sample rate for lower latency
       // ... other settings
   };
   ```

2. **Enable Real-Time Processing**:

   ```rust
   // Enable real-time optimizations
   set_real_time_mode(true);
   set_thread_priority(ThreadPriority::RealTime);
   ```

3. **Check Audio Backend**:
   ```bash
   # Test different audio backends
   cargo run --release -- --audio-backend coreaudio  # macOS
   cargo run --release -- --audio-backend alsa      # Linux
   ```

## 🎛️ Effect-Specific Issues

### Stereo Delay Problems

#### Problem: No stereo separation

**Solutions**:

1. **Check Stereo Width Setting**:

   ```rust
   // Increase stereo width
   stereo_delay.set_stereo_width(0.5);  // Increase from 0.2
   ```

2. **Verify Ping-Pong Settings**:

   ```rust
   // Enable ping-pong for stereo effect
   stereo_delay.set_ping_pong(true);
   stereo_delay.set_cross_feedback(0.3);
   ```

3. **Check Delay Times**:
   ```rust
   // Ensure different delay times for stereo effect
   stereo_delay.set_left_delay(0.3);
   stereo_delay.set_right_delay(0.6);  // Different from left
   ```

#### Problem: Excessive feedback

**Solutions**:

1. **Reduce Feedback**:

   ```rust
   // Reduce feedback amount
   stereo_delay.set_feedback(0.2);  // Reduce from 0.5
   ```

2. **Adjust Cross-Feedback**:

   ```rust
   // Reduce cross-feedback
   stereo_delay.set_cross_feedback(0.1);  // Reduce from 0.3
   ```

3. **Check Wet Mix**:
   ```rust
   // Reduce wet mix
   stereo_delay.set_wet_mix(0.4);  // Reduce from 0.7
   ```

### Distortion Issues

#### Problem: Too much distortion

**Solutions**:

1. **Reduce Drive**:

   ```rust
   // Reduce distortion drive
   stereo_delay.set_cross_feedback_distortion(
       DistortionType::Tube,
       0.3,  // Reduce drive from 0.7
       0.6,  // Reduce mix
       0.4,  // Reduce feedback intensity
   );
   ```

2. **Change Distortion Type**:
   ```rust
   // Use softer distortion
   stereo_delay.set_cross_feedback_distortion(
       DistortionType::SoftClip,  // Softer than Tube
       0.4,
       0.5,
       0.3,
   );
   ```

#### Problem: No distortion effect

**Solutions**:

1. **Enable Distortion**:

   ```rust
   // Ensure distortion is enabled
   stereo_delay.set_cross_feedback_distortion(
       DistortionType::Tube,
       0.5,  // Increase drive
       0.8,  // Increase mix
       0.6,  // Increase feedback intensity
   );
   ```

2. **Check Cross-Feedback**:
   ```rust
   // Ensure cross-feedback is enabled
   stereo_delay.set_cross_feedback(0.3);
   ```

## 🔍 Debugging Tools

### System Diagnostics

```bash
# Check system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

# Check audio system
cargo run --release -- --diagnostics

# Monitor system resources
htop
iotop
```

### Audio Diagnostics

```bash
# Test audio devices
cargo run --release -- --test-audio

# List audio devices
cargo run --release -- --list-devices

# Check audio status
cargo run --release -- --status
```

### Performance Monitoring

```bash
# Monitor CPU usage
top -p $(pgrep rust_audio_processor)

# Monitor memory usage
ps -o pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head

# Check system load
uptime
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Run diagnostic commands**:
   ```bash
   cargo run --release -- --diagnostics
   ```
3. **Check system logs**:
   ```bash
   journalctl -u audio-processor
   dmesg | grep audio
   ```

### Information to Provide

When reporting issues, include:

1. **Platform**: macOS/Linux/Raspberry Pi
2. **System Information**: OS version, hardware specs
3. **Audio Device**: Make and model
4. **Error Messages**: Complete error output
5. **Steps to Reproduce**: Detailed reproduction steps
6. **Diagnostic Output**: Results from diagnostic commands

### Common Error Messages

#### "Device not found"

- Check USB connection
- Verify device drivers
- Test with different USB port

#### "Permission denied"

- Add user to audio group
- Fix device permissions
- Check file permissions

#### "Buffer underrun"

- Increase buffer size
- Reduce system load
- Check real-time settings

#### "High latency"

- Optimize buffer settings
- Enable real-time processing
- Check system performance
