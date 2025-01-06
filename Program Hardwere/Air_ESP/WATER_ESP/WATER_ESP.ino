#include <WiFi.h>
#include <PubSubClient.h>
#include "DFRobot_URM09.h"


/* WiFi Configuration */
const char* ssid = "......";
const char* password = ".....;

/* MQTT Configuration */
const char* mqtt_server = ".....";
const int mqtt_port = 1883;
const char* mqtt_user = ".....";
const char* mqtt_password =  "......";

/* Ultrasonic Sensor */
DFRobot_URM09 URM09;

const int relayPin = 23; // GPIO untuk relay
unsigned long lastPublishTime = 0; // Waktu terakhir publish
unsigned long publishInterval = 1000;  // GPIO untuk relay
WiFiClient espClient;
PubSubClient client(espClient);

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  // Tunggu sampai terhubung
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void connectToMQTT() {
  Serial.println("Connecting to MQTT...");
  client.setServer(mqtt_server, mqtt_port);
  while (!client.connected()) {
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("MQTT connected");
      client.subscribe("inTopic");
      client.subscribe("airbaku/delay");
      client.subscribe("ultrasonic/reset"); 
    } else {
      Serial.print("Failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}
void callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0'; // Tambahkan null terminator
  String message = String((char*)payload);

  if (String(topic) == "airbaku/Relay") {
    if (message == "1") {
      digitalWrite(relayPin, HIGH); // Menyalakan relay
      Serial.println("Relay ON");
    } else if (message == "0") {
      digitalWrite(relayPin, LOW); // Mematikan relay
      Serial.println("Relay OFF");
    }
  } if (String(topic) == "airbaku/delay") {
    int newInterval = message.toInt();
    if (newInterval > 0) {
        publishInterval = newInterval * 1000; // Konversi detik ke milidetik
        Serial.print("Interval publish diubah ke: ");
        Serial.print(publishInterval / 1000); // Cetak dalam satuan detik
        Serial.println(" detik");
    } else {
        Serial.println("Invalid interval received.");
    }
}
    else if (String(topic) == "airbaku/reset") { 
    if (message == "1") { 
      Serial.println("Reset command received. Restarting device...");
      delay(1000); 
      ESP.restart();
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  connectToWiFi();

  // Inisialisasi sensor setelah Wi-Fi
  Serial.println("Initializing ultrasonic sensor...");
  while (!URM09.begin()) {
    Serial.println("I2C device not detected. Retrying...");
    delay(1000);
  }
  URM09.setModeRange(MEASURE_MODE_AUTOMATIC, MEASURE_RANG_500);
  Serial.println("Ultrasonic sensor initialized.");

  // Hubungkan ke MQTT
  client.setCallback(callback);
  connectToMQTT();
}

void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - lastPublishTime >= publishInterval) {
    lastPublishTime = currentMillis;

    float distance = URM09.getDistance();
    if (distance <= 0 || distance > 500) {
      Serial.println("Invalid distance data!");
      return;
    }
    bool relayStatus = digitalRead(relayPin);
    char payload[100];
    snprintf(payload, sizeof(payload), "{\"distance\": %.2f, \"relay_status\": %s}", distance, relayStatus ? "false" : "true");

    client.publish("ultrasonic/data", payload);
    Serial.printf("Published: %s\n", payload);
  }
}
