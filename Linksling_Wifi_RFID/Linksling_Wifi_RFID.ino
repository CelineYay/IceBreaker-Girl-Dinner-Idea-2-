#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// ================= RFID =================
#define SS_PIN 7
#define RST_PIN 3

MFRC522 mfrc522(SS_PIN, RST_PIN);

// ================= WIFI =================
const char* ssid = "Type in wifi name";
const char* password = "Type in wifi pass"; 

// 🔥 CHANGE THIS if LCD IP changes
String lcdServer = "http://10.182.118.175/receive";

// ================= CARD DATABASE =================
struct Card {
  byte uid[4];
  int number;
  const char* name;
};

Card cards[] = {
  {{0x0B,0xF9,0x29,0x9D},1,"Abby Lim"},
  {{0x5B,0x89,0x3A,0x9D},2,"Bob Liu"},
  {{0x0B,0xC5,0x3C,0x9D},3,"Catherine Ko"},
  {{0x7B,0x6E,0x02,0x9D},4,"David Drapper"},
  {{0xFB,0x16,0x20,0x9D},5,"Elvin Wong"},
  {{0xFB,0xDD,0x01,0x9D},6,"Francis Chan"},
  {{0x7B,0xF4,0x32,0x9D},7,"George Teo"},
  {{0x5B,0xAE,0x27,0x9D},8,"Henry Toa"},
  {{0x8B,0x04,0x17,0x9D},9,"Illhan Su"},
  {{0x7B,0x5F,0x4E,0x9D},10,"Joshua Luo"},
  {{0x27,0xF4,0x53,0x24},11,"Card"},
  {{0x15,0xFD,0x41,0xE0},12,"Blue tear thing"}
};

int totalCards = sizeof(cards)/sizeof(cards[0]);

// ================= FIND CARD =================
Card* findCard(byte *uid){
  for(int i=0;i<totalCards;i++){
    bool match=true;
    for(int j=0;j<4;j++){
      if(uid[j]!=cards[i].uid[j]){
        match=false;
        break;
      }
    }
    if(match) return &cards[i];
  }
  return NULL;
}

// ================= SETUP =================
void setup() {

  Serial.begin(115200);

  SPI.begin(4,5,6,7);
  mfrc522.PCD_Init();

  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid,password);
  while(WiFi.status()!=WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  Serial.println("Ready to scan...");
}

// ================= LOOP =================
void loop() {

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // ===== Build UID string =====
  String uid="";
  for(byte i=0;i<mfrc522.uid.size;i++){
    if(mfrc522.uid.uidByte[i]<0x10) uid+="0";
    uid+=String(mfrc522.uid.uidByte[i],HEX);
  }
  uid.toUpperCase();

  // ===== Match card =====
  String name="Unknown";
  String num="0";

  Card* card=findCard(mfrc522.uid.uidByte);
  if(card!=NULL){
    name=card->name;
    num=String(card->number);
  }

  // ===== URL encode spaces =====
  name.replace(" ", "%20");

  // ===== Send to LCD =====
  HTTPClient http;

  String url = lcdServer + "?uid=" + uid +
               "&name=" + name +
               "&num=" + num;

  Serial.println("Sending to LCD:");
  Serial.println(url);

  http.begin(url);
  int httpCode = http.GET();

  Serial.print("HTTP Code: ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.println("Response:");
    Serial.println(payload);
  } else {
    Serial.println("HTTP Request Failed");
  }

  http.end();

  mfrc522.PICC_HaltA();
}