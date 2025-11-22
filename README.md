# Police Robot Dog Remote Control System

Remote control system for a robot dog using Raspberry Pi 4B and Arduino Mega 2560.

## Hardware Components

- **Raspberry Pi 4B** - Main controller and server
- **Arduino Mega 2560** - Motor controller
- **4x DC Motors** - For robot movement (or servos)
- **L298N Motor Driver** (or similar) - Motor control board
- **USB Webcam** - 1080p for live video streaming
- **Jumper Wires** - For Arduino connections
- **Power Supply** - For motors and Arduino

## System Architecture

```
[Control Device] --Wi-Fi--> [Raspberry Pi] --Serial/USB--> [Arduino] --> [Motors]
                                    |
                                    |
                              [USB Webcam]
```

## Setup Instructions

### 1. Arduino Setup

#### Upload Firmware
1. Connect Arduino Mega 2560 to your computer via USB
2. Open Arduino IDE
3. Open `arduino_motor.ino`
4. Select board: **Tools > Board > Arduino Mega 2560**
5. Select port: **Tools > Port > [your Arduino port]**
6. Click **Upload**

#### Wiring Diagram (L298N Motor Driver)

**Motor Pin Connections:**
```
Arduino Mega 2560    L298N Motor Driver
-----------------    -------------------
Pin 2  ----------->  Right Rear IN1
Pin 3  ----------->  Right Rear IN2
Pin 4  ----------->  Left Rear IN1
Pin 5  ----------->  Left Rear ENA (PWM)
Pin 6  ----------->  Right Rear ENA (PWM)
Pin 7  ----------->  Left Front IN2
Pin 8  ----------->  Left Front IN1
Pin 9  ----------->  Left Front ENA (PWM)
Pin 10 ----------->  Right Front ENA (PWM)
Pin 11 ----------->  Right Front IN2
Pin 12 ----------->  Right Front IN1
Pin 13 ----------->  Right Rear IN2 (alternative)
```

**L298N Connections:**
- **VCC** → 5V (Arduino or external)
- **GND** → GND (common ground)
- **Motor A** → Left Front Motor
- **Motor B** → Right Front Motor
- **Motor C** → Left Rear Motor
- **Motor D** → Right Rear Motor
- **12V Power** → External 12V supply (for motors)

**Note:** Adjust pin numbers in `arduino_motor.ino` if your wiring differs.

### 2. Raspberry Pi Setup

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install required Python packages
pip3 install -r requirements.txt

# Install serial communication library (if needed)
sudo apt install python3-serial -y
```

#### Configure Settings
1. Edit `config.py`:
   ```python
   # Set your Wi-Fi credentials
   WIFI_SSID = "YourWiFiName"
   WIFI_PASSWORD = "YourWiFiPassword"
   
   # Arduino port (will auto-detect, but you can set manually)
   ARDUINO_PORT = "/dev/ttyACM0"  # Common on Raspberry Pi
   
   # Change security token
   AUTH_TOKEN = "your_secure_random_token_here"
   ```

2. Connect Arduino to Raspberry Pi via USB cable

3. Verify Arduino connection:
   ```bash
   ls /dev/ttyACM*  # Should show /dev/ttyACM0 or similar
   ```

#### Run the Server
```bash
# Make script executable
chmod +x pi_main.py

# Run the server
python3 pi_main.py
```

The server will start on port 5000. You should see:
```
INFO - Starting Police Robot Dog Control Server
INFO - Server will listen on 0.0.0.0:5000
INFO - Found Arduino at: /dev/ttyACM0
INFO - Arduino connection established successfully
INFO - Connection monitor started
 * Running on http://0.0.0.0:5000
```

## API Endpoints

### 1. Health Check
```bash
GET http://raspberry-pi-ip:5000/health
```

**Response:**
```json
{
  "status": "ok",
  "arduino": "connected",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Send Command
```bash
POST http://raspberry-pi-ip:5000/command
Content-Type: application/json

{
  "command": "FORWARD",
  "token": "robot_dog_secure_token_2024"
}
```

**Valid Commands:**
- `FORWARD` or `FWD` - Move forward
- `BACKWARD` or `BWD` or `REVERSE` - Move backward
- `LEFT` - Turn left (pivot)
- `RIGHT` - Turn right (pivot)
- `STOP` - Stop all motors

**Response:**
```json
{
  "status": "success",
  "command": "FORWARD",
  "arduino_response": "OK:FORWARD"
}
```

### 3. Get Status
```bash
GET http://raspberry-pi-ip:5000/status
```

**Response:**
```json
{
  "arduino_connected": true,
  "time_since_last_command": 1.23,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Testing

### Test 1: Arduino Serial Communication
1. Upload `arduino_motor.ino` to Arduino
2. Open Arduino Serial Monitor (9600 baud)
3. Send commands: `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP`
4. Verify motors respond correctly

### Test 2: Raspberry Pi → Arduino
1. Connect Arduino to Raspberry Pi via USB
2. Run `pi_main.py`
3. Check logs for "Arduino connection established"
4. Use curl to test:
   ```bash
   curl -X POST http://localhost:5000/command \
     -H "Content-Type: application/json" \
     -d '{"command": "FORWARD", "token": "robot_dog_secure_token_2024"}'
   ```

### Test 3: Remote Control
1. Find Raspberry Pi IP address:
   ```bash
   hostname -I
   ```
2. From another device on the same network:
   ```bash
   curl -X POST http://192.168.1.100:5000/command \
     -H "Content-Type: application/json" \
     -d '{"command": "FORWARD", "token": "robot_dog_secure_token_2024"}'
   ```

### Test 4: Failsafe
1. Send a command to move the robot
2. Wait 2+ seconds without sending another command
3. Robot should automatically stop (failsafe activated)

## Troubleshooting

### Arduino Not Found
- Check USB connection
- Verify port: `ls /dev/ttyACM*` or `ls /dev/ttyUSB*`
- Update `ARDUINO_PORT` in `config.py`
- Check permissions: `sudo usermod -a -G dialout $USER` (logout/login)

### Motors Not Moving
- Verify motor wiring matches pin definitions
- Check power supply to L298N (12V for motors)
- Test motors directly with Arduino Serial Monitor
- Verify motor speed setting in `arduino_motor.ino` (MOTOR_SPEED)

### Connection Timeout
- Check Wi-Fi connection on Raspberry Pi
- Verify firewall allows port 5000: `sudo ufw allow 5000`
- Check server logs for errors

### Commands Not Working
- Verify authentication token matches in request and `config.py`
- Check Arduino serial connection in logs
- Test Arduino directly with Serial Monitor first

## Safety Features

1. **Failsafe Timeout**: Robot stops automatically if no command received for 2 seconds
2. **Authentication**: All commands require valid token
3. **Command Validation**: Only valid commands are processed
4. **Error Logging**: All errors logged to `robot_dog.log`

## File Structure

```
Robo/
├── config.py              # Configuration settings
├── arduino_motor.ino      # Arduino motor control firmware
├── pi_main.py            # Raspberry Pi server
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── robot_dog.log        # Log file (created at runtime)
```

## Next Steps

- [ ] Add webcam video streaming (MJPEG)
- [ ] Implement WebSocket for lower latency
- [ ] Add speed control commands
- [ ] Add sensor integration (ultrasonic, IMU)
- [ ] Create mobile/web control interface
- [ ] Add autonomous behavior modes

## License

This project is for educational and law enforcement use.

