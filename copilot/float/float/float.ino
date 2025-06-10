#include "Arduino.h"
#include "heltec.h"
#include <Wire.h>
// #include "MS5837.h"
#include "WiFi.h"
#include <HTTPClient.h>

// MS5837 sensor;
void checkForCommands() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://172.20.10.14:8080/get_command");
    
    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("Command received: " + response);
      
      if (response.indexOf("\"command\":null") == -1) {
        int start = response.indexOf("\"command\":\"") + 11;
        int end = response.indexOf("\"", start);
        String command = response.substring(start, end);
        
        processCommand(command);
      }
    }
    http.end();
  }
}

void processCommand(String command) {
  Serial.println("Processing command: " + command);
  
  if (command == "reset") {
    ESP.restart();
  } else if (command == "status") {
    Serial.println("ESP32 is running normally");
  } else if (command.startsWith("delay:")) {
    // Example: "delay:10000" to change delay
    int newDelay = command.substring(6).toInt();
    Serial.println("Setting new delay: " + String(newDelay));
    // You'd need to implement variable delay logic
  }
  // Add more commands as needed
}

void WIFISetUp(void)
{
	WiFi.disconnect(true);
	delay(100);
	WiFi.mode(WIFI_STA);
	WiFi.setAutoReconnect(true);
	WiFi.begin("dultez","Dultez04");
	delay(100);
  Serial.print("Connecting...");
	byte count = 0;
	while(WiFi.status() != WL_CONNECTED && count < 10)
	{
		count ++;
		delay(500);
	}

	if(WiFi.status() == WL_CONNECTED)
	{
		Serial.println("OK");
	}
	else
	{
		Serial.println("Failed");
	}
	Serial.println("WIFI Setup done");
	delay(500);
}

void setup()
{
	Heltec.begin(true, false, true);
	// Wire.begin(SDA_OLED, SCL_OLED); // 17 & 18
	Serial.begin(9600);
	Serial.println("Starting");
 	// while (!sensor.init()) {
  //   Serial.println("Init failed!");
  //   Serial.println("Are SDA/SCL connected correctly?");
  //   Serial.println("Blue Robotics Bar30: White=SDA, Green=SCL");
  //   Serial.println("\n\n\n");
  //   delay(5000);
  // }

  WIFISetUp();
  // sensor.setFluidDensity(997); 

}

void loop()
{
  // Serial.println("Reading sensor...");
  // sensor.read();

  // float pressure = sensor.pressure();
  // float temperature = sensor.temperature();
  // float depth = sensor.depth();
  // float altitude = sensor.altitude();

  float pressure = 1.0;
  float temperature = 2.0;
  float depth = 3.0;
  float altitude = 4.0;

  String data = "Pressure: " + String(pressure) + " mbar\n" +
                "Temperature: " + String(temperature) + " °C\n" +
                "Depth: " + String(depth) + " m\n" +
                "Altitude: " + String(altitude) + " m\n";



  Serial.println("[SENDING DATA]");
  Serial.println(data);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://172.20.10.14:8080/upload"); 
    http.addHeader("Content-Type", "text/plain");

    int httpResponseCode = http.POST(data);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  static int commandCheckCounter = 0;
  if (commandCheckCounter % 5 == 0) {
    checkForCommands();
  }
  commandCheckCounter++;

  delay(6000); // Delay between readings
}

