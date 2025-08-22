# Guitar Synth Effect

A powerful synthesizer effect that transforms your guitar input into
synthesizer-like sounds using various synthesis techniques.

## Features

- **Ring Modulation**: Creates metallic, robotic sounds by modulating the input
  with a sine wave oscillator
- **Bit Crushing**: Reduces bit depth for lo-fi digital effects (1-16 bits)
- **Sample Rate Reduction**: Creates retro digital artifacts by reducing sample
  rate
- **Wave Shaping**: Applies harmonic distortion and saturation
- **Low-Pass Filter**: Warm, analog-style filtering with resonance control
- **Envelope Following**: Dynamic response based on input signal amplitude
- **LFO Modulation**: Subtle movement and animation to the sound
- **Presets**: Four built-in presets for quick sound design

## Usage

### Starting the Effect

1. Select the guitar synth effect: `select guitar_synth`
2. Start the effect: `start`
3. Use `help` to see all available commands

### Basic Controls

- **ring_freq <hz>**: Set ring modulation frequency (20-2000 Hz)
- **bit_depth <bits>**: Set bit depth for crushing (1-16 bits)
- **sample_rate <factor>**: Set sample rate reduction (0.1-1.0)
- **wave_shape <amount>**: Set wave shaping intensity (0.0-1.0)
- **filter_cutoff <hz>**: Set filter cutoff frequency (20-20000 Hz)
- **filter_resonance <amount>**: Set filter resonance (0.0-1.0)
- **envelope <sensitivity>**: Set envelope sensitivity (0.0-1.0)
- **wet_mix <amount>**: Set wet/dry mix (0.0-1.0)
- **lfo_freq <hz>**: Set LFO frequency (0.1-20 Hz)
- **lfo_depth <amount>**: Set LFO depth (0.0-1.0)

### Presets

- **robotic**: Metallic, digital sound with high ring modulation
- **warm**: Smooth, analog-style filtering with subtle effects
- **digital**: Aggressive bit crushing and wave shaping
- **metallic**: Balanced metallic character with moderate effects

Use `preset <name>` to apply a preset, or `presets` to list available options.

### Examples

```bash
# Set up a robotic sound
ring_freq 200
bit_depth 4
sample_rate 0.3
wave_shape 0.8

# Create a warm, filtered sound
filter_cutoff 800
filter_resonance 0.2
envelope 0.4

# Apply a preset
preset digital

# Reset to defaults
reset
```

## Technical Details

The effect processes audio through a chain of effects in this order:

1. Ring modulation
2. Bit crushing
3. Sample rate reduction
4. Wave shaping
5. Low-pass filtering
6. Envelope modulation
7. LFO modulation

Each stage can be individually controlled, allowing for extensive sound design
possibilities.

## Tips

- Start with presets and then fine-tune individual parameters
- Use low ring modulation frequencies (50-200 Hz) for subtle metallic character
- Higher bit depths (12-16) preserve more of the original signal
- Lower sample rate reduction factors (0.1-0.5) create more digital artifacts
- The envelope follower responds to your playing dynamics
- LFO adds subtle movement - keep depth low (0.1-0.3) for natural sounds

## Integration

The guitar synth effect integrates seamlessly with the existing guitar effects
system and can be used alongside other effects like delays and the arpeggiator.
