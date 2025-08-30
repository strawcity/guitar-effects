# 🎸 Guitar Delay Effects System

A comprehensive real-time guitar delay effects processing system featuring
professional-quality delay algorithms. This system provides multiple delay
effect types with real-time parameter control and ultra-low latency processing.
**Now with full Raspberry Pi support including GPIO button controls and an
extensive delay effects package!**

## Features

### 🎛️ **Professional Delay Effects Package**

- **Basic Delay**: Clean echo effects with stereo separation and configurable
  delay time and feedback
- **Tape Delay**: Vintage tape-style delay with saturation, modulation, and
  stereo phase effects
- **Multi-Tap Delay**: Complex delay patterns with multiple delay lines and
  stereo panning
- **Tempo-Synced Delay**: Musical timing synchronization with tempo-based stereo
  modulation
- **Stereo Delay**: Ping-pong and stereo width enhancement effects with
  independent left/right delays

### ⚙️ **System Features**

- **Configurable Parameters**: Adjustable delay time (0.1-2.0s), feedback
  (0.0-0.9), and wet mix (0.0-1.0)
- **Stereo Processing**: All effects output in stereo with spatial separation
  and width control
- **Cross-Platform Support**: Full compatibility with macOS, Linux, and
  Raspberry Pi
- **GPIO Integration**: Physical button controls on Raspberry Pi
- **Real-time Audio Processing**: Ultra-low-latency audio processing using
  optimized audio processor
- **Smart Audio Detection**: Platform-specific audio device detection and
  optimization
- **Interactive CLI**: Menu-driven interface for easy effect control and
  parameter adjustment

## System Architecture

The system consists of several main components organized into specialized
packages:

### 🎯 **Core Components**

1. **Config** (`config.py`): Platform detection, system configuration, and
   Pi-specific optimizations
2. **GPIOInterface** (`gpio_interface.py`): Raspberry Pi GPIO control for
   buttons
3. **Main System** (`main.py`): Primary delay effects processing system

### 🎛️ **Delay Effects Package** (`delay/`)

4. **BaseDelay** (`delay/base_delay.py`): Abstract base class for delay effects
5. **StereoDelay** (`delay/stereo_delay.py`): Advanced stereo delay with
   ping-pong, width enhancement, and cross-feedback

## Installation

### Prerequisites

- **Python 3.8+** (3.9+ recommended for Pi)
- **Audio Interface**: USB audio interface (e.g., Focusrite Scarlett 2i2) for
  best results
- **Raspberry Pi**: Pi 3B+ or Pi 4 recommended for optimal performance

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guitar-effects
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Raspberry Pi Specific Setup

If running on Raspberry Pi, additional setup is required:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-venv python3-full
sudo apt-get install -y libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install -y libffi-dev libssl-dev

# Create and activate virtual environment (required for newer Pi OS versions)
python3 -m venv ~/guitar-effects-env
source ~/guitar-effects-env/bin/activate

# Install GPIO library in virtual environment
pip install RPi.GPIO

# Install project dependencies
pip install -r requirements.txt

# Add user to audio group
sudo usermod -a -G audio $USER

# Fix USB audio issues (IMPORTANT for Scarlett 2i2)
sudo nano /boot/firmware/cmdline.txt
# Add "dwc_otg.fiq_fsm_enable=0" to the end of the line

# Reboot to apply all changes
sudo reboot
```

**Important Note for Raspberry Pi OS Bookworm+**: Newer Pi OS versions use an
"externally managed environment" that prevents global Python package
installation. You **must** use a virtual environment. If you get an
"externally-managed-environment" error, follow the virtual environment setup
above.

## Delay Effects Package

The guitar effects system includes a professional-quality stereo delay effect
with advanced features:

### 🎯 **Stereo Delay Effect**

```python
from delay import StereoDelay

# Advanced stereo delay with ping-pong and width enhancement
stereo_delay = StereoDelay(
    left_delay=0.3,      # Left channel delay time
    right_delay=0.6,     # Right channel delay time
    feedback=0.3,        # Feedback amount
    wet_mix=0.6,         # Wet signal mix
    ping_pong=True,      # Enable ping-pong pattern
    stereo_width=0.5,    # Stereo width enhancement
    cross_feedback=0.2   # Cross-feedback between channels
)

# Process mono input to stereo output
left_output, right_output = stereo_delay.process_mono_to_stereo(input_signal)

# Process stereo input to stereo output
left_output, right_output = stereo_delay.process_buffer(left_input, right_input)
```

### 🚀 **Quick Start with Stereo Delay**

```bash
# Test stereo delay effects
python test_delay_effects.py

# Test stereo system
python test_stereo_system.py

# Start the main system
python main.py

# Use interactive CLI
python interactive_cli.py
```

### 📚 **Documentation**

- **Package Overview**: `delay/README.md`
- **Stereo Delay**: Comprehensive docstrings and examples
- **Real-time Control**: Parameter adjustment during playback

## Platform-Specific Features

### macOS

- **Audio Backend**: Core Audio with Scarlett 2i2 auto-detection
- **Optimizations**: High-latency mode for stability
- **Device Priority**: Focusrite/Scarlett audio interfaces

### Raspberry Pi

- **Audio Backend**: ALSA with hardware acceleration
- **GPIO Controls**: Physical buttons for delay parameter control
- **Optimizations**: Performance CPU governor, audio group permissions
- **Device Priority**: USB audio devices, built-in audio

### Linux (Other)

- **Audio Backend**: Default system audio
- **Optimizations**: Standard audio settings
- **Device Priority**: System default devices

## GPIO Hardware Setup (Raspberry Pi)

### Pin Layout (BCM Numbering)

```
🔘 Control Buttons:
   Start/Stop: GPIO 17
   Delay Time Up:   GPIO 22
   Delay Time Down: GPIO 23
```

### Wiring Diagram

```
Raspberry Pi GPIO → Component
    17 → Start/Stop Button (with 10kΩ pull-up)
    22 → Delay Time Up Button (with 10kΩ pull-up)
    23 → Delay Time Down Button (with 10kΩ pull-up)
```

### Component Requirements

- **Buttons**: 3x momentary push buttons
- **Pull-up Resistors**: 3x 10kΩ resistors for buttons
- **Breadboard**: For prototyping
- **Jumper Wires**: Male-to-female for Pi connection

## Usage

### Basic Usage

#### Interactive Mode (with screen)

Run the main system:

```bash
python main.py
```

Or use the interactive CLI (keyboard control on a connected monitor):

```bash
python interactive_cli.py
```

Interactive CLI commands:

```
start | stop | status
delay <type>   (basic, tape, multi, tempo, stereo)
time <seconds> | feedback <0-0.9> | wet <0-1.0>
effects | demo
quit
```

The system will:

1. **Auto-detect platform** and apply optimizations
2. **Initialize GPIO** (if on Pi)
3. **Detect audio devices** based on platform priorities
4. **Run demo mode** with different delay effects
5. **Start real-time processing** with guitar input

### Platform-Specific Behavior

#### macOS

- Automatically detects Scarlett 2i2 or similar audio interfaces
- Uses Core Audio with high-latency mode for stability
- Maintains all existing functionality

#### Raspberry Pi

- **Button Controls**: Physical buttons for start/stop and delay time control
- **Audio Optimization**: ALSA backend with hardware acceleration
- **GPIO Status**: Real-time button callback handling

### Interactive Commands

Once running, you can use these commands:

```python
# Set delay time
system.set_delay_time(0.8)

# Change delay effect type
system.set_delay_effect('tape')

# Adjust feedback
system.set_feedback(0.5)

# Adjust wet mix
system.set_wet_mix(0.7)

# Run demo mode
system.demo_mode()

# Stop the system
system.stop()
```

### GPIO Commands (Pi Only)

```python
# Check GPIO status
system.gpio.get_status()

# Simulate button press (for testing)
system.gpio.simulate_button_press('start')
```

### Available Delay Effects

- `basic`: Clean echo effect with configurable parameters
- `tape`: Vintage tape-style delay with analog characteristics
- `multi`: Multi-tap delay with complex patterns
- `tempo`: Tempo-synced delay for musical timing
- `stereo`: Stereo ping-pong and width enhancement

## Testing

Run the test suite to verify all components work correctly:

```bash
# Test main system components
python test_system.py

# Test delay effects package
python test_delay_effects.py

# Run delay effects demo
python -m delay.demo
```

### 🧪 **Test Coverage**

**Main System Tests** (`test_system.py`):

- Configuration and platform detection
- GPIO interface (on Pi)
- Audio device detection

**Delay Effects Tests** (`test_delay_effects.py`):

- All delay effect imports and instantiation
- Basic audio processing functionality
- Parameter validation and clipping
- Buffer management and memory efficiency

**Delay Effects Demo** (`delay/demo.py`):

- Comprehensive demonstration of all delay types
- Parameter adjustment examples
- Audio processing demonstrations
- Integration examples

## Audio Setup

### Scarlett 2i2 Monitor Output Setup

**For Raspberry Pi users without a headphone jack**, the system is configured to
output audio through the Scarlett 2i2's monitor outputs:

1. **Connect your headphones** to the Scarlett 2i2's monitor jack
2. **Set the Scarlett 2i2 Direct Monitor** to OFF (no pass-through needed)
3. **The delay effects output** will be sent to the monitor outputs
4. **You'll hear** the processed delay effects when you play guitar

**Audio Flow:**

```
Guitar → Scarlett 2i2 Input → Raspberry Pi → Delay Processing → Scarlett 2i2 Output → Monitor/Headphones
```

### Platform-Specific Audio Configuration

The system automatically detects and configures audio devices based on your
platform:

#### macOS

- **Input Priority**: Focusrite Scarlett 2i2, audio interfaces
- **Output Priority**: Built-in speakers, headphones
- **Backend**: Core Audio with high-latency mode
- **Buffer Size**: 1024 samples for stability

#### Raspberry Pi

- **Input Priority**: USB audio devices, USB Audio Device
- **Output Priority**: Built-in audio (bcm2835 ALSA), USB audio
- **Backend**: ALSA with hardware acceleration
- **Buffer Size**: 512 samples for performance
- **Optimizations**: Performance CPU governor, audio group permissions

#### Linux (Other)

- **Input Priority**: System default devices
- **Output Priority**: System default devices
- **Backend**: Default system audio
- **Buffer Size**: 1024 samples

### Input Device Setup

For best results:

- **USB Audio Interface**: Use a high-quality interface (e.g., Focusrite
  Scarlett 2i2)
- **Signal Quality**: Ensure clean guitar signal with minimal noise
- **Gain Levels**: Set appropriate input gain levels (avoid clipping)
- **Connection**: Connect via USB for Pi, USB/Thunderbolt for Mac

### Output Device Setup

- **System Volume**: Adjust system volume as needed
- **Audio Routing**: Clean delay output only (no pass-through)
- **Latency**: Platform-optimized buffer sizes for stability vs. performance

## Configuration

Edit `config.py` to customize platform-specific and general settings:

### General Settings

- **Sample Rate**: 48000 Hz (configurable)
- **Default Delay Time**: 0.5 seconds (0.1-2.0 range)
- **Default Feedback**: 0.3 (0.0-0.9 range)
- **Default Wet Mix**: 0.6 (0.0-1.0 range)

### Platform-Specific Settings

#### Raspberry Pi

- **GPIO Pins**: Button pin assignments
- **Audio Backend**: ALSA configuration
- **Performance**: CPU governor and buffer optimizations
- **Audio Group**: User permissions for audio access

#### macOS

- **Audio Backend**: Core Audio settings
- **Latency Mode**: High-latency for stability
- **Device Priority**: Scarlett 2i2 detection

#### Linux

- **Audio Backend**: Default system audio
- **Device Priority**: System default devices

### GPIO Configuration (Pi Only)

```python
# Button pins for control
self.button_pins = {'start': 17, 'stop': 18, 'delay_up': 22, 'delay_down': 23}
```

## Technical Details

### Audio Processing

- Real-time streaming with configurable buffer sizes
- Automatic audio normalization to prevent clipping
- Multi-threaded audio processing for low latency

### Performance

- **Cross-Platform Optimization**: Platform-specific audio backends and buffer
  sizes
- **Real-time Processing**: Optimized for low-latency performance
- **Configurable Buffers**: Platform-specific buffer sizes for stability vs.
  performance trade-offs
- **Efficient Processing**: NumPy-based signal processing with hardware
  acceleration on Pi
- **GPIO Performance**: Non-blocking GPIO operations with callback-based event
  handling

### GPIO System (Pi Only)

- **Event-Driven**: Button presses trigger immediate callbacks
- **Hardware Abstraction**: Clean interface that works across platforms
- **Error Handling**: Graceful fallback when GPIO operations fail

## Troubleshooting

### Common Issues

#### General

1. **Import errors**: Ensure all dependencies are installed
2. **Audio device not found**: Check system audio settings
3. **High latency**: Reduce chunk size in config (may affect stability)
4. **Poor audio quality**: Check input gain levels and signal quality

#### macOS Specific

1. **Core Audio errors**: Common on macOS, usually harmless
2. **Scarlett not detected**: Check USB connection and system audio settings
3. **Permission issues**: Grant microphone access in System Preferences

#### Raspberry Pi Specific

1. **"externally-managed-environment" error**: This is common on Pi OS
   Bookworm+. You must use a virtual environment:
   ```bash
   python3 -m venv ~/guitar-effects-env
   source ~/guitar-effects-env/bin/activate
   pip install -r requirements.txt
   ```
2. **GPIO import error**: Install RPi.GPIO in your virtual environment with
   `pip install RPi.GPIO`
3. **Audio permission denied**: Add user to audio group and reboot
4. **High CPU usage**: Check if performance governor is active
5. **USB audio not working**: Ensure USB audio device is properly connected
6. **GPIO pins not responding**: Check wiring and pin assignments
7. **ModuleNotFoundError**: Always activate your virtual environment before
   running the project:
   ```bash
   source ~/guitar-effects-env/bin/activate
   python main.py
   ```
8. **AttributeError: 'cdata' has no field 'time'**: This is a known issue with
   sounddevice on Raspberry Pi. The project has been fixed to use `time_module`
   instead of `time` to avoid conflicts with CFFI callbacks.
9. **Segmentation fault**: This can be caused by audio threading conflicts. The
   project has been updated to use a single audio stream with mixed output to
   prevent crashes. If you still experience crashes, try increasing the buffer
   size in the audio_loop method.
10. **Scarlett 2i2 not detected**: This is a common USB audio issue on Raspberry
    Pi. Add `dwc_otg.fiq_fsm_enable=0` to `/boot/firmware/cmdline.txt` and
    reboot. This disables a USB controller feature that interferes with USB
    audio devices.

#### Linux Specific

1. **ALSA errors**: Install ALSA development libraries
2. **PortAudio issues**: Install portaudio development packages
3. **Audio group permissions**: Ensure user is in audio group

### Debug Mode

Enable debug output by modifying the delay parameters in `config.py`:

```python
self.default_delay_time = 0.3  # Shorter delay for testing
self.default_feedback = 0.2    # Lower feedback for testing
```

### Platform-Specific Debugging

#### Raspberry Pi

```bash
# Check GPIO status
python -c "from gpio_interface import GPIOInterface; from config import Config; gpio = GPIOInterface(Config()); print(gpio.get_status())"

# Test audio system
python -c "import sounddevice as sd; print(sd.query_devices())"

# Check audio group membership
groups $USER
```

#### macOS

```bash
# Check audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test Core Audio
python -c "import sounddevice as sd; sd.default.device = 'default'; print('Audio system working')"
```

## Development

### Adding New Delay Effects

To add a new delay effect:

1. Create a new class inheriting from `BaseDelay`
2. Implement the required methods (`process_buffer`, `set_parameters`)
3. Add the effect to the main system's effect selection
4. Update the interactive CLI to support the new effect

### Adding GPIO Components (Pi Only)

To add new GPIO functionality:

1. **Add pins to config**: Update pin assignments in `config.py`
2. **Extend GPIOInterface**: Add new methods to `gpio_interface.py`
3. **Register callbacks**: Connect GPIO events to system functions
4. **Handle errors**: Ensure graceful fallback for GPIO failures

Example GPIO extension:

```python
# In config.py
self.new_component_pins = {'sensor': 27, 'actuator': 28}

# In gpio_interface.py
def read_sensor(self):
    if self.gpio_available:
        import RPi.GPIO as GPIO
        return GPIO.input(self.config.new_component_pins['sensor'])
    return False

# In main.py
self.gpio.register_button_callback('sensor', self.handle_sensor_event)
```

## Future Development

The guitar delay effects system is designed for continuous expansion and
enhancement:

### 🚀 **Planned Effects Packages**

- **Reverb Effects**: Room, hall, plate, and spring reverb algorithms
- **Distortion & Overdrive**: Tube, fuzz, and modern distortion models
- **Modulation Effects**: Chorus, flanger, phaser, and tremolo
- **Filtering & EQ**: Dynamic filters, parametric EQ, and envelope followers
- **Compression & Dynamics**: Multi-band compression and limiting

### 🎛️ **System Enhancements**

- **Effect Chains**: Configurable effect routing and signal flow
- **MIDI Integration**: External MIDI control and synchronization
- **Preset Management**: Save and recall effect configurations
- **Real-time Visualization**: Audio spectrum and effect parameter displays
- **Multi-channel Processing**: Support for stereo and surround sound

### 🔧 **Integration Features**

- **Plugin Architecture**: Modular effect loading system
- **Audio Interface Support**: Extended device compatibility
- **Network Control**: Remote control via web interface or mobile app
- **Recording Integration**: Direct-to-DAW recording capabilities

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Acknowledgments

- Built with NumPy, SciPy, and sounddevice
- Inspired by classic delay effects and modern music production tools
- Designed for real-time performance and creative expression
