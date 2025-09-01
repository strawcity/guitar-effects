# System Architecture

## Overview

The Guitar Effects System is built with a modular, high-performance architecture
designed for real-time audio processing. The system is written in Rust and
provides a unified API across multiple platforms while leveraging
platform-specific optimizations.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Main Application (main.rs)                                 │
│  ├── CLI Interface                                          │
│  ├── Interactive Mode                                       │
│  └── GPIO Integration (Raspberry Pi)                       │
├─────────────────────────────────────────────────────────────┤
│                    Audio Processing Layer                   │
├─────────────────────────────────────────────────────────────┤
│  Audio Processor (audio_processor.rs)                       │
│  ├── Stereo Delay Effects                                   │
│  ├── Distortion Effects                                     │
│  └── Real-time Parameter Control                           │
├─────────────────────────────────────────────────────────────┤
│                    Platform Abstraction Layer               │
├─────────────────────────────────────────────────────────────┤
│  Cross-Platform Audio I/O (CPAL)                           │
│  ├── macOS: Core Audio                                      │
│  ├── Linux: ALSA                                            │
│  └── Windows: WASAPI                                        │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Configuration System (config.rs)                           │
│  ├── Platform Detection                                     │
│  ├── Audio Device Management                               │
│  └── Effect Parameter Storage                              │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. Main Application (`src/main.rs`)

- **Purpose**: Application entry point and user interface
- **Responsibilities**:
  - CLI argument parsing and validation
  - Interactive mode management
  - GPIO integration (Raspberry Pi)
  - Real-time parameter control
  - Error handling and graceful shutdown

### 2. Audio Processor (`src/audio_processor.rs`)

- **Purpose**: Core audio processing engine
- **Responsibilities**:
  - Real-time audio I/O management
  - Effect chain processing
  - Buffer management and synchronization
  - Performance optimization
  - Cross-platform audio backend abstraction

### 3. Stereo Delay Effects (`src/delay.rs`)

- **Purpose**: Advanced stereo delay implementation
- **Responsibilities**:
  - Independent left/right channel delay
  - Ping-pong delay patterns
  - Cross-feedback between channels
  - Stereo width enhancement
  - Modulation and tempo sync

### 4. Distortion Effects (`src/distortion.rs`)

- **Purpose**: Cross-feedback distortion algorithms
- **Responsibilities**:
  - Multiple distortion types (SoftClip, HardClip, Tube, Fuzz, etc.)
  - Cross-feedback signal processing
  - Drive and mix control
  - Harmonic enhancement

### 5. Configuration System (`src/config.rs`)

- **Purpose**: System configuration and platform detection
- **Responsibilities**:
  - Platform-specific optimizations
  - Audio device detection and prioritization
  - Effect parameter management
  - Configuration persistence

### 6. Platform-Specific Processors

- **ALSA Processor** (`src/alsa_processor.rs`): Linux-specific audio processing
- **Error Handling** (`src/error.rs`): Unified error types and handling

## 🔄 Data Flow

### Audio Processing Pipeline

```
Input Signal → Audio Processor → Effect Chain → Output Signal
     ↓              ↓              ↓              ↓
  Guitar      Real-time      Stereo Delay    Processed
  Input       Processing     + Distortion    Output
```

### Detailed Processing Flow

1. **Input Capture**: Audio input from guitar/audio interface
2. **Buffer Management**: Ring buffer for low-latency processing
3. **Effect Processing**: Stereo delay with cross-feedback distortion
4. **Output Rendering**: Processed audio sent to output device
5. **Parameter Control**: Real-time parameter adjustment via CLI/GPIO

## 🎛️ Effect Chain Architecture

### Stereo Delay Effect Chain

```
Left Input ──┐                    ┌── Left Output
             ├── Left Delay ──┐   │
             │                ├───┤
             │                │   │
Right Input ─┘                │   │
             ┌── Right Delay ─┘   │
             │                    │
             └── Cross-Feedback ─┘
```

### Cross-Feedback Distortion Integration

```
Left Delay Output ──┐
                   ├── Cross-Feedback ── Distortion ──┐
                   │                                   │
Right Delay Output ─┘                                   │
                                                       │
                   ┌── Left Output ◄───────────────────┘
                   │
                   └── Right Output ◄───────────────────┘
```

## 🔧 Modular Design Principles

### 1. Separation of Concerns

- **Audio I/O**: Handled by platform-specific backends
- **Effect Processing**: Modular effect implementations
- **Configuration**: Centralized configuration management
- **User Interface**: Separate CLI and interactive modes

### 2. Platform Abstraction

- **Unified API**: Common interface across platforms
- **Platform Detection**: Automatic platform-specific optimizations
- **Graceful Fallback**: Fallback mechanisms for missing features

### 3. Extensibility

- **Trait-Based Design**: Common interfaces for effects
- **Plugin Architecture**: Easy addition of new effects
- **Configuration-Driven**: Effect parameters via configuration

### 4. Performance Optimization

- **Zero-Copy Processing**: Minimize memory allocations
- **SIMD Optimization**: Vectorized audio processing
- **Lock-Free Design**: Thread-safe audio processing
- **Buffer Optimization**: Optimized buffer sizes and management

## 🎯 Key Design Decisions

### 1. Rust Implementation

- **Memory Safety**: Guaranteed memory safety without garbage collection
- **Performance**: Near-C performance with high-level abstractions
- **Concurrency**: Safe concurrent programming with ownership system
- **Cross-Platform**: Native compilation for all target platforms

### 2. Real-Time Processing

- **Low Latency**: Optimized for real-time audio processing
- **Predictable Performance**: Consistent processing times
- **Buffer Management**: Efficient ring buffer implementation
- **Thread Safety**: Lock-free audio processing pipeline

### 3. Cross-Platform Support

- **Unified API**: Common interface across platforms
- **Platform-Specific Optimizations**: Leverage platform strengths
- **Device Detection**: Automatic audio device detection
- **Configuration Persistence**: Platform-specific configuration storage

### 4. Professional Audio Quality

- **Studio-Grade Algorithms**: Professional audio processing
- **High Sample Rates**: Support for up to 192kHz
- **24-bit Processing**: High-resolution audio processing
- **Minimal Distortion**: Clean signal path with minimal artifacts

## 🔗 Component Relationships

### Dependencies

```
main.rs
├── audio_processor.rs
│   ├── delay.rs
│   ├── distortion.rs
│   └── config.rs
├── config.rs
├── error.rs
└── alsa_processor.rs (Linux only)
```

### Trait Interfaces

The system uses trait-based design for extensibility:

```rust
// Common audio processor interface
pub trait AudioProcessorTrait {
    fn start_audio(&mut self) -> Result<(), AudioProcessorError>;
    fn stop_audio(&mut self) -> Result<(), AudioProcessorError>;
    fn set_stereo_delay_parameter(&self, param: &str, value: f32) -> Result<(), AudioProcessorError>;
    // ... other methods
}

// Base delay effect interface
pub trait BaseDelay {
    fn process_sample(&mut self, input_sample: f32) -> (f32, f32);
    fn set_delay_time(&mut self, delay_time: f32);
    fn set_feedback(&mut self, feedback: f32);
    // ... other methods
}
```

## 🚀 Performance Characteristics

### Latency Targets

- **Input Latency**: < 5ms
- **Processing Latency**: < 2ms
- **Total Round-Trip**: < 10ms

### Throughput

- **Sample Rate**: 44.1kHz - 192kHz
- **Bit Depth**: 16-bit - 24-bit
- **Channels**: Stereo (2 channels)

### Resource Usage

- **CPU Usage**: < 5% on modern hardware
- **Memory Usage**: < 50MB
- **Buffer Sizes**: Configurable (256 - 8192 samples)

## 🔮 Future Architecture Extensions

### Planned Enhancements

1. **Effect Chain Management**: Configurable effect routing
2. **MIDI Integration**: External MIDI control
3. **Plugin System**: Dynamic effect loading
4. **Network Control**: Remote control via web interface
5. **Multi-Channel Support**: Surround sound processing

### Scalability Considerations

- **Multi-Effect Processing**: Parallel effect processing
- **Distributed Processing**: Network-distributed audio processing
- **Cloud Integration**: Cloud-based effect processing
- **Mobile Support**: iOS/Android companion apps
