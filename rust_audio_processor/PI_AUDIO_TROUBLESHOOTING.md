# Raspberry Pi Audio Troubleshooting Guide

## 🎸 Scarlett 2i2 USB Audio Interface Setup

This guide helps resolve common audio I/O errors when running the Rust audio
processor on Raspberry Pi with a Focusrite Scarlett 2i2 USB audio interface.

## 🔍 Quick Diagnosis

### 1. Run the Audio Fix Script

```bash
cd rust_audio_processor
chmod +x fix_audio_io.sh
./fix_audio_io.sh
```

### 2. Test Audio Device Detection

```bash
cargo run --release --example test_audio_devices
```

### 3. Check USB Device Status

```bash
dmesg | grep -i usb
lsusb
```

## 🚨 Common Issues and Solutions

### Issue: "Output test failed" in fix_audio_io.sh

**Symptoms:**

- `speaker-test` command fails
- Audio processor can't open output stream
- "Device not available" errors

**Solutions:**

1. **Check ALSA Configuration**

   ```bash
   cat /etc/asound.conf
   ```

   Should show:

   ```
   pcm.!default {
       type hw
       card 2
       device 0
   }
   ```

2. **Verify Device Permissions**

   ```bash
   ls -la /dev/snd/
   sudo chmod 666 /dev/snd/*
   ```

3. **Test Direct Device Access**

   ```bash
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1
   arecord -D hw:2,0 -c 2 -f S16_LE -r 48000 -d 1 /tmp/test.wav
   ```

4. **Check USB Power**
   - Try different USB ports
   - Use powered USB hub if available
   - Check if device appears in `lsusb`

### Issue: "No USB audio device found"

**Symptoms:**

- Device not detected by Rust audio processor
- Device names don't contain expected keywords

**Solutions:**

1. **Check Device Names**

   ```bash
   aplay -l
   arecord -l
   ```

2. **Update Device Detection** The Rust processor looks for devices containing:

   - "usb" (case insensitive)
   - "scarlett" (case insensitive)
   - "focusrite" (case insensitive)
   - "2i2" (case insensitive)

3. **Manual Device Selection**
   ```bash
   # Run with explicit device specification
   cargo run --release -- --device hw:2,0
   ```

### Issue: PulseAudio Conflicts

**Symptoms:**

- Timeout errors
- "Device busy" errors
- Audio not working after PulseAudio starts

**Solutions:**

1. **Disable PulseAudio**

   ```bash
   pulseaudio --kill
   sudo systemctl disable pulseaudio
   ```

2. **Use Direct ALSA**

   ```bash
   # Test with direct ALSA device
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1
   ```

3. **Check for PulseAudio Processes**
   ```bash
   ps aux | grep pulse
   killall pulseaudio
   ```

### Issue: Sample Rate/Format Mismatch

**Symptoms:**

- "Unsupported format" errors
- Audio distortion or no sound

**Solutions:**

1. **Check Supported Formats**

   ```bash
   amixer -c 2 sget 'USB Audio'
   ```

2. **Force Sample Rate**

   ```bash
   # Add to /etc/asound.conf
   pcm.!default {
       type hw
       card 2
       device 0
       rate 48000
       format S16_LE
       channels 2
   }
   ```

3. **Test Different Formats**

   ```bash
   # Test 44.1kHz
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -r 44100 -l 1

   # Test 48kHz
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -r 48000 -l 1
   ```

## 🔧 Advanced Troubleshooting

### Debug Audio Device Access

1. **Run Diagnostic Tool**

   ```bash
   cargo run --release --example test_audio_devices
   ```

2. **Check ALSA Debug Output**

   ```bash
   export ALSA_DEBUG=1
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1
   ```

3. **Monitor System Logs**
   ```bash
   dmesg -w | grep -i audio
   journalctl -f | grep -i audio
   ```

### USB Power Management Issues

1. **Disable USB Power Management**

   ```bash
   # Add to /boot/config.txt
   max_usb_current=1
   ```

2. **Check USB Power**

   ```bash
   cat /sys/bus/usb/devices/*/power/runtime_status
   ```

3. **Force USB Power**
   ```bash
   echo on > /sys/bus/usb/devices/*/power/runtime_status
   ```

### Kernel Module Issues

1. **Check Loaded Modules**

   ```bash
   lsmod | grep snd
   lsmod | grep usb
   ```

2. **Reload Audio Modules**

   ```bash
   sudo modprobe -r snd_usb_audio
   sudo modprobe snd_usb_audio
   ```

3. **Check Module Parameters**
   ```bash
   modinfo snd_usb_audio
   ```

## 📋 Step-by-Step Recovery

### Complete Reset Procedure

1. **Stop All Audio Processes**

   ```bash
   pulseaudio --kill
   killall -9 speaker-test
   killall -9 arecord
   ```

2. **Reset ALSA Configuration**

   ```bash
   sudo rm /etc/asound.conf
   sudo alsa force-reload
   ```

3. **Recreate ALSA Configuration**

   ```bash
   ./fix_audio_io.sh
   ```

4. **Test Basic Audio**

   ```bash
   speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1
   arecord -D hw:2,0 -c 2 -f S16_LE -r 48000 -d 1 /tmp/test.wav
   ```

5. **Test Rust Audio Processor**
   ```bash
   cargo run --release
   # Then type: start
   ```

### If Still Not Working

1. **Reboot the Raspberry Pi**

   ```bash
   sudo reboot
   ```

2. **Try Different USB Ports**

   - USB 2.0 ports often work better than USB 3.0
   - Try powered USB hub

3. **Check Hardware**

   - Test Scarlett 2i2 on another computer
   - Try different USB cable
   - Check if device lights up

4. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade
   sudo rpi-update  # Only if needed
   ```

## 🎯 Expected Behavior

### Successful Setup Should Show:

1. **Device Detection:**

   ```
   [0] Scarlett 2i2 USB
   ```

2. **Audio Test Results:**

   ```
   ✅ Output test successful
   ✅ Input test successful
   ```

3. **Rust Processor Output:**
   ```
   🎵 Audio streams started - input and output are now active!
   ```

### Common Error Messages:

- `Device not available` → Check device permissions and ALSA config
- `Format not supported` → Check sample rate and format settings
- `Device busy` → Stop other audio processes
- `Timeout` → Check USB power and connections

## 📞 Getting Help

If you're still having issues:

1. Run the diagnostic tools and save output
2. Check system logs: `dmesg | grep -i usb`
3. Test with different USB ports
4. Try a different USB audio interface if available
5. Check the GitHub issues for similar problems

## 🔗 Useful Commands

```bash
# Audio device info
aplay -l && arecord -l

# USB device info
lsusb && dmesg | grep -i usb

# ALSA info
amixer -c 2 contents

# Test audio
speaker-test -D hw:2,0 -c 2 -t sine -f 440 -l 1

# Monitor audio
watch -n 1 'cat /proc/asound/card*/pcm*/sub*/status'
```
