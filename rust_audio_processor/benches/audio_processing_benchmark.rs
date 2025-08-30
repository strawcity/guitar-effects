use criterion::{black_box, criterion_group, criterion_main, Criterion};
use rust_audio_processor::{AudioProcessor, AudioConfig, StereoDelayConfig, DistortionConfig};

fn benchmark_audio_processing(c: &mut Criterion) {
    let mut group = c.benchmark_group("Audio Processing");
    
    // Create audio processor
    let config = AudioConfig {
        sample_rate: 44100,
        buffer_size: 4096,
        stereo_delay: StereoDelayConfig {
            left_delay: 0.3,
            right_delay: 0.6,
            feedback: 0.3,
            wet_mix: 0.6,
            ping_pong: true,
            stereo_width: 0.5,
            cross_feedback: 0.2,
        },
        distortion: DistortionConfig {
            enabled: true,
            distortion_type: "soft_clip".to_string(),
            drive: 0.3,
            mix: 0.7,
            feedback_intensity: 0.5,
        },
        ..Default::default()
    };
    
    let processor = AudioProcessor::with_config(config).unwrap();
    
    // Generate test audio data
    let sample_count = 44100; // 1 second at 44.1kHz
    let mut test_audio = Vec::with_capacity(sample_count);
    
    for i in 0..sample_count {
        let t = i as f32 / 44100.0;
        let sample = 0.3 * (2.0 * std::f32::consts::PI * 440.0 * t).sin();
        test_audio.push(sample);
    }
    
    group.bench_function("process_audio_1s", |b| {
        b.iter(|| {
            processor.process_audio(black_box(&test_audio)).unwrap()
        });
    });
    
    group.bench_function("process_audio_100ms", |b| {
        let short_audio = &test_audio[..4410]; // 100ms
        b.iter(|| {
            processor.process_audio(black_box(short_audio)).unwrap()
        });
    });
    
    group.bench_function("process_audio_10ms", |b| {
        let short_audio = &test_audio[..441]; // 10ms
        b.iter(|| {
            processor.process_audio(black_box(short_audio)).unwrap()
        });
    });
    
    group.finish();
}

fn benchmark_parameter_setting(c: &mut Criterion) {
    let mut group = c.benchmark_group("Parameter Setting");
    
    let config = AudioConfig::default();
    let processor = AudioProcessor::with_config(config).unwrap();
    
    group.bench_function("set_feedback", |b| {
        b.iter(|| {
            processor.set_stereo_delay_parameter("feedback", black_box(0.5)).unwrap()
        });
    });
    
    group.bench_function("set_wet_mix", |b| {
        b.iter(|| {
            processor.set_stereo_delay_parameter("wet_mix", black_box(0.7)).unwrap()
        });
    });
    
    group.bench_function("set_left_delay", |b| {
        b.iter(|| {
            processor.set_stereo_delay_parameter("left_delay", black_box(0.4)).unwrap()
        });
    });
    
    group.finish();
}

fn benchmark_stereo_delay_creation(c: &mut Criterion) {
    let mut group = c.benchmark_group("Stereo Delay Creation");
    
    group.bench_function("create_stereo_delay", |b| {
        b.iter(|| {
            use rust_audio_processor::{StereoDelay, DistortionType};
            black_box(StereoDelay::new(
                44100,
                0.3,
                0.6,
                0.3,
                0.6,
                true,
                0.5,
                0.2,
                true,
                DistortionType::SoftClip,
                0.3,
                0.7,
            ));
        });
    });
    
    group.finish();
}

criterion_group!(
    benches,
    benchmark_audio_processing,
    benchmark_parameter_setting,
    benchmark_stereo_delay_creation
);
criterion_main!(benches);
