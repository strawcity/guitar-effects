# Delay Effects Package

This package contains comprehensive delay effect implementations for the guitar
effects project.

## Implemented Effects

### 🎯 **Basic Delay** (`basic_delay.py`)

- Simple echo effect with configurable delay time and feedback
- Clean, digital sound with wet/dry mix control
- Configurable delay time (1ms to 2 seconds)
- Adjustable feedback (0% to 90%)

### 🎛️ **Tape Delay** (`tape_delay.py`)

- Vintage tape-style delay with analog characteristics
- Tape saturation and compression
- Wow and flutter modulation
- High-frequency rolloff and tape noise simulation
- Variable tape speed control

### 🔄 **Multi-Tap Delay** (`multi_tap_delay.py`)

- Complex delay patterns with multiple delay lines
- Individual control over each tap's delay time, level, and panning
- Stereo output with rhythmic delay patterns
- Tempo synchronization capabilities
- Dynamic tap management

### 🎵 **Tempo-Synced Delay** (`tempo_synced_delay.py`)

- Automatic tempo synchronization with musical timing
- Multiple note division options (1/4, 1/8, 1/16, triplets, dotted notes)
- Swing and humanization controls
- Tempo tap detection
- External clock synchronization

### 🎧 **Stereo Delay** (`stereo_delay.py`)

- Ping-pong and stereo delay effects
- Independent left/right channel control
- Stereo width enhancement using mid-side processing
- Cross-feedback between channels
- Mono to stereo conversion

## Core Infrastructure

### **Base Delay** (`base_delay.py`)

- Abstract base class for all delay effects
- Core delay line functionality
- Modulation and feedback control
- Memory-efficient buffer management

## Usage Examples

```python
from delay import BasicDelay, TapeDelay, MultiTapDelay, TempoSyncedDelay, StereoDelay

# Basic delay
basic = BasicDelay(delay_time=0.5, feedback=0.3, wet_mix=0.6)
output = basic.process_buffer(input_audio)

# Tape delay with vintage character
tape = TapeDelay(delay_time=0.6, saturation=0.4, wow_rate=0.5)
output = tape.process_buffer(input_audio)

# Multi-tap with tempo sync
multi = MultiTapDelay()
multi.sync_taps_to_tempo(120.0, ['1/4', '1/2', '3/4'])
left, right = multi.process_buffer(input_audio)

# Tempo-synced delay
tempo = TempoSyncedDelay(bpm=120.0, note_division='1/4', swing=0.2)
output = tempo.process_buffer(input_audio)

# Stereo ping-pong delay
stereo = StereoDelay(left_delay=0.3, right_delay=0.6, ping_pong=True)
left, right = stereo.process_mono_to_stereo(input_audio)
```

## Demo Script

Run `python -m delay.demo` to see all effects in action with parameter
demonstrations.

## Integration

All delay effects are designed to integrate seamlessly with the existing guitar
effects system:

- Consistent parameter interfaces
- Real-time parameter adjustment
- Memory-efficient implementations
- Support for both mono and stereo processing
- Configurable buffer sizes for different delay ranges

## Performance Features

- **Memory Management**: Efficient circular buffer implementation
- **Real-time Processing**: Sample-by-sample and buffer processing modes
- **Parameter Validation**: Automatic clipping and validation of all parameters
- **Modulation Support**: Built-in LFO modulation for dynamic effects
- **Stereo Processing**: Native stereo support with width enhancement
