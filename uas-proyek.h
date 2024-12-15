#include <ESP8266WiFi.h>        // Untuk ESP8266, gunakan <WiFi.h> untuk ESP32
#include <PubSubClient.h>
#include <DHT.h>

// WiFi dan konfigurasi MQTT
const char* ssid = "wifiName";             // Ganti dengan SSID WiFi Anda
const char* password = "wifiPass";        // Ganti dengan password WiFi Anda
const char* mqtt_server = "mqttServerIP"; // Ganti dengan alamat IP broker MQTT Anda
const int mqtt_port = 1883;

// Topik MQTT
const char* topic_suhu = "dht/suhu";
const char* topic_kelembapan = "dht/kelembapan";
const char* topic_jarak = "hc_sro4/jarak";
const char* topic_air = "waterdrop/value"; // Mengirimkan nilai Waterdrop Sensor

// Konfigurasi Sensor DHT
#define DHTPIN D4            // Pin tempat sensor DHT22 terhubung
#define DHTTYPE DHT22        // Jenis sensor DHT (bisa diganti ke DHT22)
DHT dht(DHTPIN, DHTTYPE);

// Konfigurasi Sensor Ultrasonik HC-SR04
#define TRIG_PIN D5          // Pin Trigger untuk sensor ultrasonik
#define ECHO_PIN D6          // Pin Echo untuk sensor ultrasonik

// Konfigurasi Sensor Waterdrop
#define WATERDROP_PIN A0     // Pin analog untuk sensor Waterdrop

long duration;
int distance;

// Membuat objek WiFiClient dan PubSubClient untuk koneksi MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Fungsi untuk menghubungkan ke WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Fungsi untuk menghubungkan kembali ke broker MQTT jika terputus
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// Fungsi untuk menghitung jarak menggunakan sensor ultrasonik HC-SR04
long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  duration = pulseIn(ECHO_PIN, HIGH);  // Mengukur durasi pulsa pada pin Echo
  distance = duration * 0.0344 / 2;   // Menghitung jarak dalam cm (kecepatan suara 0.0344 cm/�s)

  return distance;
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  dht.begin();

  // Inisialisasi pin sensor ultrasonik
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Inisialisasi sensor Waterdrop (tidak memerlukan konfigurasi tambahan)
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Membaca suhu dan kelembapan dari sensor DHT
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Memastikan pembacaan sensor DHT berhasil
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Mengirimkan suhu dan kelembapan ke MQTT broker
  char tempStr[8];
  char humStr[8];
  dtostrf(t, 6, 2, tempStr);  // Mengubah suhu menjadi string
  dtostrf(h, 6, 2, humStr);   // Mengubah kelembapan menjadi string

  client.publish(topic_suhu, tempStr);  // Mengirimkan data suhu
  client.publish(topic_kelembapan, humStr);  // Mengirimkan data kelembapan

  Serial.print("Temperature: ");
  Serial.print(tempStr);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humStr);
  Serial.println(" %");

  // Membaca jarak dari sensor ultrasonik
  long distance = getDistance();
  
  // Mengirimkan jarak ke MQTT broker
  char distanceStr[8];
  itoa(distance, distanceStr, 10);  // Mengubah jarak menjadi string
  client.publish(topic_jarak, distanceStr);  // Mengirimkan data jarak

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Membaca data dari sensor Waterdrop
  int waterValue = analogRead(WATERDROP_PIN);  // Membaca nilai analog dari sensor

  // Mengirimkan nilai sensor Waterdrop ke MQTT broker
  char waterValueStr[8];
  itoa(waterValue, waterValueStr, 10);  // Mengubah nilai analog menjadi string
  client.publish(topic_air, waterValueStr);

  Serial.print("Waterdrop Value: ");
  Serial.println(waterValue);

  // Tunggu 30 detik sebelum pengambilan data berikutnya
  delay(30000);
}
