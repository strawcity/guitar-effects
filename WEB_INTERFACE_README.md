# Guitar Effects Web Interface

A modern web interface for controlling your guitar effects system from any
device on your network.

## 🌐 Features

- **Real-time Control**: Adjust all parameters in real-time
- **Mobile-Friendly**: Works on phones, tablets, and computers
- **Network Access**: Control from any device on your network
- **Visual Feedback**: Real-time status updates and notifications
- **Professional UI**: Modern, responsive design with knobs and controls

## 🚀 Quick Start

### 1. Build the Project

```bash
cargo build --release
```

### 2. Start Web Interface

```bash
# Start with default port (1051)
cargo run --release -- --web

# Start with custom port
cargo run --release -- --web --web-port 9090
```

### 3. Access the Interface

Open your web browser and navigate to:

- **Local**: `http://localhost:1051`
- **Network**: `http://[raspberry-pi-ip]:1051`
- **Mobile**: Use your phone's browser to access the Pi's IP address

## 🎛️ Controls

### System Controls

- **Start Audio**: Begin real-time audio processing
- **Stop Audio**: Stop audio processing
- **Reset Delay**: Clear delay buffers and feedback

### Stereo Delay Controls

- **Left Delay**: Left channel delay time (0-2 seconds)
- **Right Delay**: Right channel delay time (0-2 seconds)
- **Feedback**: Delay feedback amount (0-0.9)
- **Wet Mix**: Wet/dry signal mix (0-1)
- **Stereo Width**: Stereo width enhancement (0-1)
- **Cross Feedback**: Cross-feedback between channels (0-0.5)
- **BPM**: Tempo-based timing (20-300 BPM)
- **Ping Pong**: Enable ping-pong delay pattern

### Distortion Controls

- **Enabled**: Enable/disable distortion
- **Type**: Distortion algorithm (Soft Clip, Hard Clip, Tube, Fuzz, etc.)
- **Drive**: Distortion drive amount (0-1)
- **Mix**: Distortion wet/dry mix (0-1)
- **Feedback Intensity**: How much distortion affects feedback (0-1)

## 📱 Mobile Usage

The web interface is fully responsive and works great on mobile devices:

1. **Connect to the same network** as your Raspberry Pi
2. **Find your Pi's IP address**: `hostname -I` or check your router
3. **Open your phone's browser** and navigate to `http://[pi-ip]:8080`
4. **Control your effects** with touch-friendly knobs and buttons

## 🔧 System Service

### Install as System Service (Raspberry Pi)

```bash
# Copy service file
sudo cp guitar-effects-web.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable guitar-effects-web
sudo systemctl start guitar-effects-web

# Check status
sudo systemctl status guitar-effects-web

# View logs
sudo journalctl -u guitar-effects-web -f
```

### Service Management

```bash
# Start service
sudo systemctl start guitar-effects-web

# Stop service
sudo systemctl stop guitar-effects-web

# Restart service
sudo systemctl restart guitar-effects-web

# View logs
sudo journalctl -u guitar-effects-web -f
```

## 🌐 Network Configuration

### Find Your Pi's IP Address

```bash
# Method 1: hostname command
hostname -I

# Method 2: ip command
ip addr show | grep inet

# Method 3: Check router admin panel
```

### Port Configuration

The web interface runs on port 8080 by default. You can change this:

```bash
# Custom port
cargo run --release -- --web --web-port 9090

# Or edit the service file
sudo nano /etc/systemd/system/guitar-effects-web.service
```

### Firewall Configuration

If you can't access the web interface from other devices:

```bash
# Allow port 1051 through firewall
sudo ufw allow 1051

# Or for custom port
sudo ufw allow 9090
```

## 🔒 Security Considerations

- The web interface is accessible to anyone on your network
- No authentication is currently implemented
- Consider using a reverse proxy with SSL for production use
- Change default port if needed

## 🐛 Troubleshooting

### Can't Access Web Interface

1. **Check if service is running**:

   ```bash
   sudo systemctl status guitar-effects-web
   ```

2. **Check logs**:

   ```bash
   sudo journalctl -u guitar-effects-web -f
   ```

3. **Verify port is open**:

   ```bash
   netstat -tlnp | grep 1051
   ```

4. **Check firewall**:
   ```bash
   sudo ufw status
   ```

### Audio Issues

1. **Check audio devices**:

   ```bash
   aplay -l
   ```

2. **Test audio**:

   ```bash
   speaker-test -c 2 -t sine
   ```

3. **Check audio group**:
   ```bash
   groups $USER
   ```

### Performance Issues

1. **Monitor system resources**:

   ```bash
   htop
   ```

2. **Check CPU governor**:

   ```bash
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

3. **Monitor temperature**:
   ```bash
   vcgencmd measure_temp
   ```

## 🔮 Future Enhancements

- **WebSocket Support**: Real-time bidirectional communication
- **Preset Management**: Save and load effect configurations
- **Audio Visualization**: Real-time audio spectrum display
- **MIDI Integration**: MIDI control via web interface
- **Multi-User Support**: Multiple simultaneous users
- **Authentication**: User login and access control
- **SSL Support**: Secure HTTPS connections

## 📚 API Reference

### Endpoints

- `GET /api/status` - Get current system status
- `POST /api/parameter` - Set a parameter
- `POST /api/start` - Start audio processing
- `POST /api/stop` - Stop audio processing
- `POST /api/reset` - Reset delay buffers
- `GET /api/config` - Get configuration
- `POST /api/config` - Save configuration

### Example API Usage

```javascript
// Set left delay to 0.5 seconds
fetch("/api/parameter", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    parameter: "left_delay",
    value: 0.5,
  }),
});

// Get current status
fetch("/api/status")
  .then((response) => response.json())
  .then((status) => console.log(status));
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source. See LICENSE file for details.
