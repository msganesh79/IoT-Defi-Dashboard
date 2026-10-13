/*
 * Secure IoT–DeFi Integration: ESP32 Arduino Microcontroller Sketch
 * ------------------------------------------------------------------
 * Microcontroller: ESP32 Dev Module
 * Protocol: WiFi + MQTT (PubSubClient)
 * Topic: iot/sensors
 * Payload: JSON formatted telemetry
 * 
 * Hardware Requirements:
 * - ESP32 Board
 * - DHT11/DHT22 or DS18B20 Temperature & Humidity Sensor
 * - 10k resistor (pull-up for DHT)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ================= USER CONFIGURATION =================
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// MQTT Broker IP (IP address of the laptop running Mosquitto)
const char* MQTT_BROKER = "192.168.1.100"; 
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "iot/sensors";

// Unique Node Identifier for this physical device
const char* NODE_ID     = "ESP32_Node_Physical_1"; 
// ======================================================

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Sensor pin definitions (e.g. GPIO 4 for DHT11)
#define SENSOR_PIN 4

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to WiFi network: ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi Connected successfully!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting MQTT connection to ");
        Serial.print(MQTT_BROKER);
        Serial.print("...");

        String clientId = "ESP32Client-" + String(random(0xffff), HEX);
        if (mqttClient.connect(clientId.c_str())) {
            Serial.println(" CONNECTED!");
        } else {
            Serial.print(" Failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(". Retrying in 5 seconds...");
            delay(5000);
        }
    }
}

// Function to read sensor or generate hardware telemetry
float readTemperature() {
    // In production, replace with: return dht.readTemperature();
    // Hardware reading simulation fallback:
    static float baseTemp = 25.0;
    float noise = (random(-50, 50) / 100.0);
    return baseTemp + noise;
}

float readHumidity() {
    // In production, replace with: return dht.readHumidity();
    return 52.0 + (random(-100, 100) / 100.0);
}

void setup() {
    Serial.begin(115200);
    setup_wifi();

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();

    // Read sensor values
    float temp = readTemperature();
    float hum  = readHumidity();

    // Construct JSON Payload using ArduinoJson
    StaticJsonDocument<256> doc;
    doc["node_id"]     = NODE_ID;
    doc["temperature"]  = round(temp * 100.0) / 100.0;
    doc["humidity"]     = round(hum * 10.0) / 10.0;
    doc["status"]       = "HEALTHY";
    doc["timestamp"]    = millis() / 1000;

    char jsonBuffer[256];
    serializeJson(doc, jsonBuffer);

    // Publish to Mosquitto MQTT Broker
    Serial.print("Publishing JSON payload: ");
    Serial.println(jsonBuffer);
    
    if (mqttClient.publish(MQTT_TOPIC, jsonBuffer)) {
        Serial.println("--> MQTT Publish SUCCESS!");
    } else {
        Serial.println("--> MQTT Publish FAILED.");
    }

    // Transmit telemetry every 3 seconds
    delay(3000);
}
