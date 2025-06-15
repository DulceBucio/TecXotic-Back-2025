#include "Arduino.h"
#include "heltec.h"
#include <Wire.h>
#include "MS5837.h"
#include "WiFi.h"
#include <HTTPClient.h>
#include <time.h>

// Pines
#define IN1 5 // Compresor adelante
#define IN2 6 // Compresor reversa
#define IN3 7 // Válvula
#define FLOAT_STATE_PIN 4 // 1 = surface, 0 = underwater

// Sensor
MS5837 sensor;

// Flags
bool floatSetupActive = false;
bool floatTaskActive = false;
bool floatFirstSequence = true;
bool isUnderwater = false;
bool lastFloatState = true; 
unsigned long lastStateChange = 0;
const unsigned long STATE_DEBOUNCE_TIME = 2000; 
bool sensorState = false;

// Data storage
const int MAX_DATA_ENTRIES = 100; 
String dataEntries[MAX_DATA_ENTRIES];
int dataCount = 0;
String company_name = "EX 22";

// Time config
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;
const int daylightOffset_sec = 0;

// WiFi
const char* ssid = "dultez";
const char* password = "Dultez04";
const char* serverURL = "http://172.20.10.14:8080";


/* FUNCIONES PARA SUBIR/BAJAR BOYA*/

void float_first_sequence() {
  // dejamos caer por unos segundos, pero mientras guardamos datos
  Serial.println("entra aquí");
  storeSensorData();
  delay(10000);

  // volvemos a subir para mandar datos
  float_setup();
  Serial.println("sube");
  sendAllStoredData();
  floatFirstSequence = false;

}
void float_setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(FLOAT_STATE_PIN, INPUT_PULLUP);

  // INFLAR
  digitalWrite(IN1, HIGH);
  digitalWrite(IN3, HIGH);  
  digitalWrite(IN2, LOW);

  floatSetupActive = true;
}

void float_task() {  
  Serial.println("baja");
  isUnderwater = true;

  // Apagar IN1 y IN3, prender IN2 (reversa compresor)
  digitalWrite(IN1, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN2, HIGH);

  delay(3000);  // Simula inversión, espera 3 segundos
  digitalWrite(IN2, LOW);

  unsigned long holdStart = millis();
  unsigned long lastStore = millis();
  const float targetDepth = 2.5;
  const int holdDuration = 45000;

  while (millis() - holdStart < holdDuration) {
    // almacenar datos cada 5 seg
    if (millis() - lastStore >= 5000) {
      storeSensorData();
      lastStore = millis();
    }
    // // Lectura real del sensor
    // sensor.read();
    // float currentDepth = sensor.depth();

    // // Depth control logic
    // if (abs(currentDepth - targetDepth) > 0.1) {
    //   digitalWrite(IN1, HIGH);
    //   digitalWrite(IN3, HIGH);
    // } else {
    //   digitalWrite(IN1, LOW);
    //   digitalWrite(IN3, LOW);
    // }

    delay(100);
  }

  //
  Serial.println("sube de nuevo?");
  unsigned long surfaceStart = millis();
  const unsigned long MAX_SURFACE_TIME = 15000;

  while(millis() - surfaceStart < MAX_SURFACE_TIME) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN3, HIGH);
    if (millis() - lastStore >= 5000) {
      storeSensorData();
      lastStore = millis();
    }
  }
    
  digitalWrite(IN1, LOW);
  digitalWrite(IN3, LOW);

  isUnderwater = false;
  Serial.println("[FINALIZADO] Secuencia de flotación completada.");
  floatTaskActive = false;
  floatSetupActive = true;
  
  sendAllStoredData();
}

/* FUNCIONES PARA EL MANEJO DE COMANDOS*/
String checkForCommands() {
  HTTPClient http;
  http.begin(String(serverURL) + "/get_command");
  http.setTimeout(5000); // 5 second timeout
  
  int httpResponseCode = http.GET();
  String command = "";
  
  if (httpResponseCode == 200) {
    String response = http.getString();
    int commandStart = response.indexOf("\"command\":\"");
    if (commandStart != -1) {
      commandStart += 11; // Move past "command":"
      int commandEnd = response.indexOf("\"", commandStart);
      if (commandEnd != -1) {
        command = response.substring(commandStart, commandEnd);
        processCommand(command);
      }
    }
  }
  
  http.end();
  return command;
}

void processCommand(String command) {  
  if (command == "start" && !floatTaskActive) {
    // if (digitalRead(FLOAT_STATE_PIN) == HIGH) {
    //   floatSetupActive = false;
    //   floatTaskActive = true;
    //   Serial.println("[CMD] vamos abajo");
    // } else {
    //   Serial.println("[CMD]estamos abajo");
    // }
    floatSetupActive = false;
    floatTaskActive = true;
    float_task();
  } else if (command == "send_data") {
    sendAllStoredData();
  } else if (command == "clear_data") {
    clearStoredData();
  }
}

void WIFISetUp() {
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(ssid, password);
  delay(100);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
}

void storeSensorData() {
  Serial.println("guardando datos");

  if (!sensorState) {
    Serial.println("[ERROR] Sensor read failed.");
    return;
  }

  if (dataCount >= MAX_DATA_ENTRIES) {
    for (int i = 0; i < MAX_DATA_ENTRIES - 1; i++) {
      dataEntries[i] = dataEntries[i + 1];
    }
    dataCount = MAX_DATA_ENTRIES - 1;
  }

  struct tm timeinfo;
  String timestamp = "UNKNOWN_TIME";
  if (getLocalTime(&timeinfo)) {
    char timeStr[30];
    strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
    timestamp = String(timeStr);
  }

  float pressure = sensor.pressure();
  float depth = sensor.depth();

  String dataEntry = company_name + "," + 
                    timestamp + "," +
                    String(pressure, 2) + "," +
                    String(depth, 2); 

  dataEntries[dataCount++] = dataEntry;
}


void sendAllStoredData() {
  Serial.println("mandando todo");
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  if (dataCount == 0) {
    return;
  }

  // Prepare data packet
  String dataPacket = "";
  for (int i = 0; i < dataCount; i++) {
    dataPacket += dataEntries[i];
    if (i < dataCount - 1) {
      dataPacket += "\n";
    }
  }

  HTTPClient http;
  http.begin(String(serverURL) + "/upload");
  http.addHeader("Content-Type", "text/plain");
  http.setTimeout(10000); 
  
  int httpResponseCode = http.POST(dataPacket);
  Serial.println("[SEND] HTTP Response: " + String(httpResponseCode));
  
  if (httpResponseCode == 200) {
    clearStoredData();
  } else {
    Serial.println("[SEND] Failed to send data, keeping local copy");
    String response = http.getString();
    Serial.println("[SEND] Error response: " + response);
  }

  http.end();
}

void clearStoredData() {
  for (int i = 0; i < dataCount; i++) {
    dataEntries[i] = "";
  }
  dataCount = 0;
  Serial.println("[STORAGE] All stored data cleared");
}

void reconnectWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Attempting to reconnect...");
    WiFi.disconnect();
    delay(1000);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println(" Reconnected!");
    } else {
      Serial.println(" Failed to reconnect!");
    }
  }
}

bool checkFloatStateChange() {
  bool currentState = digitalRead(FLOAT_STATE_PIN);
  
  if (currentState != lastFloatState) {
    if (millis() - lastStateChange > STATE_DEBOUNCE_TIME) {
      Serial.println("[FLOAT_STATE] Changed from " + String(lastFloatState ? "SURFACE" : "UNDERWATER") + 
                    " to " + String(currentState ? "SURFACE" : "UNDERWATER"));
      
      lastFloatState = currentState;
      lastStateChange = millis();
      
      isUnderwater = !currentState;
      
      if (currentState && dataCount > 0 && WiFi.status() == WL_CONNECTED) {
        Serial.println("[AUTO_SEND] Just surfaced with data - attempting to send...");
        sendAllStoredData();
      }
      
      return true; 
    }
  } else {
    lastStateChange = millis();
  }
  
  return false; 
}

void setup() {
  // setup de sensores y de cosas
  Heltec.begin(false, false, true);
  Wire.begin(SDA_OLED, SCL_OLED); // 17 & 18
  Serial.begin(115200); 
  Serial.println("[INIT] Starting Float Controller...");

  while (!sensor.init()) {
    Serial.println("[INIT] Sensor init failed!");
    Serial.println("[INIT] Check SDA/SCL connections");
    Serial.println("[INIT] Blue Robotics Bar30: White=SDA, Green=SCL");
    sensorState = false;
    delay(5000);
  }

  sensorState = true;

  Serial.println("[INIT] Sensor initialized successfully");
  sensor.setFluidDensity(1000); 

  WIFISetUp();
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  Serial.print("[INIT] Waiting for time sync");
  int timeAttempts = 0;
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo) && timeAttempts < 10) {
    delay(1000);
    Serial.print(".");
    timeAttempts++;
  }

  if (getLocalTime(&timeinfo)) {
    Serial.println(" Time synced!");
  } else {
    Serial.println(" Time sync failed, continuing anyway");
  }

  Serial.println("[INIT] Setup complete");
}

void loop() {
  checkFloatStateChange();
  
  static unsigned long lastWiFiCheck = 0;
  if (millis() - lastWiFiCheck > 30000) {
    reconnectWiFi();
    lastWiFiCheck = millis();
  }

  if (floatFirstSequence) {
    float_first_sequence();
  }
  
  while(floatSetupActive) {
    checkForCommands();
    delay(2000);
  }

  delay(1000);
}