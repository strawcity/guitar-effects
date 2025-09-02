#!/bin/bash

# Demo script for CLI web interface notifications

echo "🎸 Guitar Effects CLI Web Interface Notification Demo" echo
"=====================================================" echo "" echo "This demo
shows how the CLI will display notifications when" echo "parameters are changed
from the web interface." echo "" echo "Setup:" echo "1. Run the guitar effects
in interactive mode on your Pi" echo "2. Access the web interface from your
laptop" echo "3. Change parameters in the web interface" echo "4. Watch the CLI
show notifications in real-time" echo "" echo "Commands to run:" echo "" echo
"On Raspberry Pi (via Pi-Connect or SSH):" echo " cargo run --release" echo ""
echo "On your laptop browser:" echo " http://[raspberry-pi-ip]:1051" echo ""
echo "Example CLI output when web interface changes parameters:" echo "" echo
"🎛️ Interactive Parameter Control" echo "Type 'help' for available commands,
'quit' to exit" echo "📱 Web interface changes will be shown here" echo "" echo
"> " echo "" echo "🌐 [14:32:15] Web Interface: Left Delay changed from 0.30s to
0.45s" echo "> " echo "" echo "🌐 [14:32:18] Web Interface: Feedback changed
from 0.30 to 0.55" echo "> " echo "" echo "🌐 [14:32:22] Web Interface: BPM
changed from 120 BPM to 140 BPM" echo "> " echo "" echo "Features:" echo "✅
Real-time notifications with timestamps" echo "✅ Formatted parameter names
(Left Delay, Feedback, etc.)" echo "✅ Appropriate value formatting (seconds,
BPM, percentages)" echo "✅ Non-intrusive (doesn't break CLI input)" echo "✅
Works with any parameter change from web interface" echo "" echo "Perfect for
remote control via Pi-Connect!"
