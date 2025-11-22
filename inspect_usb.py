#!/usr/bin/env python3
"""
USB Device Inspector
Helps identify connected Arduino and serial devices.
Run this when your Arduino is connected via USB.
"""

import serial
import serial.tools.list_ports
import sys
import platform
import time


def inspect_serial_ports():
    """Inspect all available serial ports."""
    print("=" * 60)
    print("SERIAL PORTS INSPECTION")
    print("=" * 60)
    print()
    
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No serial ports found!")
        print("\nMake sure:")
        print("  - Arduino is connected via USB")
        print("  - USB cable supports data (not just power)")
        print("  - Arduino drivers are installed")
        return
    
    print(f"✓ Found {len(ports)} serial port(s):\n")
    
    for i, port in enumerate(ports, 1):
        print(f"Port #{i}:")
        print(f"  Device: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Manufacturer: {port.manufacturer or 'Unknown'}")
        print(f"  Hardware ID: {port.hwid}")
        print(f"  VID:PID: {port.vid}:{port.pid if port.pid else 'N/A'}")
        
        # Check if it looks like Arduino
        is_arduino = False
        if port.manufacturer:
            if "arduino" in port.manufacturer.lower() or "arduino" in port.description.lower():
                is_arduino = True
                print(f"  🎯 LIKELY ARDUINO!")
        
        print()
    
    # Suggest most likely Arduino port
    print("=" * 60)
    print("RECOMMENDED ARDUINO PORT:")
    print("=" * 60)
    
    # Try to find Arduino by manufacturer/description
    arduino_ports = []
    for port in ports:
        desc_lower = port.description.lower()
        man_lower = (port.manufacturer or "").lower()
        if "arduino" in desc_lower or "arduino" in man_lower or "ch340" in desc_lower or "ftdi" in desc_lower:
            arduino_ports.append(port.device)
    
    if arduino_ports:
        print(f"✓ Most likely: {arduino_ports[0]}")
        print(f"\nUpdate config.py with:")
        print(f'  ARDUINO_PORT = "{arduino_ports[0]}"')
    else:
        print("⚠ Could not auto-detect Arduino")
        print("Try the first port listed above, or check manually")
        if ports:
            print(f"\nSuggested port: {ports[0].device}")
    
    print()


def test_port_connection(port_path):
    """Test if we can connect to a port."""
    print(f"\nTesting connection to {port_path}...")
    try:
        ser = serial.Serial(port_path, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino reset
        ser.close()
        print(f"✓ Successfully opened {port_path}")
        return True
    except serial.SerialException as e:
        print(f"✗ Failed to open {port_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main function."""
    import time
    
    print("\n🔍 USB/Serial Device Inspector")
    print("Connect your Arduino via USB and run this script\n")
    
    inspect_serial_ports()
    
    # Ask if user wants to test connection
    if len(sys.argv) > 1:
        port_to_test = sys.argv[1]
        test_port_connection(port_to_test)
    else:
        print("=" * 60)
        print("To test a specific port, run:")
        print(f"  python3 {sys.argv[0]} /dev/ttyACM0")
        print("=" * 60)


if __name__ == "__main__":
    main()

