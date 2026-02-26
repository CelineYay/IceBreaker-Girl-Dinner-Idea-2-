#include <WiFi.h>
#include <Arduino_GFX_Library.h>

// ---- Display Setup (based on GFX HelloWorld example) ----
Arduino_DataBus *bus = new Arduino_ESP32SPI(
  27 /* DC */, 5 /* CS */, 18 /* SCK */, 23 /* MOSI */, 19 /* MISO */
);
Arduino_GFX *gfx = new Arduino_ST7796(
  bus, -1 /* RST */, 0 /* rotation */, true /* IPS */
);

// ---- WiFi Configuration ----
const char* ssid     = "FTS(WiFi) I'm Out";
const char* password = "Meiz:3lol";

void setup() {
  Serial.begin(115200);

  // Init Display
  gfx->begin();
  gfx->fillScreen(0x0000);
  gfx->setTextSize(2);
  gfx->setTextColor(0xFFFF);

  // First message
  gfx->setCursor(10, 220);
  gfx->println("No connections yet");

  // Start WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    // Wi-Fi connected
    String msg = "Connected with ";
    msg += WiFi.SSID();

    gfx->fillScreen(0x0000);
    gfx->setCursor(10, 220);
    gfx->println(msg);
  } else {
    // Failed
    gfx->fillScreen(0x0000);
    gfx->setCursor(10, 220);
    gfx->println("WiFi failed");
  }
}

void loop() {
  // Nothing else here
}