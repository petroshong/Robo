# Step-by-Step Upload Instructions

## ✅ Step 1: Upload Arduino Firmware

### In Arduino IDE:

1. **Open the file:**
   - File → Open → Navigate to `/Users/petroshong/Robo/arduino_motor.ino`

2. **Select Board:**
   - Tools → Board → Arduino AVR Boards → **Arduino Mega 2560**

3. **Select Port:**
   - Tools → Port → **/dev/cu.usbmodem1101** (or the port shown in Arduino IDE)

4. **Upload:**
   - Click the Upload button (→) or press `Cmd+U`
   - Wait for "Done uploading" message

5. **Open Serial Monitor:**
   - Tools → Serial Monitor
   - Set baud rate to **9600**
   - You should see: `ARDUINO_READY`

### ✅ Verification:
Run this test to verify:
```bash
python3 test_arduino_connection.py
```

You should see:
```
✓ ARDUINO_READY signal received!
✓ Arduino is responding to commands!
```

---

## ✅ Step 2: Test GUI Program

Once firmware is uploaded:

1. **Run the GUI:**
   ```bash
   python3 robot_control_gui.py
   ```

2. **In the GUI window:**
   - Click **"Connect"** button (should turn green)
   - Status should show: "● Connected"
   - Port should show: "Port: /dev/cu.usbmodem1101"

3. **Test movement buttons:**
   - Click **⬆ FORWARD** - Check log for "OK:FORWARD"
   - Click **⬇ BACKWARD** - Check log for "OK:BACKWARD"
   - Click **⬅ LEFT** - Check log for "OK:LEFT"
   - Click **➡ RIGHT** - Check log for "OK:RIGHT"
   - Click **⏹ STOP** - Check log for "OK:STOP"

4. **Check the log window:**
   - Should show commands being sent
   - Should show Arduino responses like "OK:FORWARD"

---

## ✅ Step 3: Wire Motors (When Ready)

### Motor Wiring (L298N Driver):

**Arduino Mega 2560 → L298N Motor Driver:**

```
Left Front Motor:
  Pin 8  → IN1
  Pin 7  → IN2
  Pin 9  → ENA (PWM)

Right Front Motor:
  Pin 12 → IN1
  Pin 11 → IN2
  Pin 10 → ENA (PWM)

Left Rear Motor:
  Pin 4  → IN1
  Pin 3  → IN2
  Pin 5  → ENA (PWM)

Right Rear Motor:
  Pin 2  → IN1
  Pin 13 → IN2
  Pin 6  → ENA (PWM)
```

**L298N Power:**
- VCC → 5V (from Arduino or external)
- GND → Common ground (connect Arduino GND to L298N GND)
- 12V → External 12V power supply (for motors)
- Motor outputs → Connect to your 4 DC motors

**Important:**
- If your wiring is different, edit `arduino_motor.ino` and change the pin numbers
- Make sure all grounds are connected together
- Test each motor individually before connecting all 4

---

## Troubleshooting

### "ARDUINO_READY not received"
- Firmware not uploaded - go back to Step 1
- Wrong board selected in Arduino IDE
- Wrong port selected

### "Failed to connect" in GUI
- Arduino not connected
- Wrong port in config.py
- Another program using the serial port (close Arduino Serial Monitor)

### "No response" to commands
- Firmware not uploaded
- Wrong baud rate (should be 9600)
- Check Serial Monitor in Arduino IDE to see if commands are received

### Motors not moving
- Motors not wired yet (that's okay - test commands first!)
- Check wiring matches pin definitions
- Verify power supply to L298N
- Test motors directly with Arduino Serial Monitor

---

## Current Status

✅ Arduino detected: `/dev/cu.usbmodem1101`  
✅ Code ready  
⏳ **Next: Upload firmware (Step 1)**



