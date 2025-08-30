# Guitar Delay Effects Package

This package contains the stereo delay effect implementation for the guitar
effects project.

## Overview

The delay effects package provides a high-quality stereo delay effect with
advanced features for guitar processing. The stereo delay creates rich, spatial
delay effects with independent left and right channel control.

## Stereo Delay Effect

### Features

- **Independent left/right delay times**: Set different delay times for each
  channel
- **Ping-pong delay patterns**: Creates bouncing delay effects between channels
- **Stereo width enhancement**: Expands the stereo image using mid-side
  processing
- **Cross-feedback**: Allows delays to feed back between left and right channels
- **Real-time parameter adjustment**: Change parameters during playback
- **High-quality audio processing**: Professional-grade delay algorithms

### Usage

```python
from delay import StereoDelay

# Create a stereo delay effect
stereo_delay = StereoDelay(
    sample_rate=44100,
    left_delay=0.3,      # Left channel delay time (seconds)
    right_delay=0.6,     # Right channel delay time (seconds)
    feedback=0.3,        # Feedback amount (0.0-0.9)
    wet_mix=0.6,         # Wet signal mix (0.0-1.0)
    ping_pong=True,      # Enable ping-pong delay pattern
    stereo_width=0.5,    # Stereo width enhancement (0.0-1.0)
    cross_feedback=0.2   # Cross-feedback between channels (0.0-0.5)
)

# Process mono input to stereo output
left_output, right_output = stereo_delay.process_mono_to_stereo(input_signal)

# Process stereo input to stereo output
left_output, right_output = stereo_delay.process_buffer(left_input, right_input)
```

### Parameters

- **left_delay**: Left channel delay time in seconds (0.001-4.0)
- **right_delay**: Right channel delay time in seconds (0.001-4.0)
- **feedback**: Feedback amount for delay repeats (0.0-0.9)
- **wet_mix**: Balance between dry and wet signals (0.0-1.0)
- **ping_pong**: Enable ping-pong delay pattern (True/False)
- **stereo_width**: Stereo width enhancement amount (0.0-1.0)
- **cross_feedback**: Cross-feedback between channels (0.0-0.5)

### Real-time Control

```python
# Adjust delay times
stereo_delay.set_left_delay(0.4)
stereo_delay.set_right_delay(0.8)

# Adjust basic parameters
stereo_delay.set_parameters(feedback=0.5, wet_mix=0.7)

# Adjust stereo parameters
stereo_delay.set_stereo_parameters(
    ping_pong=False,
    stereo_width=0.8,
    cross_feedback=0.3
)
```

## Installation

The delay effects package is part of the guitar effects system. Install the main
requirements:

```bash
pip install -r requirements.txt
```

## Testing

Run the stereo delay tests:

```bash
python3 test_delay_effects.py
python3 test_stereo_system.py
```

## Architecture

The stereo delay effect is built on a modular architecture:

- **BaseDelay**: Base class providing common delay functionality
- **StereoDelay**: Main stereo delay implementation with advanced features

## Performance

The stereo delay effect is optimized for real-time processing with:

- Low latency processing
- Efficient buffer management
- Minimal CPU usage
- Stable audio performance

## License

This project is licensed under the MIT License.
