#!/bin/bash

echo "🧪 Testing Stereo Audio Processing"
echo "================================="

# Build the project
echo "🔨 Building project..."
cargo build --release

# Test stereo processing
echo "🎵 Testing stereo processing..."
echo "This will run for 5 seconds to test stereo audio..."

# Run in background and capture output
./target/release/rust_audio_processor --daemon > stereo_test.log 2>&1 &
DAEMON_PID=$!

# Wait for a moment to see initial output
sleep 3

# Check if the process is still running
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "✅ Stereo test started successfully!"
    echo "📋 Output so far:"
    cat stereo_test.log
    
    echo ""
    echo "🎧 Expected behavior:"
    echo "  - You should hear audio in BOTH left and right channels"
    echo "  - Audio should be clear without static"
    echo "  - Stereo delay effect should be audible"
    echo ""
    echo "🔍 If you only hear audio in one ear:"
    echo "  - Check the device selection in the logs"
    echo "  - Verify Scarlett 2i2 is being used"
    echo "  - Check ALSA configuration"
else
    echo "❌ Stereo test failed to start!"
    echo "📋 Error output:"
    cat stereo_test.log
    exit 1
fi

# Stop the daemon
echo "🛑 Stopping test..."
kill $DAEMON_PID

# Wait for it to stop
sleep 2

echo "✅ Stereo test completed!"
echo "🎸 Check the logs above for device selection and audio configuration."
