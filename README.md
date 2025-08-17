# Guitar Arpeggiator System

A real-time polyphonic chord detection and arpeggio generation system for guitar
input. This system automatically detects guitar chords and generates electronic
arpeggios in real-time.

## Features

- **Real-time Chord Detection**: Uses FFT analysis to detect polyphonic guitar
  chords
- **Multiple Arpeggio Patterns**: 11 different arpeggio patterns including
  classic, trance, dubstep, and ambient styles
- **Synthesizer Engine**: 9 different synthesizer types (saw, square, sine,
  triangle, FM, pluck, pad, lead, bass)
- **Configurable Parameters**: Adjustable tempo (60-200 BPM), pattern selection,
  synth type, and duration
- **Platform Detection**: Automatically detects macOS, Linux, and Raspberry Pi
  for optimal configuration
- **Real-time Audio Processing**: Low-latency audio input/output using
  sounddevice

## System Architecture

The system consists of four main components:

1. **Config** (`config.py`): Platform detection and system configuration
2. **ChordDetector** (`chord_detector.py`): Real-time polyphonic chord detection
   using FFT
3. **ArpeggioEngine** (`arpeggio_engine.py`): Pattern generation and arpeggio
   sequencing
4. **SynthEngine** (`synth_engine.py`): Electronic sound synthesis with multiple
   waveforms

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd guitar-arpeggiator
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main system:

```bash
python main.py
```

The system will:

1. Initialize all components
2. Run a demo with a C major chord
3. Start real-time audio processing
4. Listen for guitar input and generate arpeggios

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

# Stop the system
arpeggiator.stop()
```

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

## Audio Setup

### Input Device

The system automatically detects audio input devices. For best results:

- Use a high-quality audio interface (e.g., Focusrite Scarlett)
- Ensure clean guitar signal with minimal noise
- Set appropriate input gain levels

### Output Device

Audio output uses the system default output device. Adjust system volume as
needed.

## Configuration

Edit `config.py` to customize:

- Sample rate (default: 48000 Hz)
- Audio chunk size (default: 4096 samples)
- Chord detection confidence threshold (default: 0.6)
- Chord hold time (default: 0.5 seconds)
- Default tempo, pattern, and synth type

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

- Optimized for real-time performance
- Configurable audio buffer sizes for latency vs. stability trade-offs
- Efficient numpy-based signal processing

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Audio device not found**: Check system audio settings
3. **High latency**: Reduce chunk size in config (may affect stability)
4. **Poor chord detection**: Adjust confidence threshold and ensure clean input
   signal

### Debug Mode

Enable debug output by modifying the confidence threshold in `config.py`:

```python
self.min_chord_confidence = 0.3  # Lower threshold for more detections
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
