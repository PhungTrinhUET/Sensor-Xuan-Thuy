#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char *ssid = "Fatlab";
const char *password = "12345678@!";
const char *mqtt_server = "192.168.1.148";

// Địa chỉ IP và cổng của ThingsBoard
const char *thingsboard_server = "192.168.1.148";
const int thingsboard_port = 1883;
const char *device_access_token = "jHpuzhE7MWOchvCTPXoi";

WiFiClient espClient;
PubSubClient client(espClient);

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");

  client.setServer(thingsboard_server, thingsboard_port);
  dht.begin();
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (!isnan(temperature) && !isnan(humidity)) {
    String payload = "{\"outsideTemp\":" + String(temperature) + ", \"outsideHumidity\":" + String(humidity) + "}";

    if (!client.connected()) {
      if (client.connect("ESP32Client", device_access_token, NULL)) {
        Serial.println("Connected to ThingsBoard");
      } else {
        Serial.println("Failed to connect to ThingsBoard");
        return;
      }
    }

    if (client.publish("v1/devices/me/telemetry", payload.c_str())) {
      Serial.println("Data sent to ThingsBoard");
    } else {
      Serial.println("Failed to send data to ThingsBoard");
    }
  } else {
    Serial.println("Failed to read data from sensors");
  }

  delay(1000); // Delay để giảm tải trên ThingsBoard
}
