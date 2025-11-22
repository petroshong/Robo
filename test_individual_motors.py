#!/usr/bin/env python3
"""
Test each motor individually to identify which one is working.
"""

import serial
import time
import config

def test_motor(ser, test_command, motor_name):
    """Test a single motor."""
    print(f"\n{'='*60}")
    print(f"Testing {motor_name}")
    print(f"{'='*60}")
    print(f"Sending command: {test_command}")
    
    ser.write((test_command + "\n").encode('utf-8'))
    ser.flush()
    
    # Wait for response
    start_time = time.time()
    while time.time() - start_time < 5:
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Response: {response}")
            if response.startswith("Testing"):
                # Motor is being tested - it will move forward for 1s, then backward for 1s
                print(f"  → {motor_name} should move FORWARD for 1 second...")
                time.sleep(1.2)
                print(f"  → {motor_name} should move BACKWARD for 1 second...")
                time.sleep(1.2)
                if ser.in_waiting > 0:
                    final = ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Final: {final}")
                break
        time.sleep(0.1)
    
    print(f"\nDid {motor_name} move? (y/n): ", end="")
    # Don't wait for input in script - user will observe

def main():
    """Test all motors individually."""
    print("=" * 60)
    print("INDIVIDUAL MOTOR TEST")
    print("=" * 60)
    print("\nThis will test each motor one at a time.")
    print("Watch which motor moves and note it down!")
    print("\nMotor positions:")
    print("  LF = Left Front")
    print("  RF = Right Front")
    print("  LR = Left Rear")
    print("  RR = Right Rear")
    print("\nPress Enter to start...")
    input()
    
    try:
        ser = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD_RATE, timeout=2)
        time.sleep(2)
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Wait for ready
        print("Waiting for Arduino...")
        start_time = time.time()
        while time.time() - start_time < 3:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "ARDUINO_READY" in line:
                    print("✓ Arduino ready\n")
                    break
            time.sleep(0.1)
        
        # Test each motor
        motors = [
            ("TEST_LF", "Left Front (LF)"),
            ("TEST_RF", "Right Front (RF)"),
            ("TEST_LR", "Left Rear (LR)"),
            ("TEST_RR", "Right Rear (RR)")
        ]
        
        results = {}
        for cmd, name in motors:
            test_motor(ser, cmd, name)
            print("\nPress Enter to test next motor...")
            input()
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nWhich motor(s) moved?")
        print("This will help identify which pins are actually connected.")
        
        ser.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()

