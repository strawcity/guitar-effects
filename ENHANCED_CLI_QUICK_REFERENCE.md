# 🎸 Enhanced Interactive CLI Quick Reference

The enhanced interactive CLI now supports multiple effects including arpeggiator
and delay effects, with a menu-driven interface for easy effect selection and
control.

## 🚀 **Quick Start**

```bash
# Run the enhanced CLI
python interactive_cli.py

# Test the CLI functionality
python test_enhanced_cli.py
```

## 📋 **Main Commands**

| Command               | Description                |
| --------------------- | -------------------------- |
| `effects`             | List all available effects |
| `select <effect>`     | Select effect to control   |
| `status`              | Show current effect status |
| `help`                | Show effect-specific help  |
| `start`               | Start current effect       |
| `stop`                | Stop current effect        |
| `quit` / `q` / `exit` | Exit the CLI               |

## 🎛️ **Available Effects**

| Effect         | Description                             | Type  |
| -------------- | --------------------------------------- | ----- |
| `arpeggiator`  | Chord detection and arpeggio generation | Core  |
| `basic_delay`  | Simple echo delay effect                | Delay |
| `tape_delay`   | Vintage tape-style delay                | Delay |
| `multi_delay`  | Multi-tap delay patterns                | Delay |
| `tempo_delay`  | Tempo-synchronized delay                | Delay |
| `stereo_delay` | Stereo ping-pong delay                  | Delay |

## 🎹 **Arpeggiator Commands**

| Command      | Usage                         | Description             |
| ------------ | ----------------------------- | ----------------------- |
| `tempo`      | `tempo <bpm>` or `tempo +<n>` | Set or adjust tempo     |
| `pattern`    | `pattern <name>`              | Set arpeggio pattern    |
| `synth`      | `synth <name>`                | Set synthesizer type    |
| `duration`   | `duration <seconds>`          | Set arpeggio duration   |
| `demo`       | `demo`                        | Play demo arpeggio      |
| `test_audio` | `test_audio`                  | Test audio system       |
| `patterns`   | `patterns`                    | List available patterns |
| `synths`     | `synths`                      | List available synths   |

## 🎛️ **Delay Effect Commands**

### **Common Delay Commands** (All Types)

| Command      | Usage                  | Description         |
| ------------ | ---------------------- | ------------------- |
| `delay_time` | `delay_time <seconds>` | Set delay time      |
| `feedback`   | `feedback <0.0-0.9>`   | Set feedback amount |
| `wet_mix`    | `wet_mix <0.0-1.0>`    | Set wet/dry mix     |

### **Tape Delay Specific**

| Command        | Usage                     | Description                 |
| -------------- | ------------------------- | --------------------------- |
| `saturation`   | `saturation <0.0-1.0>`    | Set tape saturation         |
| `wow_rate`     | `wow_rate <0.0-2.0>`      | Set wow modulation rate     |
| `flutter_rate` | `flutter_rate <0.0-20.0>` | Set flutter modulation rate |
| `tape_speed`   | `tape_speed <0.5-2.0>`    | Set tape speed multiplier   |

### **Multi-Tap Delay Specific**

| Command      | Usage                          | Description        |
| ------------ | ------------------------------ | ------------------ |
| `sync_tempo` | `sync_tempo <bpm>`             | Sync taps to tempo |
| `add_tap`    | `add_tap <time> <level> <pan>` | Add new delay tap  |
| `remove_tap` | `remove_tap <index>`           | Remove delay tap   |

### **Tempo-Synced Delay Specific**

| Command         | Usage                  | Description        |
| --------------- | ---------------------- | ------------------ |
| `tempo`         | `tempo <bpm>`          | Set tempo for sync |
| `note_division` | `note_division <name>` | Set note division  |
| `swing`         | `swing <0.0-1.0>`      | Set swing amount   |
| `humanize`      | `humanize <0.0-1.0>`   | Set humanization   |

### **Stereo Delay Specific**

| Command        | Usage                    | Description              |
| -------------- | ------------------------ | ------------------------ |
| `left_delay`   | `left_delay <seconds>`   | Set left channel delay   |
| `right_delay`  | `right_delay <seconds>`  | Set right channel delay  |
| `ping_pong`    | `ping_pong <on/off>`     | Enable/disable ping-pong |
| `stereo_width` | `stereo_width <0.0-1.0>` | Set stereo width         |

## 🔄 **Usage Examples**

### **Basic Workflow**

```bash
# Start the CLI
python interactive_cli.py

# List available effects
effects

# Select arpeggiator
select arpeggiator

# Start arpeggiator
start

# Check status
status

# Adjust tempo
tempo 140

# Switch to delay effect
select basic_delay

# Configure delay
delay_time 0.5
feedback 0.3
wet_mix 0.6

# Start delay effect
start
```

### **Advanced Delay Configuration**

```bash
# Select tape delay
select tape_delay

# Configure tape characteristics
delay_time 0.6
saturation 0.4
wow_rate 0.5
flutter_rate 8.0

# Select multi-tap delay
select multi_delay

# Sync to tempo
sync_tempo 120

# Select stereo delay
select stereo_delay

# Configure stereo parameters
left_delay 0.3
right_delay 0.6
ping_pong on
stereo_width 0.5
```

## 🎯 **Effect-Specific Features**

### **Arpeggiator**

- Real-time chord detection
- 11 arpeggio patterns
- 9 synthesizer types
- Tempo control (60-200 BPM)
- Duration control (0.5-10.0 seconds)

### **Basic Delay**

- Clean echo effect
- Configurable delay time (1ms-2s)
- Feedback control (0-90%)
- Wet/dry mix control

### **Tape Delay**

- Vintage analog character
- Tape saturation and compression
- Wow and flutter modulation
- Variable tape speed

### **Multi-Tap Delay**

- Multiple delay lines
- Individual tap control
- Tempo synchronization
- Stereo panning

### **Tempo-Synced Delay**

- Musical timing sync
- Note division support
- Swing and humanization
- External clock sync

### **Stereo Delay**

- Independent L/R control
- Ping-pong patterns
- Stereo width enhancement
- Cross-feedback

## 🚨 **Troubleshooting**

### **Common Issues**

- **Effect not responding**: Check if effect is started with `start`
- **Unknown command**: Use `help` to see effect-specific commands
- **Parameter errors**: Check parameter ranges in help text
- **Audio issues**: Use `test_audio` to verify audio system

### **Getting Help**

- `help` - Show effect-specific commands
- `status` - Check effect status and parameters
- `effects` - List all available effects
- `select <effect>` - Switch to different effect

## 🎵 **Musical Applications**

### **Arpeggiator + Delay Combinations**

- **Basic Echo**: Arpeggiator → Basic Delay
- **Vintage Sound**: Arpeggiator → Tape Delay
- **Rhythmic Effects**: Arpeggiator → Multi-Tap Delay
- **Musical Timing**: Arpeggiator → Tempo-Synced Delay
- **Spatial Effects**: Arpeggiator → Stereo Delay

### **Performance Tips**

- Start with arpeggiator to establish rhythm
- Add delay effects gradually
- Use tempo sync for musical coherence
- Experiment with feedback and wet/dry mix
- Combine multiple delay types for complex textures

---

**🎸 Happy experimenting with your guitar effects system!**
