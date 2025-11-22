#!/usr/bin/env python3
"""
Police Robot Dog - Raspberry Pi Main Server
Receives commands via HTTP POST and controls Arduino via serial communication.
"""

import serial
import serial.tools.list_ports
import time
import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Optional, Dict
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global serial connection
arduino_serial: Optional[serial.Serial] = None
last_command_time: float = 0
connection_monitor_thread: Optional[threading.Thread] = None
monitor_running = False


def find_arduino_port() -> Optional[str]:
    """
    Automatically find Arduino port by checking common ports.
    Returns port path if found, None otherwise.
    """
    # Common Arduino ports
    common_ports = [
        "/dev/ttyACM0", "/dev/ttyACM1",
        "/dev/ttyUSB0", "/dev/ttyUSB1",
        "/dev/ttyAMA0"
    ]
    
    # Try the configured port first
    if config.ARDUINO_PORT:
        try:
            test_serial = serial.Serial(config.ARDUINO_PORT, config.ARDUINO_BAUD_RATE, timeout=1)
            test_serial.close()
            logger.info(f"Found Arduino at configured port: {config.ARDUINO_PORT}")
            return config.ARDUINO_PORT
        except (serial.SerialException, OSError):
            pass
    
    # Try common ports
    for port in common_ports:
        try:
            test_serial = serial.Serial(port, config.ARDUINO_BAUD_RATE, timeout=1)
            test_serial.close()
            logger.info(f"Found Arduino at: {port}")
            return port
        except (serial.SerialException, OSError):
            continue
    
    # List all available ports
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    logger.warning(f"Arduino not found. Available ports: {available_ports}")
    return None


def connect_arduino() -> bool:
    """
    Establish serial connection with Arduino.
    Returns True if successful, False otherwise.
    """
    global arduino_serial
    
    port = find_arduino_port()
    if not port:
        logger.error("Could not find Arduino port. Check connections.")
        return False
    
    try:
        arduino_serial = serial.Serial(
            port=port,
            baudrate=config.ARDUINO_BAUD_RATE,
            timeout=config.SERIAL_TIMEOUT,
            write_timeout=1.0
        )
        time.sleep(2)  # Wait for Arduino to reset
        
        # Clear any existing data
        arduino_serial.reset_input_buffer()
        arduino_serial.reset_output_buffer()
        
        # Wait for Arduino ready signal
        start_time = time.time()
        while time.time() - start_time < 3:
            if arduino_serial.in_waiting > 0:
                line = arduino_serial.readline().decode('utf-8').strip()
                if "ARDUINO_READY" in line:
                    logger.info("Arduino connection established successfully")
                    return True
            time.sleep(0.1)
        
        logger.warning("Arduino ready signal not received, but continuing...")
        return True
        
    except serial.SerialException as e:
        logger.error(f"Failed to connect to Arduino: {e}")
        arduino_serial = None
        return False
    except Exception as e:
        logger.error(f"Unexpected error connecting to Arduino: {e}")
        arduino_serial = None
        return False


def send_command_to_arduino(command: str) -> Dict[str, any]:
    """
    Send command to Arduino via serial and wait for response.
    Returns dict with status and response.
    """
    global last_command_time
    
    if not arduino_serial or not arduino_serial.is_open:
        logger.error("Arduino not connected")
        return {"status": "error", "message": "Arduino not connected"}
    
    try:
        # Send command
        command_bytes = (command + "\n").encode('utf-8')
        arduino_serial.write(command_bytes)
        arduino_serial.flush()
        
        last_command_time = time.time()
        logger.info(f"Sent command to Arduino: {command}")
        
        # Wait for response (with timeout)
        start_time = time.time()
        response = ""
        while time.time() - start_time < config.SERIAL_TIMEOUT:
            if arduino_serial.in_waiting > 0:
                line = arduino_serial.readline().decode('utf-8').strip()
                if line:
                    response = line
                    break
            time.sleep(0.05)
        
        if response:
            logger.debug(f"Arduino response: {response}")
            if response.startswith("OK:"):
                return {"status": "success", "response": response}
            elif response.startswith("ERROR:"):
                return {"status": "error", "response": response}
        
        return {"status": "success", "response": "Command sent (no response)"}
        
    except serial.SerialException as e:
        logger.error(f"Serial communication error: {e}")
        return {"status": "error", "message": f"Serial error: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error sending command: {e}")
        return {"status": "error", "message": f"Unexpected error: {e}"}


def connection_monitor():
    """
    Background thread to monitor connection and implement failsafe.
    Stops robot if no commands received for too long.
    """
    global monitor_running, last_command_time
    
    logger.info("Connection monitor started")
    
    while monitor_running:
        time.sleep(0.5)  # Check every 0.5 seconds
        
        if arduino_serial and arduino_serial.is_open:
            time_since_last_command = time.time() - last_command_time
            
            if time_since_last_command > config.COMMAND_TIMEOUT:
                # Send stop command as failsafe
                logger.warning(f"No command received for {time_since_last_command:.1f}s. Stopping robot.")
                send_command_to_arduino("STOP")
                last_command_time = time.time()  # Reset to prevent spam


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    arduino_status = "connected" if (arduino_serial and arduino_serial.is_open) else "disconnected"
    return jsonify({
        "status": "ok",
        "arduino": arduino_status,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/command', methods=['POST'])
def handle_command():
    """
    Receive movement commands via HTTP POST.
    Expected JSON: {"command": "FORWARD|BACKWARD|LEFT|RIGHT|STOP", "token": "auth_token"}
    """
    global last_command_time
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
        
        # Check authentication token
        token = data.get('token', '')
        if token != config.AUTH_TOKEN:
            logger.warning(f"Invalid token attempt from {request.remote_addr}")
            return jsonify({"status": "error", "message": "Invalid authentication token"}), 401
        
        # Get command
        command = data.get('command', '').upper().strip()
        
        if not command:
            return jsonify({"status": "error", "message": "No command provided"}), 400
        
        # Validate command
        valid_commands = ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'STOP', 'FWD', 'BWD', 'REVERSE']
        if command not in valid_commands:
            return jsonify({"status": "error", "message": f"Invalid command: {command}"}), 400
        
        # Send command to Arduino
        result = send_command_to_arduino(command)
        
        if result["status"] == "success":
            logger.info(f"Command executed: {command}")
            return jsonify({
                "status": "success",
                "command": command,
                "arduino_response": result.get("response", "")
            }), 200
        else:
            logger.error(f"Command failed: {command} - {result.get('message', '')}")
            return jsonify({
                "status": "error",
                "message": result.get("message", "Command execution failed")
            }), 500
            
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """Get current robot status."""
    arduino_connected = arduino_serial and arduino_serial.is_open
    time_since_last_command = time.time() - last_command_time if last_command_time > 0 else 0
    
    return jsonify({
        "arduino_connected": arduino_connected,
        "time_since_last_command": round(time_since_last_command, 2),
        "timestamp": datetime.now().isoformat()
    })


def main():
    """Main function to start the server."""
    global connection_monitor_thread, monitor_running
    
    logger.info("Starting Police Robot Dog Control Server")
    logger.info(f"Server will listen on {config.SERVER_HOST}:{config.SERVER_PORT}")
    
    # Connect to Arduino
    if not connect_arduino():
        logger.error("Failed to connect to Arduino. Server will start but commands will fail.")
        logger.error("Check Arduino connection and port configuration in config.py")
    
    # Start connection monitor thread
    monitor_running = True
    connection_monitor_thread = threading.Thread(target=connection_monitor, daemon=True)
    connection_monitor_thread.start()
    
    # Start Flask server
    try:
        app.run(
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            debug=False,  # Set to False in production
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        monitor_running = False
        if arduino_serial and arduino_serial.is_open:
            send_command_to_arduino("STOP")
            arduino_serial.close()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()

