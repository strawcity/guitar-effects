# 🔌 Complete Wiring Diagram for Raspberry Pi

## **🎯 What You Need:**

### **Components:**

- **4x Push buttons** (momentary)
- **4x 10kΩ resistors** (for buttons)
- **Breadboard** (for prototyping)
- **Jumper wires** (male-to-female for Pi connection)

### **Raspberry Pi Pins:**

- **Power**: 3.3V, 5V, Ground (GND)
- **GPIO**: 12, 13, 16, 17, 18, 22, 23, 24, 25, 26

---

## **🔌 Button Wiring (GPIO as INPUT):**

### **How Buttons Work:**

```
GPIO Pin (Input) ←→ 10kΩ Resistor ←→ Button ←→ Ground (GND)
```

**When button NOT pressed:** GPIO reads HIGH (3.3V) via pull-up resistor **When
button IS pressed:** GPIO reads LOW (0V) because connected to ground

### **Button Connections:**

#### **START Button (GPIO 17):**

```
GPIO 17 (Pin 11) ←→ 10kΩ Resistor ←→ Button Terminal 1
Button Terminal 2 ←→ Ground (GND)
```

#### **STOP Button (GPIO 18):**

```
GPIO 18 (Pin 12) ←→ 10kΩ Resistor ←→ Button Terminal 1
Button Terminal 2 ←→ Ground (GND)
```

#### **TEMPO UP Button (GPIO 22):**

```
GPIO 22 (Pin 15) ←→ 10kΩ Resistor ←→ Button Terminal 1
Button Terminal 2 ←→ Ground (GND)
```

#### **TEMPO DOWN Button (GPIO 23):**

```
GPIO 23 (Pin 16) ←→ 10kΩ Resistor ←→ Button Terminal 1
Button Terminal 2 ←→ Ground (GND)
```

---

## LED Wiring

LEDs are no longer used in this project. You can skip any LED wiring.

---

## **🎛️ Complete Circuit Layout:**

### **Power Distribution:**

```
Ground (GND) ←→ Multiple 10kΩ resistors ←→ Button circuits
```

### **Breadboard Layout:**

```
Power Rail (3.3V):
(buttons use internal pull-ups; see button wiring below)

Ground Rail (GND):
├── 10kΩ → Button START → GPIO 17
├── 10kΩ → Button STOP → GPIO 18
├── 10kΩ → Button TEMPO+ → GPIO 22
└── 10kΩ → Button TEMPO- → GPIO 23
```

---

## **🔧 Step-by-Step Assembly:**

### **Step 1: Power Rails**

1. Connect **3.3V** to breadboard power rail
2. Connect **Ground (GND)** to breadboard ground rail

### **Step 2: (Skipped) LEDs**

LEDs are not used.

### **Step 3: Buttons**

1. Place button on breadboard
2. Connect **10kΩ resistor** from GPIO pin to button terminal 1
3. Connect **button terminal 2** to ground

### **Step 4: Test**

1. Power on Pi
2. Check LEDs light up when GPIO goes HIGH
3. Check buttons register when pressed

---

## **⚠️ Important Notes:**

### **LED Polarity:**

LEDs are not used.

### **Resistor Values:**

- **10kΩ for buttons**: Pull-up resistor, not too strong

### **GPIO Configuration:**

- **Buttons**: Configured as INPUT with internal pull-up enabled
- **No external power needed**: Pi provides 3.3V and ground

---

## **🎯 Why This Works:**

1. **GPIO pins are programmable** - can be INPUT or OUTPUT
2. **Buttons create a switch** between GPIO and ground
3. **Pull-up resistors** ensure stable HIGH state when not pressed
4. **Software detects voltage change** from HIGH to LOW
5. Buttons are read via GPIO input with pull-ups

**The magic is that one GPIO pin can be either input OR output, and the button
circuit creates a simple voltage divider that the Pi can read!**
