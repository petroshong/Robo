"""
Configuration file for Police Robot Dog Remote Control System
Modify these settings according to your hardware setup.
"""

# Wi-Fi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Arduino Serial Communication
ARDUINO_PORT = "/dev/cu.usbmodem1101"  # Detected Arduino Mega 2560
# On macOS: /dev/cu.usbmodem* or /dev/cu.usbserial*
# On Linux/Raspberry Pi: /dev/ttyACM0 or /dev/ttyUSB0
ARDUINO_BAUD_RATE = 9600  # Standard baud rate for Arduino communication
SERIAL_TIMEOUT = 1.0  # Timeout in seconds for serial reads

# Security Token (for future authentication)
AUTH_TOKEN = "robot_dog_secure_token_2024"  # Change this to a secure random string

# Server Configuration
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5000  # HTTP server port
COMMAND_TIMEOUT = 2.0  # Seconds before robot stops if no command received

# Webcam Configuration
WEBCAM_INDEX = 0  # Usually 0 for first USB webcam
WEBCAM_WIDTH = 1920  # 1080p width
WEBCAM_HEIGHT = 1080  # 1080p height
WEBCAM_FPS = 30  # Frames per second (may need to reduce for performance)

# Motor Configuration (adjust based on your hardware)
# Assuming 4 DC motors: Left Front, Right Front, Left Rear, Right Rear
MOTOR_PINS = {
    "left_front_enable": 9,   # PWM pin for speed control
    "left_front_in1": 8,
    "left_front_in2": 7,
    "right_front_enable": 10,
    "right_front_in1": 12,
    "right_front_in2": 11,
    "left_rear_enable": 5,
    "left_rear_in1": 4,
    "left_rear_in2": 3,
    "right_rear_enable": 6,
    "right_rear_in1": 2,
    "right_rear_in2": 13,
}

# Motor Speed Settings (0-255 for PWM)
MOTOR_SPEED_NORMAL = 150  # Normal movement speed
MOTOR_SPEED_SLOW = 100    # Slow movement
MOTOR_SPEED_FAST = 200    # Fast movement

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "robot_dog.log"

