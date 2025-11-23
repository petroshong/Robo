#!/usr/bin/env python3
"""
Simple test script to send commands to the robot dog server.
Usage: python3 test_commands.py <command>
Commands: FORWARD, BACKWARD, LEFT, RIGHT, STOP
"""

import sys
import requests
import time
import config

SERVER_URL = f"http://localhost:{config.SERVER_PORT}"


def send_command(command: str):
    """Send a command to the robot server."""
    try:
        response = requests.post(
            f"{SERVER_URL}/command",
            json={
                "command": command.upper(),
                "token": config.AUTH_TOKEN
            },
            timeout=2
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: {data.get('command')} - {data.get('arduino_response', '')}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Error: Could not connect to server at {SERVER_URL}")
        print("  Make sure pi_main.py is running!")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_health():
    """Test server health endpoint."""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"Server Status: {data.get('status')}")
            print(f"Arduino: {data.get('arduino')}")
            return True
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_commands.py <command>")
        print("Commands: FORWARD, BACKWARD, LEFT, RIGHT, STOP, HEALTH")
        print("\nExample:")
        print("  python3 test_commands.py FORWARD")
        print("  python3 test_commands.py HEALTH")
        sys.exit(1)
    
    command = sys.argv[1].upper()
    
    if command == "HEALTH":
        test_health()
    elif command in ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP", "FWD", "BWD", "REVERSE"]:
        send_command(command)
    else:
        print(f"Invalid command: {command}")
        print("Valid commands: FORWARD, BACKWARD, LEFT, RIGHT, STOP, HEALTH")
        sys.exit(1)


if __name__ == "__main__":
    main()



