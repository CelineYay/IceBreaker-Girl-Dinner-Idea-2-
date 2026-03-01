#include <WiFi.h>
#include <WebServer.h>
#include <Arduino_GFX_Library.h>
#include "TCA9554.h"
#include <Wire.h>

// ================= WIFI =================
const char* ssid     = "FTS(WiFi) I'm Out";
const char* password = "Meiz:3lol";

WebServer server(80);

// ================= LCD =================
#define GFX_BL 25
#define I2C_SDA 21
#define I2C_SCL 22

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
String lastInterest = "None";   // 🔥 NEW

// ================= POPUP STATE =================
bool showPopup = false;
uint32_t popupStart = 0;

// ================= COLORS =================
#define BLACK 0x0000
#define WHITE 0xFFFF
#define GREEN 0x07E0
#define CYAN  0x07FF
#define GREY  0x8410
#define GOLD  0xFEA0

// ================= MAIN UI =================
void drawScreen1() {

  gfx->fillScreen(BLACK);

  const char* shared[]  = { "UX Design", "IoT" };
  uint16_t    scol[]    = { CYAN, GREEN };
  uint16_t    sbg[]     = { 0x0410, 0x0200 };

  int sx = 12, sy = 202;

  for (int i = 0; i < 2; i++) {
    int sw = strlen(shared[i]) * 12 + 20;
    gfx->fillRoundRect(sx, sy, sw, 28, 6, sbg[i]);
    gfx->drawRoundRect(sx, sy, sw, 28, 6, scol[i]);
    gfx->setTextColor(scol[i]);
    gfx->setTextSize(2);
    gfx->setCursor(sx + 10, sy + 6);
    gfx->print(shared[i]);
    sx += sw + 10;
  }

  gfx->drawFastHLine(12, 244, 296, GREY);

  gfx->setTextColor(GREY);
  gfx->setTextSize(1);
  gfx->setCursor(12, 252);
  gfx->print("MATCH SCORE");

  gfx->setTextColor(GREEN);
  gfx->setTextSize(5);
  gfx->setCursor(80, 268);
  gfx->print("88%");

  gfx->fillRoundRect(12, 330, 296, 18, 6, 0x0200);
  gfx->fillRoundRect(12, 330, 260, 18, 6, GREEN);

  gfx->fillCircle(152, 420, 5, GREY);
  gfx->fillCircle(170, 420, 5, GOLD);

  gfx->setTextColor(GREY);
  gfx->setTextSize(1);
  gfx->setCursor(65, 460);
  gfx->print("< SWIPE RIGHT to go back");
}

// ================= TEXT WRAP FUNCTION =================
void drawWrappedText(String text, int x, int y, int maxWidth) {

  int charWidth = 12; // approximate for textSize 2
  int maxChars = maxWidth / charWidth;

  String line = "";
  int cursorY = y;

  for (int i = 0; i < text.length(); i++) {
    line += text[i];

    if (line.length() >= maxChars || i == text.length() - 1) {
      gfx->setCursor(x, cursorY);
      gfx->println(line);
      line = "";
      cursorY += 24;
    }
  }
}

// ================= POPUP =================
void drawPopup() {

  int boxW = 280;
  int boxH = 200;
  int x = (320 - boxW) / 2;
  int y = (480 - boxH) / 2;

  gfx->fillRoundRect(x, y, boxW, boxH, 12, 0x0410);
  gfx->drawRoundRect(x, y, boxW, boxH, 12, GREEN);

  gfx->setTextColor(WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(x + 20, y + 20);
  gfx->println("Matched:");

  gfx->setTextColor(GREEN);
  gfx->setTextSize(2);

  // Name
  drawWrappedText(lastName, x + 20, y + 60, boxW - 40);

  // Shared Interest
  gfx->setTextColor(WHITE);
  gfx->setCursor(x + 20, y + 120);
  gfx->println("Shared Interest:");

  gfx->setTextColor(CYAN);
  drawWrappedText(lastInterest, x + 20, y + 150, boxW - 40);
}

// ================= RECEIVE HANDLER =================
void handleReceive() {

  if (server.hasArg("uid"))      lastUID = server.arg("uid");
  if (server.hasArg("name"))     lastName = server.arg("name");
  if (server.hasArg("num"))      lastNumber = server.arg("num");
  if (server.hasArg("interest")) lastInterest = server.arg("interest");  // 🔥 NEW

  showPopup = true;
  popupStart = millis();

  server.send(200, "text/plain", "OK");
}

// ================= WIFI CONNECT =================
void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  Serial.print("LCD IP: ");
  Serial.println(WiFi.localIP());
}

// ================= SETUP =================
void setup() {

  Serial.begin(115200);

  Wire.begin(I2C_SDA, I2C_SCL);
  TCA.begin();
  TCA.pinMode1(0, OUTPUT);

  TCA.write1(0,1); delay(10);
  TCA.write1(0,0); delay(10);
  TCA.write1(0,1); delay(200);

  gfx->begin();

  pinMode(GFX_BL, OUTPUT);
  digitalWrite(GFX_BL, HIGH);

  connectWiFi();

  server.on("/receive", handleReceive);
  server.begin();

  drawScreen1();
}

// ================= LOOP =================
void loop() {

  server.handleClient();

  if (showPopup) {
    drawPopup();

    if (millis() - popupStart > 3000) {
      showPopup = false;
      drawScreen1();
    }
  }

  delay(20);
}