#include <ESP8266WiFi.h>
#include <WiFiClient.h>

const char* ssid = "GNXS-2640A0";     // Replace with your WiFi SSID
const char* password = "22november"; // Replace with your WiFi password

WiFiServer server(12345);  // TCP server port


int whiteledPin = 2;
int greenledPin = 0;
int redledPin = 5; 
int blueledPin = 15;
int yellowledPin = 13;

void setup() {
  Serial.begin(9600);
  pinMode(whiteledPin, OUTPUT);
  pinMode(greenledPin, OUTPUT);
  pinMode(redledPin, OUTPUT);
  pinMode(blueledPin, OUTPUT);
  pinMode(yellowledPin, OUTPUT);
  Serial.println("Starting MCU");

  // Connect to WiFi
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Attempting to connect to WiFi...");
  }

  // If connected, print the WiFi network details
  Serial.println("Connected to WiFi");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.println("WiFi connected");

  // Start the server
  server.begin();
  Serial.println("Server started");
}

void setLEDColor(String emotion) {
  // Print the received emotion for debugging
  Serial.print("Passed emotion: ");
  Serial.println(emotion);

  // Set all LED pins to LOW
  digitalWrite(whiteledPin, LOW);
  digitalWrite(greenledPin, LOW);
  digitalWrite(redledPin, LOW);
  digitalWrite(blueledPin, LOW);
  digitalWrite(yellowledPin, LOW);

  // Determine the LED color based on the received emotion
  if (emotion.startsWith("Neutral")) {
    digitalWrite(whiteledPin, HIGH); 
  } else if (emotion.startsWith("Happy")) {
    digitalWrite(greenledPin, HIGH);
  } 
  else if (emotion.startsWith("Sad")) {
    digitalWrite(blueledPin, HIGH);
  }
  else if (emotion.startsWith("Angry")) {
    digitalWrite(redledPin, HIGH);
  }
  else if (emotion.startsWith("Surprise")) {
    digitalWrite(yellowledPin, HIGH);
  }
}


void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  // Wait until the client sends some data
  while (!client.available()) {
    delay(1);
  }

  // Read the first line of the request
  String emotion = client.readStringUntil('\r');
  Serial.print("Received emotion: ");
  Serial.println(emotion);

  // Set the LED color based on the received emotion
  setLEDColor(emotion);

  // Send response to the client
  client.println("Emotion received");
  client.flush();

  // Wait a moment before closing the connection
  delay(10);
}
