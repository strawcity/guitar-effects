# 🔌 Complete Wiring Diagram for Raspberry Pi

## **🎯 What You Need:**

### **Components:**

- **3x LEDs** (5mm, any color)
- **3x 220Ω resistors** (for LEDs)
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

## **💡 LED Wiring (GPIO as OUTPUT):**

### **How LEDs Work:**

```
3.3V ←→ 220Ω Resistor ←→ LED ←→ GPIO Pin (Output)
```

**When GPIO is HIGH:** Current flows, LED lights up **When GPIO is LOW:** No
current, LED is off

### **LED Connections:**

#### **C Note LED (GPIO 12):**

```
3.3V ←→ 220Ω Resistor ←→ LED Anode (+)
LED Cathode (-) ←→ GPIO 12 (Pin 32)
```

#### **E Note LED (GPIO 13):**

```
3.3V ←→ 220Ω Resistor ←→ LED Anode (+)
LED Cathode (-) ←→ GPIO 13 (Pin 33)
```

#### **G Note LED (GPIO 16):**

```
3.3V ←→ 220Ω Resistor ←→ LED Anode (+)
LED Cathode (-) ←→ GPIO 16 (Pin 36)
```

---

## **🎛️ Complete Circuit Layout:**

### **Power Distribution:**

```
3.3V ←→ Multiple 220Ω resistors ←→ LED circuits
Ground (GND) ←→ Multiple 10kΩ resistors ←→ Button circuits
```

### **Breadboard Layout:**

```
Power Rail (3.3V):
├── 220Ω → LED C → GPIO 12
├── 220Ω → LED E → GPIO 13
└── 220Ω → LED G → GPIO 16

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

### **Step 2: LEDs**

1. Place LED on breadboard (note anode/cathode)
2. Connect **220Ω resistor** from 3.3V to LED anode
3. Connect **LED cathode** to GPIO pin via jumper wire

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

- **Anode (+)**: Longer leg, connects to resistor
- **Cathode (-)**: Shorter leg, connects to GPIO
- **Wrong polarity**: LED won't light up

### **Resistor Values:**

- **220Ω for LEDs**: Prevents too much current
- **10kΩ for buttons**: Pull-up resistor, not too strong

### **GPIO Configuration:**

- **LEDs**: Configured as OUTPUT in software
- **Buttons**: Configured as INPUT with internal pull-up enabled
- **No external power needed**: Pi provides 3.3V and ground

---

## **🎯 Why This Works:**

1. **GPIO pins are programmable** - can be INPUT or OUTPUT
2. **Buttons create a switch** between GPIO and ground
3. **Pull-up resistors** ensure stable HIGH state when not pressed
4. **Software detects voltage change** from HIGH to LOW
5. **LEDs are controlled** by setting GPIO HIGH/LOW

**The magic is that one GPIO pin can be either input OR output, and the button
circuit creates a simple voltage divider that the Pi can read!**
