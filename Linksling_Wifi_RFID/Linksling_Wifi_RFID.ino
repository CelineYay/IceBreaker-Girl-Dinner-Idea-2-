#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define SS_PIN   7
#define RST_PIN  3

MFRC522 mfrc522(SS_PIN, RST_PIN);

const char* ssid = "FTS(WiFi) I'm Out";
const char* password = "Meiz:3lol";

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  SPI.begin(4, 5, 6, 7);
  mfrc522.PCD_Init();

  connectWiFi();
  Serial.println("Ready to scan...");
}

void loop() {

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uidString = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uidString += "0";
    uidString += String(mfrc522.uid.uidByte[i], HEX);
  }

  uidString.toUpperCase();

  Serial.print("Scanned UID: ");
  Serial.println(uidString);

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    String url = "http://httpbin.org/get?uid=" + uidString;

    http.begin(url);

    int httpCode = http.GET();

    Serial.print("HTTP Code: ");
    Serial.println(httpCode);

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println("Server Response:");
      Serial.println(payload);
    }

    http.end();
  }

  mfrc522.PICC_HaltA();
}

//for OG test
/* 
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define SS_PIN   7
#define RST_PIN  3

MFRC522 mfrc522(SS_PIN, RST_PIN);

const char* ssid = "FTS(WiFi) I'm Out";
const char* password = "Meiz:3lol";

// ===== CARD STRUCT =====
struct Card {
  byte uid[4];
  int number;
  const char* name;
};

Card cards[] = {
  {{0x0B, 0xF9, 0x29, 0x9D}, 1, "Abby"},
  {{0x5B, 0x89, 0x3A, 0x9D}, 2, "Bob"},
  {{0x0B, 0xC5, 0x3C, 0x9D}, 3, "Catherine"},
  {{0x7B, 0x6E, 0x02, 0x9D}, 4, "David Drapper"},
  {{0xFB, 0x16, 0x20, 0x9D}, 5, "Elvin"},
  {{0xFB, 0xDD, 0x01, 0x9D}, 6, "Francis"},
  {{0x7B, 0xF4, 0x32, 0x9D}, 7, "George"},
  {{0x5B, 0xAE, 0x27, 0x9D}, 8, "Henry"},
  {{0x8B, 0x04, 0x17, 0x9D}, 9, "Illhan"},
  {{0x7B, 0x5F, 0x4E, 0x9D}, 10, "u Jerk"},
  {{0x27, 0xF4, 0x53, 0x24}, 11, "Card"},
  {{0x15, 0xFD, 0x41, 0xE0}, 12, "Blue tear thing"}
};

int totalCards = sizeof(cards) / sizeof(cards[0]);

const char* connectedToWho(byte *uid) {

  for (int i = 0; i < totalCards; i++) {
    bool match = true;

    for (int j = 0; j < 4; j++) {
      if (uid[j] != cards[i].uid[j]) {
        match = false;
        break;
      }
    }

    if (match) {
      return cards[i].name;
    }
  }

  return "Unknown";
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  SPI.begin(4, 5, 6, 7);
  mfrc522.PCD_Init();

  connectWiFi();
  Serial.println("Ready to scan...");
}

void loop() {

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uidString = "";

  for (byte i = 0; i < 4; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uidString += "0";
    uidString += String(mfrc522.uid.uidByte[i], HEX);
  }

  uidString.toUpperCase();

  const char* cardName = connectedToWho(mfrc522.uid.uidByte);

  Serial.print("UID: ");
  Serial.println(uidString);

  Serial.print("Matched with: ");
  Serial.println(cardName);

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    String safeName = String(cardName);
    safeName.replace(" ", "%20");

    String url = "http://httpbin.org/get?uid=" + uidString + "&matchedname=" + safeName;

    http.begin(url);

    int httpCode = http.GET();

    Serial.print("HTTP Code: ");
    Serial.println(httpCode);

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println("Server Response:");
      Serial.println(payload);
    }

    http.end();
  }

  mfrc522.PICC_HaltA();
}*/
