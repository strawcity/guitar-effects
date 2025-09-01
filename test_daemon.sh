#!/bin/bash

echo "🧪 Testing Rust Audio Processor Daemon Mode"
echo "=========================================="

# Build the project
echo "🔨 Building project..."
cargo build --release

# Test daemon mode
echo "🎵 Testing daemon mode..."
echo "This will run for 10 seconds to verify it starts correctly..."

# Run in background and capture output
./target/release/rust_audio_processor --daemon > daemon_output.log 2>&1 &
DAEMON_PID=$!

# Wait for a moment to see initial output
sleep 3

# Check if the process is still running
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "✅ Daemon started successfully!"
    echo "📋 Output so far:"
    cat daemon_output.log
else
    echo "❌ Daemon failed to start!"
    echo "📋 Error output:"
    cat daemon_output.log
    exit 1
fi

# Stop the daemon
echo "🛑 Stopping daemon..."
kill $DAEMON_PID

# Wait for it to stop
sleep 2

echo "✅ Daemon test completed successfully!"
echo "🎸 The daemon mode is ready for systemd service deployment."
