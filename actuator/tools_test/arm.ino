#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);

// Initial servo positions
int servoClaw1 = 315;
int servoRoll = 210;

int servoRollPin = 0;
int servoClaw1Pin = 7;

// Limits
#define SERVOCLAW1MIN  310
#define SERVOCLAW1MAX  350

#define SERVOROLLMIN  80
#define SERVOROLLMAX  340

// Control flags
bool rolling = false;
int rollDirection = 0; // -1 for LEFT, 1 for RIGHT

bool clawing = false;
int clawDirection = 0; // -1 for CLOSE, 1 for OPEN


void setup() {
  Serial.begin(9600);
  board1.begin();
  board1.setPWMFreq(60);

  // Initialize positions
  board1.setPWM(servoRollPin, 0, servoRoll);
  board1.setPWM(servoClaw1Pin, 0, servoClaw1);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    int cmd = command.toInt();

    // Reset control flags
    if (cmd == 0) { // STOP
      rolling = false;
      clawing = false;
    } 
    else if (cmd == 1) { // LEFTROLL
      board1.setPWM(ServoRollPin, 0, SERVOROLLMIN)
    } 
    else if (cmd == 2) { // RIGHTROLL
      board1.setPWM(ServoRollPin, 0, SERVOROLLMAX)
    } 
    else if (cmd == 3) { // CLAW MID
      board1.setPWM(servoClaw1Pin, 0, servoClaw1);
    } 
    else if (cmd == 4) { // CLAW1 OPEN
      board1.setPWM(servoClaw1Pin, 0, SERVOCLAW1MAX);
    } 
    else if (cmd == 5) { // CLAW1 CLOSE
      board1.setPWM(servoClaw1Pin, 0, SERVOCLAW1MIN);
    } else if (cmd >= 0 && cmd <= 180) {
      // Map angle (0-180) to pulse width for servoRoll
      int pwm = map(cmd, 0, 180, SERVOROLLMIN, SERVOROLLMAX);
      rolling = false;
      servoRoll = pwm;
      board1.setPWM(servoRollPin, 0, servoRoll);
    }
  }
  delay(200); // Adjust this to control movement speed
}