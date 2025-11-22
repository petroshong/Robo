#!/usr/bin/env python3
"""
Test script to verify all movement commands work.
"""

import serial
import time
import config

def test_command(ser, command):
    """Test a single command."""
    print(f"\nTesting: {command}")
    ser.write((command + "\n").encode('utf-8'))
    ser.flush()
    
    time.sleep(0.5)
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"  Response: {response}")
        if response.startswith("OK:"):
            print(f"  ✓ {command} works!")
            return True
        else:
            print(f"  ✗ Unexpected response")
            return False
    else:
        print(f"  ✗ No response")
        return False

def main():
    """Test all commands."""
    print("=" * 60)
    print("TESTING ALL MOVEMENT COMMANDS")
    print("=" * 60)
    
    try:
        ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD_RATE, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Wait for ready
        print("Waiting for Arduino...")
        start_time = time.time()
        while time.time() - start_time < 3:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "ARDUINO_READY" in line:
                    print("✓ Arduino ready")
                    break
            time.sleep(0.1)
        
        # Test all commands
        commands = ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"]
        results = {}
        
        for cmd in commands:
            results[cmd] = test_command(ser, cmd)
            time.sleep(0.3)  # Small delay between commands
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        for cmd, success in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{cmd:10} {status}")
        
        ser.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()

