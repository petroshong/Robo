/*
 * Police Robot Dog - Arduino Motor Control
 * OSOYOO FlexiRover Configuration
 * Arduino Mega 2560
 * 
 * Receives serial commands and controls motors
 * Commands: FORWARD, BACKWARD, LEFT, RIGHT, STOP
 * 
 * Motor Configuration:
 * - Front Right: pins 22, 24, PWM 9
 * - Front Left: pins 26, 28, PWM 10
 * - Rear Right: pins 5, 6, PWM 11
 * - Rear Left: pins 7, 8, PWM 12
 * - Pin 49: Set HIGH (5V output)
 */

// Front Right Motor
const int RIGHT_FRONT_DIR1 = 22;
const int RIGHT_FRONT_DIR2 = 24;
const int RIGHT_FRONT_PWM = 9;

// Front Left Motor
const int LEFT_FRONT_DIR1 = 26;
const int LEFT_FRONT_DIR2 = 28;
const int LEFT_FRONT_PWM = 10;

// Rear Right Motor
const int RIGHT_REAR_DIR1 = 5;
const int RIGHT_REAR_DIR2 = 6;
const int RIGHT_REAR_PWM = 11;

// Rear Left Motor
const int LEFT_REAR_DIR1 = 7;
const int LEFT_REAR_DIR2 = 8;
const int LEFT_REAR_PWM = 12;

// Special pin
const int PIN_49 = 49;

// Motor speed (PWM: 0-255)
const int MOTOR_SPEED = 150;

// Failsafe: stop motors if no command received within this time (milliseconds)
const unsigned long FAILSAFE_TIMEOUT = 2000;  // 2 seconds
unsigned long lastCommandTime = 0;

// Serial command buffer
const int MAX_COMMAND_LENGTH = 50;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  Serial.setTimeout(100);
  
  // Set pin 49 HIGH (5V output)
  pinMode(PIN_49, OUTPUT);
  digitalWrite(PIN_49, HIGH);
  
  // Initialize motor pins as outputs
  pinMode(RIGHT_FRONT_DIR1, OUTPUT);
  pinMode(RIGHT_FRONT_DIR2, OUTPUT);
  pinMode(RIGHT_FRONT_PWM, OUTPUT);
  
  pinMode(LEFT_FRONT_DIR1, OUTPUT);
  pinMode(LEFT_FRONT_DIR2, OUTPUT);
  pinMode(LEFT_FRONT_PWM, OUTPUT);
  
  pinMode(RIGHT_REAR_DIR1, OUTPUT);
  pinMode(RIGHT_REAR_DIR2, OUTPUT);
  pinMode(RIGHT_REAR_PWM, OUTPUT);
  
  pinMode(LEFT_REAR_DIR1, OUTPUT);
  pinMode(LEFT_REAR_DIR2, OUTPUT);
  pinMode(LEFT_REAR_PWM, OUTPUT);
  
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
    command.trim();
    command.toUpperCase();
    
    if (command.length() > 0 && command.length() < MAX_COMMAND_LENGTH) {
      processCommand(command);
      lastCommandTime = millis();
    }
  }
  
  // Failsafe: stop motors if no command received for too long
  if (millis() - lastCommandTime > FAILSAFE_TIMEOUT) {
    stopAllMotors();
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
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(command);
  }
}

// Motor control functions
void moveForward() {
  // All motors forward
  // Front Right: forward works (LOW, HIGH)
  setMotor(RIGHT_FRONT_DIR1, RIGHT_FRONT_DIR2, RIGHT_FRONT_PWM, LOW, HIGH, MOTOR_SPEED);
  // Front Left: forward doesn't work - REVERSED (HIGH, LOW)
  setMotor(LEFT_FRONT_DIR1, LEFT_FRONT_DIR2, LEFT_FRONT_PWM, HIGH, LOW, MOTOR_SPEED);
  // Rear motors: REVERSED (HIGH, LOW)
  setMotor(RIGHT_REAR_DIR1, RIGHT_REAR_DIR2, RIGHT_REAR_PWM, HIGH, LOW, MOTOR_SPEED);
  setMotor(LEFT_REAR_DIR1, LEFT_REAR_DIR2, LEFT_REAR_PWM, HIGH, LOW, MOTOR_SPEED);
}

void moveBackward() {
  // All motors backward
  // Front Right: backward doesn't work - REVERSED (HIGH, LOW)
  setMotor(RIGHT_FRONT_DIR1, RIGHT_FRONT_DIR2, RIGHT_FRONT_PWM, HIGH, LOW, MOTOR_SPEED);
  // Front Left: backward works (LOW, HIGH)
  setMotor(LEFT_FRONT_DIR1, LEFT_FRONT_DIR2, LEFT_FRONT_PWM, LOW, HIGH, MOTOR_SPEED);
  // Rear motors: REVERSED (LOW, HIGH)
  setMotor(RIGHT_REAR_DIR1, RIGHT_REAR_DIR2, RIGHT_REAR_PWM, LOW, HIGH, MOTOR_SPEED);
  setMotor(LEFT_REAR_DIR1, LEFT_REAR_DIR2, LEFT_REAR_PWM, LOW, HIGH, MOTOR_SPEED);
}

void turnLeft() {
  // Left motors backward, right motors forward (pivot turn)
  // Front Right: forward (LOW, HIGH)
  setMotor(RIGHT_FRONT_DIR1, RIGHT_FRONT_DIR2, RIGHT_FRONT_PWM, LOW, HIGH, MOTOR_SPEED);
  // Front Left: backward (LOW, HIGH)
  setMotor(LEFT_FRONT_DIR1, LEFT_FRONT_DIR2, LEFT_FRONT_PWM, LOW, HIGH, MOTOR_SPEED);
  // Rear Right: forward (HIGH, LOW - reversed)
  setMotor(RIGHT_REAR_DIR1, RIGHT_REAR_DIR2, RIGHT_REAR_PWM, HIGH, LOW, MOTOR_SPEED);
  // Rear Left: backward (LOW, HIGH - reversed)
  setMotor(LEFT_REAR_DIR1, LEFT_REAR_DIR2, LEFT_REAR_PWM, LOW, HIGH, MOTOR_SPEED);
}

void turnRight() {
  // Right motors backward, left motors forward (pivot turn)
  // Front Right: backward (HIGH, LOW - reversed)
  setMotor(RIGHT_FRONT_DIR1, RIGHT_FRONT_DIR2, RIGHT_FRONT_PWM, HIGH, LOW, MOTOR_SPEED);
  // Front Left: forward (HIGH, LOW - reversed)
  setMotor(LEFT_FRONT_DIR1, LEFT_FRONT_DIR2, LEFT_FRONT_PWM, HIGH, LOW, MOTOR_SPEED);
  // Rear Right: backward (LOW, HIGH - reversed)
  setMotor(RIGHT_REAR_DIR1, RIGHT_REAR_DIR2, RIGHT_REAR_PWM, LOW, HIGH, MOTOR_SPEED);
  // Rear Left: forward (HIGH, LOW - reversed)
  setMotor(LEFT_REAR_DIR1, LEFT_REAR_DIR2, LEFT_REAR_PWM, HIGH, LOW, MOTOR_SPEED);
}

void stopAllMotors() {
  // Stop all motors
  setMotor(RIGHT_FRONT_DIR1, RIGHT_FRONT_DIR2, RIGHT_FRONT_PWM, LOW, LOW, 0);
  setMotor(LEFT_FRONT_DIR1, LEFT_FRONT_DIR2, LEFT_FRONT_PWM, LOW, LOW, 0);
  setMotor(RIGHT_REAR_DIR1, RIGHT_REAR_DIR2, RIGHT_REAR_PWM, LOW, LOW, 0);
  setMotor(LEFT_REAR_DIR1, LEFT_REAR_DIR2, LEFT_REAR_PWM, LOW, LOW, 0);
}

// Helper function to control a single motor
// dir1, dir2: direction pins, pwm: PWM speed pin
// val1, val2: HIGH/LOW for direction, speed: 0-255 PWM value
void setMotor(int dir1, int dir2, int pwm, int val1, int val2, int speed) {
  digitalWrite(dir1, val1);
  digitalWrite(dir2, val2);
  analogWrite(pwm, speed);
}
