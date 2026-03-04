#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// ================= RFID =================
#define SS_PIN 7
#define RST_PIN 3
MFRC522 mfrc522(SS_PIN, RST_PIN);

// ================= WIFI =================
const char* ssid = "FTS(WiFi) I'm Out";     // make sure spelling/case matches exactly
const char* password = "Meiz:3lol";

// LCD endpoint (change if LCD IP changes)
String lcdServer = "http://10.182.118.175/receive";

// ================= CARD DATABASE =================
struct Card {
  byte uid[4];
  int number;
  const char* name;
  const char* sharedInterest;   // sent as "interest"
};

Card cards[] = {
  {{0x0B,0xF9,0x29,0x9D},  1, "Abby Lim",            "UX Design"},
  {{0x5B,0x89,0x3A,0x9D},  2, "Bob Liu",             "AIML & IOT"},
  {{0x0B,0xC5,0x3C,0x9D},  3, "Catherine Ko",        "IOT"},
  {{0x7B,0x6E,0x02,0x9D},  4, "David Drapper",       "AIML"},
  {{0xFB,0x16,0x20,0x9D},  5, "Elvin Wong",          "Startups"},
  {{0xFB,0xDD,0x01,0x9D},  6, "Francis Chan",        "Startups & UX Design"},
  {{0x7B,0xF4,0x32,0x9D},  7, "George Teo",          "Startups & AIML"},
  {{0x5B,0xAE,0x27,0x9D},  8, "Henry Toa",           "Startups & IOT"},
  {{0x8B,0x04,0x17,0x9D},  9, "Illhan Su",           "AIML & UX Design"},
  {{0x7B,0x5F,0x4E,0x9D}, 10, "Joshua Luo",          "UX Design & IOT"},
  {{0x27,0xF4,0x53,0x24}, 11, "Card",                "xxxSI"},
  {{0x15,0xFD,0x41,0xE0}, 12, "Blue tear thing",     "xxxSI"}
};

int totalCards = sizeof(cards) / sizeof(cards[0]);

// ================= FIND CARD =================
Card* findCard(byte *uid) {
  for (int i = 0; i < totalCards; i++) {
    bool match = true;
    for (int j = 0; j < 4; j++) {
      if (uid[j] != cards[i].uid[j]) { match = false; break; }
    }
    if (match) return &cards[i];
  }
  return NULL;
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n[BOOT] Starting...");

  SPI.begin(4, 5, 6, 7);
  mfrc522.PCD_Init();
  Serial.println("[RFID] Init done");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.disconnect(true);
  delay(200);

  Serial.print("[WIFI] Connecting to: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("[WIFI] Failed. Status=");
    Serial.println(WiFi.status());
    return;
  }

  Serial.println("[WIFI] Connected!");
  Serial.print("[WIFI] IP: ");
  Serial.println(WiFi.localIP());

  Serial.println("[READY] Tap a card...");
}

// ================= LOOP =================
void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // Build UID string
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Match card
  String name = "Unknown";
  String num = "0";
  String sharedInterest = "None";

  Card* card = findCard(mfrc522.uid.uidByte);
  if (card != NULL) {
    name = card->name;
    num = String(card->number);
    sharedInterest = card->sharedInterest;
  }

  // URL encode spaces (basic)
  name.replace(" ", "%20");
  sharedInterest.replace(" ", "%20");

  // Send to LCD
  String url = lcdServer + "?uid=" + uid +
               "&name=" + name +
               "&num=" + num +
               "&interest=" + sharedInterest;

  Serial.println("\n[SEND] " + url);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    int httpCode = http.GET();
    Serial.print("[HTTP] Code: ");
    Serial.println(httpCode);
    http.end();
  } else {
    Serial.println("[WIFI] Not connected, cannot send.");
  }

  mfrc522.PICC_HaltA();
  delay(300);
}\
