#!/usr/bin/env python3
"""
Quick test to verify Arduino is connected and firmware is uploaded.
"""

import serial
import time
import config

def test_arduino():
    """Test Arduino connection and firmware."""
    print("=" * 60)
    print("ARDUINO CONNECTION TEST")
    print("=" * 60)
    print()
    
    port = config.ARDUINO_PORT
    print(f"Attempting to connect to: {port}")
    print()
    
    try:
        # Connect to Arduino
        ser = serial.Serial(port, config.ARDUINO_BAUD_RATE, timeout=2)
        print(f"✓ Successfully opened {port}")
        print("  Waiting for Arduino to initialize...")
        time.sleep(2)  # Wait for Arduino reset
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Look for ready signal
        print("  Looking for ARDUINO_READY signal...")
        start_time = time.time()
        found_ready = False
        
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"  Received: {line}")
                        if "ARDUINO_READY" in line:
                            found_ready = True
                            print("  ✓ ARDUINO_READY signal received!")
                            break
                except Exception as e:
                    # Skip invalid data
                    pass
            time.sleep(0.1)
        
        if not found_ready:
            print("  ⚠ ARDUINO_READY not received (firmware may not be uploaded)")
            print("  But connection is working - you can still test commands")
        
        # Test sending a command
        print()
        print("Testing command: STATUS")
        ser.write(b"STATUS\n")
        ser.flush()
        
        time.sleep(0.5)
        if ser.in_waiting > 0:
            try:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"  Response: {response}")
                    if response.startswith("OK:"):
                        print("  ✓ Arduino is responding to commands!")
                    else:
                        print("  ⚠ Unexpected response")
            except Exception as e:
                print(f"  ⚠ Error reading response: {e}")
        else:
            print("  ⚠ No response (firmware may need to be uploaded)")
        
        ser.close()
        print()
        print("=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print()
        if found_ready:
            print("✓ Arduino firmware is uploaded and working!")
            print("  You can now run: python3 robot_control_gui.py")
        else:
            print("⚠ Arduino is connected but firmware may not be uploaded.")
            print("  Please upload arduino_motor.ino to your Arduino first.")
        
    except serial.SerialException as e:
        print(f"✗ Failed to connect: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure Arduino is connected via USB")
        print("  2. Check that the port is correct in config.py")
        print("  3. Make sure no other program is using the serial port")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_arduino()

