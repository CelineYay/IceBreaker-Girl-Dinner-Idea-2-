#include <WiFi.h>
#include <WebServer.h>
#include <Arduino_GFX_Library.h>
#include <Wire.h>
#include "time.h"

// ================= WIFI =================
const char* ssid     = "YOUR_WIFI";
const char* password = "YOUR_PASS";

WebServer server(80);

// ================= LCD =================
#define I2C_SDA 21
#define I2C_SCL 22
#define PIN_BL  25

Arduino_DataBus *bus = new Arduino_ESP32SPI(27, 5, 18, 23, 19);
Arduino_GFX *gfx    = new Arduino_ST7796(bus, GFX_NOT_DEFINED, 0, true);

// ================= COLOR MACRO =================
#define C(r,g,b) (uint16_t)(((r&0xF8)<<8)|((g&0xFC)<<3)|(b>>3))

#define BG        C(  8,  8, 10)
#define WHITE     C(255,255,255)
#define GREY      C(136,136,153)
#define LGREY     C(240,240,240)
#define CARD_BG   C( 18, 18, 20)
#define SUTD_RED  C(212, 28, 42)
#define CYAN      C(  0,229,255)
#define GREEN     C(  0,230,118)
#define CARD_BDR  C( 30, 30, 35)

// ================= PROFILE =================
#define MY_NAME    "Wong Yu Xuan"
#define MY_TITLE   "Student"
#define MY_COMPANY "SUTD"
#define MY_PHONE   "+65 12873425"
#define MY_EMAIL   "yuxuan_wong@sutd.edu.sg"
#define EVENT_NAME "IDEA EVENT"

// ================= TIME SET =================
#define SET_HOUR  10
#define SET_MIN   36
#define SET_SEC    0
#define SET_DAY   27
#define SET_MON    2
#define SET_YEAR  2026

const char* monthName[] = {
  "JAN","FEB","MAR","APR","MAY","JUN",
  "JUL","AUG","SEP","OCT","NOV","DEC"
};

// ================= POPUP STATE =================
bool showPopup = false;
uint32_t popupStart = 0;
String popupText = "";

// ================= HELPERS =================
void fillRR(int16_t x,int16_t y,int16_t w,int16_t h,int16_t r,uint16_t c){
  gfx->fillRoundRect(x,y,w,h,r,c);
}
void drawRR(int16_t x,int16_t y,int16_t w,int16_t h,int16_t r,uint16_t c){
  gfx->drawRoundRect(x,y,w,h,r,c);
}

// ================= CLOCK =================
void drawClock() {
  struct tm t;
  getLocalTime(&t);

  gfx->fillRect(0, 0, 320, 16, BG);

  char buf[12];
  sprintf(buf, "%02d:%02d:%02d", t.tm_hour, t.tm_min, t.tm_sec);
  gfx->setTextColor(GREY);
  gfx->setTextSize(1);
  gfx->setCursor(16, 4);
  gfx->print(buf);

  char dbuf[14];
  sprintf(dbuf, "%02d %s %04d", t.tm_mday, monthName[t.tm_mon], t.tm_year+1900);
  gfx->setCursor(238, 4);
  gfx->print(dbuf);
}

// ================= DRAW CARD =================
void drawCard(int16_t x, int16_t y, int16_t w, int16_t h) {
  fillRR(x, y, w, h, 10, CARD_BG);
  drawRR(x, y, w, h, 10, CARD_BDR);
}

// ================= MAIN SCREEN =================
void drawScreen() {
  gfx->fillScreen(BG);

  int px = 16;
  int y  = 20;

  int badgeW = strlen(EVENT_NAME) * 6 + 20;
  fillRR(px, y, badgeW, 18, 4, SUTD_RED);
  gfx->setTextColor(WHITE);
  gfx->setTextSize(1);
  gfx->setCursor(px + 10, y + 5);
  gfx->print(EVENT_NAME);
  y += 26;

  int cardX = px, cardW = 320 - px*2;
  int profileH = 100;
  drawCard(cardX, y, cardW, profileH);

  gfx->setTextColor(WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(cardX + 12, y + 10);
  gfx->print(MY_NAME);

  drawClock();
}

// ================= POPUP =================
void drawPopup(String text) {

  int boxW = 260;
  int boxH = 140;
  int x = (320 - boxW) / 2;
  int y = (480 - boxH) / 2;

  fillRR(x, y, boxW, boxH, 12, CARD_BG);
  drawRR(x, y, boxW, boxH, 12, GREEN);

  gfx->setTextColor(WHITE);
  gfx->setTextSize(2);
  gfx->setCursor(x + 20, y + 20);
  gfx->print("Matched:");

  gfx->setTextColor(GREEN);
  gfx->setTextSize(2);

  int cursorY = y + 60;
  int maxWidth = boxW - 40;
  int charWidth = 12;
  int maxChars = maxWidth / charWidth;

  String word = "";
  String line = "";

  for (int i = 0; i < text.length(); i++) {
    char c = text[i];

    if (c == ' ' || i == text.length() - 1) {

      if (i == text.length() - 1 && c != ' ')
        word += c;

      if (line.length() + word.length() > maxChars) {
        gfx->setCursor(x + 20, cursorY);
        gfx->println(line);
        cursorY += 24;
        line = word + " ";
      } else {
        line += word + " ";
      }

      word = "";
    } else {
      word += c;
    }
  }

  if (line.length() > 0) {
    gfx->setCursor(x + 20, cursorY);
    gfx->println(line);
  }
}

// ================= RECEIVE HANDLER =================
void handleReceive() {

  if (server.hasArg("name")) {
    popupText = server.arg("name");
    showPopup = true;
    popupStart = millis();
  }

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

  pinMode(PIN_BL, OUTPUT);
  digitalWrite(PIN_BL, HIGH);

  gfx->begin();

  // Set RTC
  struct tm t = {0};
  t.tm_hour = SET_HOUR; t.tm_min = SET_MIN; t.tm_sec = SET_SEC;
  t.tm_mday = SET_DAY;  t.tm_mon = SET_MON - 1;
  t.tm_year = SET_YEAR - 1900;
  time_t epoch = mktime(&t);
  struct timeval tv = { epoch, 0 };
  settimeofday(&tv, NULL);

  connectWiFi();
  server.on("/receive", handleReceive);
  server.begin();

  drawScreen();
}

// ================= LOOP =================
uint32_t lastClock = 0;

void loop() {

  server.handleClient();

  if (millis() - lastClock >= 1000) {
    lastClock = millis();
    drawClock();
  }

  if (showPopup) {
    drawPopup(popupText);

    if (millis() - popupStart > 3000) {
      showPopup = false;
      drawScreen();
    }
  }

  delay(20);
}