# Guitar Arpeggiator System

A real-time polyphonic chord detection and arpeggio generation system for guitar
input. This system automatically detects guitar chords and generates electronic
arpeggios in real-time. **Now with full Raspberry Pi support including GPIO
controls!**

## Features

- **Real-time Chord Detection**: Uses FFT analysis to detect polyphonic guitar
  chords
- **Multiple Arpeggio Patterns**: 11 different arpeggio patterns including
  classic, trance, dubstep, and ambient styles
- **Synthesizer Engine**: 9 different synthesizer types (saw, square, sine,
  triangle, FM, pluck, pad, lead, bass)
- **Configurable Parameters**: Adjustable tempo (60-200 BPM), pattern selection,
  synth type, and duration
- **Cross-Platform Support**: Full compatibility with macOS, Linux, and
  Raspberry Pi
- **GPIO Integration**: Physical LED indicators and button controls on Raspberry
  Pi
- **Real-time Audio Processing**: Low-latency audio input/output using
  sounddevice
- **Smart Audio Detection**: Platform-specific audio device detection and
  optimization

## System Architecture

The system consists of five main components:

1. **Config** (`config.py`): Platform detection, system configuration, and
   Pi-specific optimizations
2. **ChordDetector** (`chord_detector.py`): Real-time polyphonic chord detection
   using FFT
3. **ArpeggioEngine** (`arpeggio_engine.py`): Pattern generation and arpeggio
   sequencing
4. **SynthEngine** (`synth_engine.py`): Electronic sound synthesis with multiple
   waveforms
5. **GPIOInterface** (`gpio_interface.py`): Raspberry Pi GPIO control for LEDs
   and buttons

## Installation

### Prerequisites

- **Python 3.8+** (3.9+ recommended for Pi)
- **Audio Interface**: USB audio interface (e.g., Focusrite Scarlett 2i2) for
  best results
- **Raspberry Pi**: Pi 3B+ or Pi 4 recommended for optimal performance

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guitar-arpeggiator
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
sudo apt-get install -y python3-pip python3-dev python3-venv
sudo apt-get install -y libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install -y libffi-dev libssl-dev

# Install GPIO library
pip install RPi.GPIO

# Add user to audio group
sudo usermod -a -G audio $USER

# Reboot to apply changes
sudo reboot
```

## Platform-Specific Features

### macOS

- **Audio Backend**: Core Audio with Scarlett 2i2 auto-detection
- **Optimizations**: High-latency mode for stability
- **Device Priority**: Focusrite/Scarlett audio interfaces

### Raspberry Pi

- **Audio Backend**: ALSA with hardware acceleration
- **GPIO Controls**: LED indicators, physical buttons, volume controls
- **Optimizations**: Performance CPU governor, audio group permissions
- **Device Priority**: USB audio devices, built-in audio

### Linux (Other)

- **Audio Backend**: Default system audio
- **Optimizations**: Standard audio settings
- **Device Priority**: System default devices

## GPIO Hardware Setup (Raspberry Pi)

### Pin Layout (BCM Numbering)

```
🎵 Audio Interface LEDs:
   C Note LED: GPIO 12
   E Note LED: GPIO 13
   G Note LED: GPIO 16

🔘 Control Buttons:
   Start/Stop: GPIO 17
   Tempo Up:   GPIO 22
   Tempo Down: GPIO 23

🎚️ Audio Controls:
   Mute:       GPIO 24
   Volume Up:  GPIO 25
   Volume Down: GPIO 26
```

### Wiring Diagram

```
Raspberry Pi GPIO → Component
    12 → C Note LED (with 220Ω resistor)
    13 → E Note LED (with 220Ω resistor)
    16 → G Note LED (with 220Ω resistor)
    17 → Start/Stop Button (with 10kΩ pull-up)
    22 → Tempo Up Button (with 10kΩ pull-up)
    23 → Tempo Down Button (with 10kΩ pull-up)
    24 → Mute LED/Relay
    25 → Volume Up LED/Relay
    26 → Volume Down LED/Relay
```

### Component Requirements

- **LEDs**: 3x 5mm LEDs (any color)
- **Resistors**: 3x 220Ω resistors for LEDs
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

The system will:

1. **Auto-detect platform** and apply optimizations
2. **Initialize GPIO** (if on Pi)
3. **Detect audio devices** based on platform priorities
4. **Run demo mode** with a C major chord
5. **Start real-time processing** with guitar input

#### Headless Mode (no screen - Pi only)

Run without screen interaction, controlled entirely by GPIO buttons:

```bash
python headless_mode.py
```

**Setup for auto-start on boot:**

```bash
# Install headless mode service
./install_headless.sh

# Reboot to enable auto-start
sudo reboot
```

**How it works:**

1. **Pi boots** → System starts automatically
2. **Press START button** → Arpeggiator begins
3. **Press STOP button** → Arpeggiator stops
4. **Tempo buttons** → Adjust BPM while running
5. **LED indicators** → Show system status and chord detection

### Platform-Specific Behavior

#### macOS

- Automatically detects Scarlett 2i2 or similar audio interfaces
- Uses Core Audio with high-latency mode for stability
- Maintains all existing functionality

#### Raspberry Pi

- **LED Feedback**: Chord detection lights up corresponding note LEDs
- **Button Controls**: Physical buttons for start/stop and tempo control
- **Audio Optimization**: ALSA backend with hardware acceleration
- **GPIO Status**: Real-time LED indicators for system state

### Interactive Commands

Once running, you can use these commands:

```python
# Set tempo (60-200 BPM)
arpeggiator.set_tempo(140)

# Change arpeggio pattern
arpeggiator.set_pattern('trance_16th')

# Change synthesizer type
arpeggiator.set_synth('pad')

# Adjust duration
arpeggiator.set_duration(3.0)

# Run demo mode
arpeggiator.demo_mode()

# Test audio system
arpeggiator.test_audio_system()

# Stop the system
arpeggiator.stop()
```

### GPIO Commands (Pi Only)

```python
# Check GPIO status
arpeggiator.gpio.get_status()

# Simulate button press (for testing)
arpeggiator.gpio.simulate_button_press('start')

# Control LEDs manually
arpeggiator.gpio.set_led('C', True)  # Turn on C LED
arpeggiator.gpio.flash_led('E', 0.5)  # Flash E LED for 0.5s
```

### Headless Mode Features (Pi Only)

The headless mode provides complete hands-free operation:

#### **Button Controls:**

- **START (GPIO 17)**: Start the arpeggiator
- **STOP (GPIO 18)**: Stop the arpeggiator
- **TEMPO UP (GPIO 22)**: Increase tempo by 10 BPM
- **TEMPO DOWN (GPIO 23)**: Decrease tempo by 10 BPM

#### **LED Indicators:**

- **C LED (GPIO 12)**: Chord detection + Tempo up feedback
- **E LED (GPIO 13)**: System running status (blinking when active)
- **G LED (GPIO 16)**: Chord detection + Tempo down feedback

#### **System Behavior:**

- **Auto-start on boot**: System loads automatically when Pi powers on
- **Button-activated**: Waits for START button before beginning
- **Real-time control**: Adjust tempo while playing
- **Visual feedback**: LEDs show chord detection and system status
- **Error handling**: Visual error indicators if something goes wrong

### Available Patterns

- `up`: Classic ascending arpeggio
- `down`: Classic descending arpeggio
- `up_down`: Up then down pattern
- `down_up`: Down then up pattern
- `random`: Random note order
- `octave_up`: Multi-octave ascending
- `octave_down`: Multi-octave descending
- `trance_16th`: Trance-style 16th notes
- `dubstep_chop`: Dubstep-style chopped rhythm
- `ambient_flow`: Ambient flowing patterns
- `rock_eighth`: Rock-style eighth notes

### Available Synths

- `saw`: Bright sawtooth wave
- `square`: Classic square wave
- `sine`: Pure sine wave
- `triangle`: Warm triangle wave
- `fm`: FM synthesis
- `pluck`: Plucked string simulation
- `pad`: Rich harmonic pad
- `lead`: Bright lead sound
- `bass`: Deep bass sound

## Testing

Run the test suite to verify all components work correctly:

```bash
python test_system.py
```

This will test:

- Configuration system
- Chord detection with synthetic audio
- Arpeggio pattern generation
- Synthesizer engine
- Full system integration
- GPIO functionality (on Pi)

## Audio Setup

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
- **Audio Routing**: Audio pass-through enabled for monitoring
- **Latency**: Platform-optimized buffer sizes for stability vs. performance

## Configuration

Edit `config.py` to customize platform-specific and general settings:

### General Settings

- **Sample Rate**: 48000 Hz (configurable)
- **Chord Detection**: Confidence threshold (default: 0.6)
- **Chord Hold Time**: 0.5 seconds (configurable)
- **Default Tempo**: 120 BPM (60-200 range)
- **Default Pattern**: 'up' arpeggio pattern
- **Default Synth**: 'saw' synthesizer type

### Platform-Specific Settings

#### Raspberry Pi

- **GPIO Pins**: LED and button pin assignments
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
# LED pins for chord detection
self.led_pins = {'C': 12, 'E': 13, 'G': 16}

# Button pins for control
self.button_pins = {'start': 17, 'stop': 18, 'tempo_up': 22, 'tempo_down': 23}

# Audio interface pins
self.audio_interface_pins = {'mute': 24, 'volume_up': 25, 'volume_down': 26}
```

## Technical Details

### Chord Detection

- Uses FFT with Hann windowing for spectral analysis
- Peak detection with configurable thresholds
- Musical note matching with cents accuracy
- Chord pattern recognition for 11 common chord types

### Audio Processing

- Real-time streaming with configurable buffer sizes
- Automatic audio normalization to prevent clipping
- ADSR envelope generation for natural sound shaping
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
- **Non-Blocking**: LED control doesn't interfere with audio processing
- **Hardware Abstraction**: Clean interface that works across platforms
- **Error Handling**: Graceful fallback when GPIO operations fail

## Troubleshooting

### Common Issues

#### General

1. **Import errors**: Ensure all dependencies are installed
2. **Audio device not found**: Check system audio settings
3. **High latency**: Reduce chunk size in config (may affect stability)
4. **Poor chord detection**: Adjust confidence threshold and ensure clean input
   signal

#### macOS Specific

1. **Core Audio errors**: Common on macOS, usually harmless
2. **Scarlett not detected**: Check USB connection and system audio settings
3. **Permission issues**: Grant microphone access in System Preferences

#### Raspberry Pi Specific

1. **GPIO import error**: Install RPi.GPIO with `pip install RPi.GPIO`
2. **Audio permission denied**: Add user to audio group and reboot
3. **High CPU usage**: Check if performance governor is active
4. **USB audio not working**: Ensure USB audio device is properly connected
5. **GPIO pins not responding**: Check wiring and pin assignments

#### Linux Specific

1. **ALSA errors**: Install ALSA development libraries
2. **PortAudio issues**: Install portaudio development packages
3. **Audio group permissions**: Ensure user is in audio group

### Debug Mode

Enable debug output by modifying the confidence threshold in `config.py`:

```python
self.min_chord_confidence = 0.3  # Lower threshold for more detections
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

### Adding New Patterns

To add a new arpeggio pattern:

1. Add the pattern function to `ArpeggioEngine`
2. Register it in the `patterns` dictionary
3. Follow the existing pattern function signature

### Adding New Synths

To add a new synthesizer type:

1. Add the synthesis function to `SynthEngine`
2. Register it in the `synth_types` dictionary
3. Follow the existing synthesis function signature

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
- Inspired by classic arpeggiators and modern music production tools
- Designed for real-time performance and creative expression
