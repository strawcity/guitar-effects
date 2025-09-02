# Quick Start Guide

## Prerequisites

- Rust 1.70+ installed
- Audio device drivers for your system

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd guitar-effects/rust_audio_processor

# Build the project
cargo build --release
```

## Basic Usage

### Interactive Mode

Run the interactive command-line interface:

```bash
cargo run --release
```

This will start an interactive session where you can:

- Adjust parameters in real-time
- Test audio processing
- View system status

### Programmatic Usage

```rust
use rust_audio_processor::{AudioProcessor, AudioConfig};

// Create audio processor
let mut processor = AudioProcessor::new()?;

// Process audio data
let input_audio = vec![0.1, 0.2, 0.3, 0.4, 0.5];
let processed_audio = processor.process_audio(&input_audio)?;

// Set parameters
processor.set_stereo_delay_parameter("bpm", 120.0)?;
processor.set_stereo_delay_parameter("feedback", 0.5)?;
processor.set_stereo_delay_parameter("wet_mix", 0.7)?;
```

### Example

Run the basic usage example:

```bash
cargo run --example basic_usage
```

## Key Parameters

| Parameter        | Range   | Description                     |
| ---------------- | ------- | ------------------------------- |
| `bpm`            | 20-300  | Tempo in beats per minute       |
| `feedback`       | 0.0-0.9 | Feedback amount                 |
| `wet_mix`        | 0.0-1.0 | Wet signal mix                  |
| `stereo_width`   | 0.0-1.0 | Stereo width enhancement        |
| `cross_feedback` | 0.0-0.5 | Cross-feedback between channels |

## Testing

```bash
# Run tests
cargo test

# Run benchmarks
cargo bench

# Run with examples
cargo run --example basic_usage
```

## Performance Tips

1. **Use release builds**: `cargo build --release` for best performance
2. **Optimize buffer sizes**: Adjust `buffer_size` in configuration
3. **Batch processing**: Process larger buffers for better efficiency
4. **Parameter caching**: Avoid frequent parameter changes

## Troubleshooting

### Common Issues

1. **Audio device not found**: Check your system's audio drivers
2. **Permission denied**: Ensure audio device access permissions
3. **High latency**: Reduce buffer size or use lower sample rates

### Debug Mode

```bash
# Run with debug output
RUST_LOG=debug cargo run
```

## Next Steps

1. Read the [full documentation](README.md)
2. Explore the [examples](examples/)
3. Check the [comparison](COMPARISON.md) with Python version
4. Contribute to the project!

## Support

- Check the [README](README.md) for detailed documentation
- Review the [comparison](COMPARISON.md) for Python vs Rust differences
- Run examples to see the system in action
