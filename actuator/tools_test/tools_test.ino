#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);

#define SERVOMIN  310
#define SERVOMAX  350

void setup() {
  Serial.begin(9600);
  board1.begin();
  board1.setPWMFreq(60);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); 
    int angle = command.toInt();

    board1.setPWM(15, 0, angle);
  }
}
