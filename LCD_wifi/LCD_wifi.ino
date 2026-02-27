#include <WiFi.h>
#include <WebServer.h>
#include <Arduino_GFX_Library.h>
#include "TCA9554.h"
#include <Wire.h>

// ================= WIFI =================
const char* ssid = "Type in wifi name";
const char* password = "Type in wifi pass"; 

WebServer server(80);

// ================= LCD =================
#define GFX_BL 25

TCA9554 TCA(0x20);

Arduino_DataBus *bus = new Arduino_ESP32SPI(
  27,  // DC
  5,   // CS
  18,  // SCK
  23,  // MOSI
  19   // MISO
);

Arduino_GFX *gfx = new Arduino_ST7796(
  bus, GFX_NOT_DEFINED, 0, true
);

// ================= DATA =================
String lastUID = "None";
String lastName = "None";
String lastNumber = "None";

void updateLCD() {
  gfx->fillScreen(RGB565_BLACK);
  gfx->setTextColor(RGB565_WHITE);
  gfx->setTextSize(2);

  gfx->setCursor(20, 80);
  gfx->println("ESP32 RFID Display");

  gfx->setCursor(20, 140);
  gfx->print("UID: ");
  gfx->println(lastUID);

  gfx->setCursor(20, 180);
  gfx->print("Name: ");
  gfx->println(lastName);

  gfx->setCursor(20, 220);
  gfx->print("Number: ");
  gfx->println(lastNumber);
}

void handleReceive() {
  if (server.hasArg("uid"))  lastUID = server.arg("uid");
  if (server.hasArg("name")) lastName = server.arg("name");
  if (server.hasArg("num"))  lastNumber = server.arg("num");

  updateLCD();
  server.send(200, "text/plain", "OK");
}

void setup() {

  Serial.begin(115200);

  // LCD reset using TCA9554
  Wire.begin(21,22);
  TCA.begin();
  TCA.pinMode1(0,OUTPUT);

  TCA.write1(0,1); delay(10);
  TCA.write1(0,0); delay(10);
  TCA.write1(0,1); delay(200);

  gfx->begin();
  pinMode(GFX_BL, OUTPUT);
  digitalWrite(GFX_BL, HIGH);

  WiFi.begin(ssid,password);
  while(WiFi.status()!=WL_CONNECTED) delay(500);

  Serial.print("LCD Board IP: ");
  Serial.println(WiFi.localIP());

  server.on("/receive", handleReceive);
  server.begin();

  updateLCD();
}

void loop() {
  server.handleClient();
}

// ================= FETCH UID =================
void fetchUID()
{
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;

  // ⚠️ IMPORTANT:
  // This must match the LAST scanned UID.
  // Since httpbin does not store anything,
  // this will only work if you manually change UID.
  http.begin(serverBase + String(lastUID));

  int httpCode = http.GET();

  if (httpCode == 200)
  {
    String payload = http.getString();

    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);

    String uid = doc["args"]["uid"];
    uid.toUpperCase();

    if (uid != "" && uid != lastUID)
    {
      lastUID = uid;

      String name = findName(uid);

      gfx->fillScreen(RGB565_BLACK);
      gfx->setCursor(20, 40);
      gfx->setTextColor(RGB565_WHITE);
      gfx->setTextSize(2);

      gfx->println("UID:");
      gfx->println(uid);
      gfx->println("");
      gfx->println("Name:");
      gfx->println(name);
    }
  }

  http.end();
}

// ================= SETUP =================
void setup()
{
  Serial.begin(115200);

  Wire.begin(21, 22);
  TCA.begin();
  TCA.pinMode1(0, OUTPUT);

  TCA.write1(0, 1);
  delay(10);
  TCA.write1(0, 0);
  delay(10);
  TCA.write1(0, 1);
  delay(200);

  gfx->begin();
  pinMode(GFX_BL, OUTPUT);
  digitalWrite(GFX_BL, HIGH);

  connectWiFi();
}

// ================= LOOP =================
void loop()
{
  fetchUID();
  delay(3000);
}