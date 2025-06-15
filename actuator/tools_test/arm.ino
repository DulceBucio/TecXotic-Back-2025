#include <Servo.h>

// Crear objetos para cada servo
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

// Definir los pines para los potenciómetros
const int potPin1 = A0;
const int potPin2 = A1;
const int potPin3 = A2;
const int potPin4 = A4;

// Definir los pines para los servos
const int servoPin1 = 9;
const int servoPin2 = 10;
const int servoPin3 = 11;
const int servoPin4 = 12;

int minValue1 = 177;  // Rango mínimo del potenciómetro 1
int maxValue1 = 860;  // Rango máximo del potenciómetro 1

int minValue2 = 180;  // Rango mínimo del potenciómetro 2
int maxValue2 = 860;  // Rango máximo del potenciómetro 2

int minValue3 = 145;  // Rango mínimo del potenciómetro 3
int maxValue3 = 880;  // Rango máximo del potenciómetro 3

int minValue4 = 0;  // Rango mínimo del potenciómetro 4
int maxValue4 = 1023;  // Rango máximo del potenciómetro 4


void setup() {
  Serial.begin(9600);
  
  // Asignar los pines de los servos
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
}

void loop() {
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

  delay(100);
}