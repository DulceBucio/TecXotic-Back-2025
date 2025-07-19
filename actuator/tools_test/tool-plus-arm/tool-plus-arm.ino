#include <Adafruit_PWMServoDriver.h>
#include <Servo.h>

/* PCA9685 */
Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);

/* Tool 1 (rov maker servos) */
// 0's
int servoClaw1 = 315;
int servoRoll = 210;

int servoRollPin = 0;
int servoClaw1Pin = 7;

// Limites
#define SERVOCLAW1MIN  310
#define SERVOCLAW1MAX  350

#define SERVOROLLMIN  80
#define SERVOROLLMAX  340

// Flags
bool rolling = false;
int rollDirection = 0; // -1 for LEFT, 1 for RIGHT

bool clawing = false;
int clawDirection = 0; // -1 for CLOSE, 1 for OPEN


/* ARM */
// Servos
Servo servo1;
Servo servo2; 
Servo servo3;
Servo servo4;

// Potenciometros (analógicos)
const int potPin1 = A0; // naranja blanco
const int potPin2 = A1; // full naranja
const int potPin3 = A2; // azul blanco
const int potPin4 = A4; // full azul

// Servos (rositas)
const int servoPin1 = 10;
const int servoPin2 = 6;
const int servoPin3 = 9;
const int servoPin4 = 11;

// Rangos
int minValue1 = 177;  // Rango mínimo del potenciómetro 1
int maxValue1 = 860;  // Rango máximo del potenciómetro 1

int minValue2 = 180;  // Rango mínimo del potenciómetro 2
int maxValue2 = 860;  // Rango máximo del potenciómetro 2

int minValue3 = 145;  // Rango mínimo del potenciómetro 3
int maxValue3 = 880;  // Rango máximo del potenciómetro 3

int minValue4 = 0;  // Rango mínimo del potenciómetro 4
int maxValue4 = 1023;  // Rango máximo del potenciómetro 4

// Lineal 
int pinLinealOpen = 2;
int pinLinealClose = 4;

// Flags 
bool opening = false;
bool closing = false;

void setup() {
  Serial.begin(9600);
  board1.begin(); 
  board1.setPWMFreq(60);

  // poner en sus 0's
  board1.setPWM(servoRollPin, 0, servoRoll);
  board1.setPWM(servoClaw1Pin, 0, servoClaw1);

  // asignar pines a servos rositas
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);

  // pines del brazo/motor lineal
  pinMode(pinLinealOpen, OUTPUT);
  pinMode(pinLinealClose, OUTPUT);
}

void loop() {

  handleArm();

  // Recibir comando desde la jetson por serial
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
    } else if (cmd == 6) {
      opening = true;
    } else if (cmd == 7) {
      closing = true;
    }else if (cmd >= 0 && cmd <= 180) {
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

  // Handle opening arm
  if (opening) {
    digitalWrite(pinLinealOpen, HIGH);
  }

  if (closing) {
    digitalWrite(pinLinealClose, HIGH);
  }
  delay(100); // Adjust this to control movement speed
}

void handleArm() {
  // Leer valores de los potenciómetros (0 a 1023)
  int potValue1 = analogRead(potPin1);
  int potValue2 = analogRead(potPin2);
  int potValue3 = analogRead(potPin3);
  int potValue4 = analogRead(potPin4);

  // Mapear los valores de los potenciómetros a ángulos de 0 a 180 grados
  int angle1 = map(potValue1, minValue1, maxValue1, 0, 180);
  int angle2 = map(potValue2, minValue2, maxValue2, 0, 180);
  int angle3 = map(potValue3, minValue3, maxValue3, 0, 180);
  int angle4 = map(potValue4, minValue4, maxValue4, 0, 180);

  // Mover los servos a las posiciones correspondientes
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);
  servo4.write(angle4);

  // Imprimir los ángulos de los servos
  Serial.print("Servo 1: ");
  Serial.print(angle1);
  Serial.print("°, Servo 2: ");
  Serial.print(angle2);
  Serial.print("°, Servo 3: ");
  Serial.print(angle3);
  Serial.print("°, Servo 4: ");
  Serial.println(angle4);

}
