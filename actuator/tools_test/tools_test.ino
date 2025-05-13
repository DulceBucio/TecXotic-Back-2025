#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);

// Initial servo positions
int servoClaw = 325;
int servoRoll = 450;

// Limits
#define SERVOCLAWMIN  310
#define SERVOCLAWMAX  350

#define SERVOROLLMIN  300
#define SERVOROLLMAX  600

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
  board1.setPWM(0, 0, servoRoll);
  board1.setPWM(14, 0, servoClaw);
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
      servoClaw = 325;
      board1.setPWM(15, 0, servoClaw);
    } 
    else if (cmd == 4) { // CLAW OPEN
      clawing = true;
      clawDirection = 1;
    } 
    else if (cmd == 5) { // CLAW CLOSE
      clawing = true;
      clawDirection = -1;
    } 
    else if (cmd >= 0 && cmd <= 180) {
      // Map angle (0-180) to pulse width for servoRoll
      int pwm = map(cmd, 0, 180, SERVOROLLMIN, SERVOROLLMAX);
      rolling = false;
      servoRoll = pwm;
      board1.setPWM(0, 0, servoRoll);
    }
  }

  // Handle rolling
  if (rolling) {
    servoRoll += 5 * rollDirection;
    servoRoll = constrain(servoRoll, SERVOROLLMIN, SERVOROLLMAX);
    board1.setPWM(0, 0, servoRoll);
  }

  // Handle clawing
  if (clawing) {
    servoClaw += 5 * clawDirection;
    servoClaw = constrain(servoClaw, SERVOCLAWMIN, SERVOCLAWMAX);
    board1.setPWM(14, 0, servoClaw);
  }

  delay(200); // Adjust this to control movement speed
}
