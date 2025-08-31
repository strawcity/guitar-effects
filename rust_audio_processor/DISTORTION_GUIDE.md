# 🎸 Distortion Controls Guide

This guide explains how to use the distortion controls in your Rust guitar
effects system.

## How Distortion Works

The distortion in this system is **cross-feedback distortion** - it applies
distortion to the feedback signals between the left and right delay channels.
This creates interesting harmonic interactions and can make the delay more
musical and less sterile.

### Distortion Types

The system supports 6 different distortion types:

1. **Soft Clip** (`soft_clip`) - Musical soft clipping using hyperbolic tangent

   - Creates warm, musical distortion
   - Good for adding harmonics without harshness
   - Great for blues and jazz tones

2. **Hard Clip** (`hard_clip`) - Traditional hard clipping with threshold
   control

   - Creates sharp, aggressive distortion
   - Good for rock and metal tones
   - More aggressive than soft clip

3. **Tube** (`tube`) - Asymmetric tube-style distortion simulation

   - Simulates vintage tube amplifier characteristics
   - Creates warm, musical harmonics
   - Great for classic rock tones

4. **Fuzz** (`fuzz`) - Aggressive fuzz with hard and soft clipping

   - Creates thick, saturated distortion
   - Good for psychedelic and experimental sounds
   - Very aggressive and characterful

5. **Bit Crush** (`bit_crush`) - Digital bit depth and sample rate reduction

   - Creates lo-fi, digital distortion
   - Good for electronic and experimental sounds
   - Adds digital artifacts and quantization noise

6. **Waveshaper** (`waveshaper`) - Cubic polynomial waveshaping
   - Creates complex harmonic distortion
   - Good for experimental and unique sounds
   - More mathematical approach to distortion

## Interactive CLI Controls

### Starting the Interactive Mode

```bash
cd rust_audio_processor
cargo run --release
```

### Basic Distortion Commands

#### Set Distortion Type

```
distortion_type=soft_clip
distortion_type=hard_clip
distortion_type=tube
distortion_type=fuzz
distortion_type=bit_crush
distortion_type=waveshaper
```

#### Enable/Disable Distortion

```
distortion_enabled=1    # Enable distortion
distortion_enabled=0    # Disable distortion
```

#### Control Distortion Parameters

```
distortion_drive=0.5              # Drive amount (0.0-1.0)
distortion_mix=0.7                # Wet/dry mix (0.0-1.0)
distortion_feedback_intensity=0.3 # How much distortion affects feedback (0.0-1.0)
```

### Complete Example Session

Here's a complete example of how to set up and control distortion:

```bash
# Start the interactive mode
cargo run --release

# In the interactive prompt:
> start                    # Start audio processing
> distortion_enabled=1    # Enable distortion
> distortion_type=tube     # Set to tube distortion
> distortion_drive=0.6     # Set drive to 60%
> distortion_mix=0.8       # Set mix to 80% wet
> distortion_feedback_intensity=0.4  # Set feedback intensity to 40%

# Now adjust delay parameters
> left_delay=0.3          # 300ms left delay
> right_delay=0.6         # 600ms right delay
> feedback=0.4            # 40% feedback
> wet_mix=0.7             # 70% wet mix
> stereo_width=0.6         # 60% stereo width
> cross_feedback=0.2       # 20% cross feedback

# Try different distortion types
> distortion_type=fuzz     # Switch to fuzz
> distortion_drive=0.8     # Increase drive
> distortion_type=soft_clip  # Switch to soft clip
> distortion_drive=0.3     # Reduce drive for softer sound
```

## Parameter Ranges and Effects

### Distortion Drive (0.0 - 1.0)

- **0.0**: No drive, clean signal
- **0.3**: Light drive, subtle harmonics
- **0.5**: Medium drive, noticeable distortion
- **0.7**: Heavy drive, strong distortion
- **1.0**: Maximum drive, very aggressive

### Distortion Mix (0.0 - 1.0)

- **0.0**: 100% dry signal (no distortion)
- **0.3**: Mostly dry with some distortion
- **0.5**: Equal mix of dry and distorted
- **0.7**: Mostly distorted with some dry
- **1.0**: 100% distorted signal

### Distortion Feedback Intensity (0.0 - 1.0)

- **0.0**: Distortion only affects direct signal
- **0.3**: Light distortion on feedback
- **0.5**: Equal distortion on direct and feedback
- **0.7**: Heavy distortion on feedback
- **1.0**: Maximum distortion on feedback

## Recommended Settings by Genre

### Blues

```
distortion_type=tube
distortion_drive=0.4
distortion_mix=0.6
distortion_feedback_intensity=0.3
```

### Rock

```
distortion_type=hard_clip
distortion_drive=0.6
distortion_mix=0.7
distortion_feedback_intensity=0.4
```

### Metal

```
distortion_type=fuzz
distortion_drive=0.8
distortion_mix=0.8
distortion_feedback_intensity=0.5
```

### Experimental

```
distortion_type=bit_crush
distortion_drive=0.5
distortion_mix=0.9
distortion_feedback_intensity=0.7
```

## Tips for Best Results

1. **Start with low drive** and increase gradually
2. **Use distortion mix** to blend clean and distorted signals
3. **Experiment with feedback intensity** for different textures
4. **Try different distortion types** for different characters
5. **Combine with delay settings** for complex sounds
6. **Use stereo width** to enhance the stereo effect
7. **Adjust cross feedback** for different stereo interactions

## Troubleshooting

### Distortion sounds too harsh

- Reduce `distortion_drive`
- Try `distortion_type=soft_clip` or `distortion_type=tube`
- Lower `distortion_mix`

### Distortion sounds too weak

- Increase `distortion_drive`
- Try `distortion_type=fuzz` or `distortion_type=hard_clip`
- Raise `distortion_mix`

### Feedback is too distorted

- Lower `distortion_feedback_intensity`
- Reduce `distortion_drive`

### No distortion effect

- Check that `distortion_enabled=1`
- Increase `distortion_drive`
- Raise `distortion_mix`

## Advanced Techniques

### Layering Distortion Types

You can create complex sounds by adjusting parameters while the audio is
running:

```bash
# Start with tube distortion
> distortion_type=tube
> distortion_drive=0.4

# Then switch to fuzz for a solo
> distortion_type=fuzz
> distortion_drive=0.8

# Return to tube for rhythm
> distortion_type=tube
> distortion_drive=0.4
```

### Creating Feedback Loops

Use high feedback and distortion feedback intensity for self-oscillating
effects:

```bash
> feedback=0.8
> distortion_feedback_intensity=0.9
> distortion_drive=0.7
```

### Stereo Width Experiments

Combine distortion with stereo width for wide, immersive sounds:

```bash
> stereo_width=0.9
> cross_feedback=0.4
> distortion_type=waveshaper
> distortion_drive=0.5
```

## Status Commands

Use these commands to check your current settings:

```bash
> status    # Show current system status
> help      # Show available commands
```

The status will show you the current values of all parameters including
distortion settings.

## Example Configurations

### Classic Delay with Tube Distortion

```
left_delay=0.3
right_delay=0.6
feedback=0.3
wet_mix=0.6
stereo_width=0.5
cross_feedback=0.2
distortion_enabled=1
distortion_type=tube
distortion_drive=0.4
distortion_mix=0.6
distortion_feedback_intensity=0.3
```

### Aggressive Fuzz Delay

```
left_delay=0.2
right_delay=0.4
feedback=0.6
wet_mix=0.8
stereo_width=0.7
cross_feedback=0.3
distortion_enabled=1
distortion_type=fuzz
distortion_drive=0.8
distortion_mix=0.8
distortion_feedback_intensity=0.6
```

### Experimental Bit Crush Delay

```
left_delay=0.5
right_delay=1.0
feedback=0.7
wet_mix=0.9
stereo_width=0.8
cross_feedback=0.4
distortion_enabled=1
distortion_type=bit_crush
distortion_drive=0.6
distortion_mix=0.9
distortion_feedback_intensity=0.7
```

Happy experimenting! 🎸
