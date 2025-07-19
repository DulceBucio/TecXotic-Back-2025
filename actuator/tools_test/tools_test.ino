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
      rolling = true;
      rollDirection = -1;
    } 
    else if (cmd == 2) { // RIGHTROLL
      rolling = true;
      rollDirection = 1;
    } 
    else if (cmd == 3) { // CLAW MID
      clawing = false;
      servoClaw1 = 325;
      board1.setPWM(servoClaw1Pin, 0, servoClaw1);
    } 
    else if (cmd == 4) { // CLAW1 OPEN
      clawing = true;
      clawDirection = 1;
    } 
    else if (cmd == 5) { // CLAW1 CLOSE
      clawing = true;
      clawDirection = -1;
    } else if (cmd >= 0 && cmd <= 180) {
      // Map angle (0-180) to pulse width for servoRoll
      int pwm = map(cmd, 0, 180, SERVOROLLMIN, SERVOROLLMAX);
      rolling = false;
      servoRoll = pwm;
      board1.setPWM(servoRollPin, 0, servoRoll);
    }
  }

  // Handle rolling
  if (rolling) {
    servoRoll += 5 * rollDirection;
    servoRoll = constrain(servoRoll, SERVOROLLMIN, SERVOROLLMAX);
    board1.setPWM(servoRollPin, 0, servoRoll);
  }

  // Handle clawing 1
  if (clawing) {
    servoClaw1 += 5 * clawDirection;
    servoClaw1 = constrain(servoClaw1, SERVOCLAW1MIN, SERVOCLAW1MAX);
    board1.setPWM(servoClaw1Pin, 0, servoClaw1);
  }
  delay(200); // Adjust this to control movement speed
}