# 🎸 Headless Mode Quick Reference

## **Power On → Ready to Play in 3 Steps:**

### **1. Power Up** ⚡

- Connect power to Raspberry Pi
- Wait for system to boot (about 30 seconds) System ready message appears in
  logs

### **2. Connect Guitar** 🎸

- Plug Scarlett 2i2 into Pi (USB)
- Connect guitar to Scarlett input
- Connect speakers/headphones to Scarlett output

### **3. Press START** ▶️

- Press **START button** (GPIO 17) Arpeggiator starting and running status shown
  in logs
- Start playing guitar!

---

## **🎛️ Button Controls:**

| Button      | GPIO | Function                 |
| ----------- | ---- | ------------------------ |
| **START**   | 17   | Start arpeggiator        |
| **STOP**    | 18   | Stop arpeggiator         |
| **TEMPO +** | 22   | Increase tempo (+10 BPM) |
| **TEMPO -** | 23   | Decrease tempo (-10 BPM) |

---

## Status Indicators

Status is provided via console logs and service logs.

---

## Status Patterns

- System ready: Logged on startup
- Arpeggiator running: Logged on start
- Error conditions: Logged with ❌ prefix

---

## **🔧 Troubleshooting:**

| Problem                 | Solution                                            |
| ----------------------- | --------------------------------------------------- |
| **No sound**            | Check Scarlett connections, volume levels           |
| **Buttons not working** | Check wiring, reboot Pi                             |
| Buttons not responding  | Check GPIO connections, reboot Pi                   |
| **System won't start**  | Check logs: `sudo journalctl -u guitar-arpeggiator` |
| **Audio crackling**     | Check USB connection, reboot Pi                     |

---

## **📊 Service Management:**

```bash
# Check if running
sudo systemctl status guitar-arpeggiator

# View live logs
sudo journalctl -u guitar-arpeggiator -f

# Restart service
sudo systemctl restart guitar-arpeggiator

# Stop service
sudo systemctl stop guitar-arpeggiator

# Start service
sudo systemctl start guitar-arpeggiator
```

---

## **🎵 Typical Workflow:**

1. **Power on Pi** → Wait for READY log message
2. **Connect guitar** → Plug into Scarlett 2i2
3. **Press START** → System logs running status
4. **Play guitar** → Chord detections shown in logs
5. **Adjust tempo** → Press TEMPO buttons while playing
6. **Press STOP** → System stops and logs ready status
7. **Power off** → Safe to disconnect power

---

## **⚡ Power Management:**

- **Safe shutdown**: Press STOP button before powering off
- **Auto-restart**: System automatically restarts if it crashes
- **Boot time**: ~30 seconds from power on to ready
- **Idle power**: Very low when waiting for START button

---

**🎯 Goal: Plug in, press button, play guitar!**
