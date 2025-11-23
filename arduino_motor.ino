/*
 * Police Robot Dog - Arduino Motor Control
 * OSOYOO FlexiRover Configuration
 * Arduino Mega 2560
 * 
 * Receives serial commands from Raspberry Pi and controls motors
 * Commands: FORWARD, BACKWARD, LEFT, RIGHT, STOP
 * 
 * Motor Setup (OSOYOO FlexiRover):
 * - 4 DC motors (Left Front, Right Front, Left Rear, Right Rear)
 * - Each motor uses: Direction pins (IN1, IN2), PWM pin (ENABLE)
 */

// Motor pin definitions (OSOYOO FlexiRover)
const int LEFT_FRONT_ENABLE = 10;   // PWM pin
const int LEFT_FRONT_IN1 = 26;       // Direction pin 1
const int LEFT_FRONT_IN2 = 28;       // Direction pin 2

const int RIGHT_FRONT_ENABLE = 9;   // PWM pin
const int RIGHT_FRONT_IN1 = 22;     // Direction pin 1
const int RIGHT_FRONT_IN2 = 24;     // Direction pin 2

const int LEFT_REAR_ENABLE = 12;    // PWM pin
const int LEFT_REAR_IN1 = 7;        // Direction pin 1
const int LEFT_REAR_IN2 = 8;        // Direction pin 2

const int RIGHT_REAR_ENABLE = 11;   // PWM pin
const int RIGHT_REAR_IN1 = 5;       // Direction pin 1
const int RIGHT_REAR_IN2 = 6;       // Direction pin 2

// Special pin
const int PIN_49 = 49;

// Motor speed (PWM: 0-255)
const int MOTOR_SPEED = 150;  // Adjust speed here (0-255)

// Failsafe: stop motors if no command received within this time (milliseconds)
const unsigned long FAILSAFE_TIMEOUT = 2000;  // 2 seconds
unsigned long lastCommandTime = 0;

// Serial command buffer
String commandBuffer = "";
const int MAX_COMMAND_LENGTH = 50;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  Serial.setTimeout(100);  // 100ms timeout for reading
  
  // Set pin 49 HIGH (5V output)
  pinMode(PIN_49, OUTPUT);
  digitalWrite(PIN_49, HIGH);
  
  // Initialize motor pins as outputs
  pinMode(LEFT_FRONT_ENABLE, OUTPUT);
  pinMode(LEFT_FRONT_IN1, OUTPUT);
  pinMode(LEFT_FRONT_IN2, OUTPUT);
  
  pinMode(RIGHT_FRONT_ENABLE, OUTPUT);
  pinMode(RIGHT_FRONT_IN1, OUTPUT);
  pinMode(RIGHT_FRONT_IN2, OUTPUT);
  
  pinMode(LEFT_REAR_ENABLE, OUTPUT);
  pinMode(LEFT_REAR_IN1, OUTPUT);
  pinMode(LEFT_REAR_IN2, OUTPUT);
  
  pinMode(RIGHT_REAR_ENABLE, OUTPUT);
  pinMode(RIGHT_REAR_IN1, OUTPUT);
  pinMode(RIGHT_REAR_IN2, OUTPUT);
  
  // Start with motors stopped
  stopAllMotors();
  
  // Initialize command time
  lastCommandTime = millis();
  
  // Send ready signal
  Serial.println("ARDUINO_READY");
  
  delay(1000);
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace
    command.toUpperCase();  // Convert to uppercase
    
    if (command.length() > 0 && command.length() < MAX_COMMAND_LENGTH) {
      processCommand(command);
      lastCommandTime = millis();  // Update last command time
    }
  }
  
  // Failsafe: stop motors if no command received for too long
  if (millis() - lastCommandTime > FAILSAFE_TIMEOUT) {
    stopAllMotors();
    // Optionally send status back
    // Serial.println("FAILSAFE_ACTIVATED");
  }
}

void processCommand(String command) {
  // Process movement commands
  if (command == "FORWARD" || command == "FWD") {
    moveForward();
    Serial.println("OK:FORWARD");
  }
  else if (command == "BACKWARD" || command == "BWD" || command == "REVERSE") {
    moveBackward();
    Serial.println("OK:BACKWARD");
  }
  else if (command == "LEFT") {
    turnLeft();
    Serial.println("OK:LEFT");
  }
  else if (command == "RIGHT") {
    turnRight();
    Serial.println("OK:RIGHT");
  }
  else if (command == "STOP") {
    stopAllMotors();
    Serial.println("OK:STOP");
  }
  else if (command == "STATUS" || command == "PING") {
    Serial.println("OK:STATUS");
  }
  // Individual motor test commands
  else if (command == "TEST_LF") {
    testMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, "LEFT_FRONT");
  }
  else if (command == "TEST_RF") {
    testMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, "RIGHT_FRONT");
  }
  else if (command == "TEST_LR") {
    testMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, "LEFT_REAR");
  }
  else if (command == "TEST_RR") {
    testMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, "RIGHT_REAR");
  }
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(command);
  }
}

// Motor control functions
void moveForward() {
  // All motors forward
  // Front Right: forward works (LOW, HIGH)
  setMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, LOW, HIGH, MOTOR_SPEED);
  // Front Left: forward fixed (HIGH, LOW)
  setMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, HIGH, LOW, MOTOR_SPEED);
  // Rear motors: REVERSED (HIGH, LOW)
  setMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, HIGH, LOW, MOTOR_SPEED);
  setMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, HIGH, LOW, MOTOR_SPEED);
}

void moveBackward() {
  // All motors backward
  // Front Right: backward fixed (HIGH, LOW)
  setMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, HIGH, LOW, MOTOR_SPEED);
  // Front Left: backward works (LOW, HIGH)
  setMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, LOW, HIGH, MOTOR_SPEED);
  // Rear motors: REVERSED (LOW, HIGH)
  setMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, LOW, HIGH, MOTOR_SPEED);
  setMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, LOW, HIGH, MOTOR_SPEED);
}

void turnLeft() {
  // Left motors backward, right motors forward (pivot turn)
  // Front Right: forward (LOW, HIGH)
  setMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, LOW, HIGH, MOTOR_SPEED);
  // Front Left: backward (LOW, HIGH)
  setMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, LOW, HIGH, MOTOR_SPEED);
  // Rear Right: forward (HIGH, LOW - reversed)
  setMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, HIGH, LOW, MOTOR_SPEED);
  // Rear Left: backward (LOW, HIGH - reversed)
  setMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, LOW, HIGH, MOTOR_SPEED);
}

void turnRight() {
  // Right motors backward, left motors forward (pivot turn)
  // Front Right: backward (HIGH, LOW - reversed)
  setMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, HIGH, LOW, MOTOR_SPEED);
  // Front Left: forward (HIGH, LOW - reversed)
  setMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, HIGH, LOW, MOTOR_SPEED);
  // Rear Right: backward (LOW, HIGH - reversed)
  setMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, LOW, HIGH, MOTOR_SPEED);
  // Rear Left: forward (HIGH, LOW - reversed)
  setMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, HIGH, LOW, MOTOR_SPEED);
}

void stopAllMotors() {
  // Stop all motors
  setMotor(LEFT_FRONT_IN1, LEFT_FRONT_IN2, LEFT_FRONT_ENABLE, LOW, LOW, 0);
  setMotor(RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, RIGHT_FRONT_ENABLE, LOW, LOW, 0);
  setMotor(LEFT_REAR_IN1, LEFT_REAR_IN2, LEFT_REAR_ENABLE, LOW, LOW, 0);
  setMotor(RIGHT_REAR_IN1, RIGHT_REAR_IN2, RIGHT_REAR_ENABLE, LOW, LOW, 0);
}

// Helper function to control a single motor
// in1, in2: direction pins, enable: PWM speed pin
// dir1, dir2: HIGH/LOW for direction, speed: 0-255 PWM value
void setMotor(int in1, int in2, int enable, int dir1, int dir2, int speed) {
  digitalWrite(in1, dir1);
  digitalWrite(in2, dir2);
  analogWrite(enable, speed);
}

// Test function for individual motors
void testMotor(int in1, int in2, int enable, String motorName) {
  Serial.print("Testing ");
  Serial.print(motorName);
  Serial.print(" (IN1=");
  Serial.print(in1);
  Serial.print(", IN2=");
  Serial.print(in2);
  Serial.print(", ENA=");
  Serial.print(enable);
  Serial.println(")");
  
  // Move forward for 1 second
  setMotor(in1, in2, enable, HIGH, LOW, MOTOR_SPEED);
  delay(1000);
  
  // Stop
  setMotor(in1, in2, enable, LOW, LOW, 0);
  delay(500);
  
  // Move backward for 1 second
  setMotor(in1, in2, enable, LOW, HIGH, MOTOR_SPEED);
  delay(1000);
  
  // Stop
  setMotor(in1, in2, enable, LOW, LOW, 0);
  
  Serial.print("OK:");
  Serial.println(motorName);
}
