# 🎸 Headless Mode Quick Reference

## **Power On → Ready to Play in 3 Steps:**

### **1. Power Up** ⚡

- Connect power to Raspberry Pi
- Wait for system to boot (about 30 seconds)
- **E LED will blink slowly** = System ready

### **2. Connect Guitar** 🎸

- Plug Scarlett 2i2 into Pi (USB)
- Connect guitar to Scarlett input
- Connect speakers/headphones to Scarlett output

### **3. Press START** ▶️

- Press **START button** (GPIO 17)
- **All LEDs flash** = Arpeggiator starting
- **E LED blinks rapidly** = System running
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

## **💡 LED Status Indicators:**

| LED   | GPIO | Meaning                                                      |
| ----- | ---- | ------------------------------------------------------------ |
| **C** | 12   | **Chord detected** OR **Tempo increased**                    |
| **E** | 13   | **System status** (slow blink = ready, fast blink = running) |
| **G** | 16   | **Chord detected** OR **Tempo decreased**                    |

---

## **🎯 LED Patterns:**

| Pattern                  | Meaning                         |
| ------------------------ | ------------------------------- |
| **E LED slow blink**     | System ready, waiting for START |
| **E LED fast blink**     | Arpeggiator running             |
| **C/E/G flash together** | System starting up              |
| **C/E/G rapid flash 3x** | Error occurred                  |
| **C flash briefly**      | Tempo increased                 |
| **G flash briefly**      | Tempo decreased                 |
| **C/E/G light up**       | Chord detected (while playing)  |

---

## **🔧 Troubleshooting:**

| Problem                 | Solution                                            |
| ----------------------- | --------------------------------------------------- |
| **No sound**            | Check Scarlett connections, volume levels           |
| **Buttons not working** | Check wiring, reboot Pi                             |
| **LEDs not lighting**   | Check GPIO connections, reboot Pi                   |
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

1. **Power on Pi** → Wait for E LED slow blink
2. **Connect guitar** → Plug into Scarlett 2i2
3. **Press START** → All LEDs flash, E LED fast blink
4. **Play guitar** → C/E/G LEDs light up for detected chords
5. **Adjust tempo** → Press TEMPO buttons while playing
6. **Press STOP** → System stops, E LED slow blink
7. **Power off** → Safe to disconnect power

---

## **⚡ Power Management:**

- **Safe shutdown**: Press STOP button before powering off
- **Auto-restart**: System automatically restarts if it crashes
- **Boot time**: ~30 seconds from power on to ready
- **Idle power**: Very low when waiting for START button

---

**🎯 Goal: Plug in, press button, play guitar!**
