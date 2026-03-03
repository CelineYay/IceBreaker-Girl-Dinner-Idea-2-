# 🧊 IceBreaker: The Smart Wearable Networking Badge 
Introducing Link Sling

**Conferences and tradeshows are great places to make connections, but how do you know who to approach and keep track of all the new faces afterwards? That's where IceBreaker comes in!**

IceBreaker is an end-to-end IoT networking ecosystem. It combines a custom-engineered wearable digital badge (ESP32-S3) with a full-stack web platform to calculate real-time attendee matchmaking, facilitate effortless digital business card exchanges via RFID, and log your connections seamlessly.

---

## ✨ How It Works

1. **Wear:** Customize your profile on the web app and wear your digital badge.
2. **Tap:** Tap badges with another attendee via the built-in RFID reader to "break the ice"—no awkward intros or physical business cards required.
3. **Connect:** The onboard UI displays "Top Matches" around you, calculating compatibility percentages based on shared goals, interests, and industry tags.
4. **Remember:** All connections are saved to the database automatically so you can revisit your newly expanded network after the event.

---

## 🛠️ System Architecture & Subsystems

This project is divided into three highly integrated subsystems:

### 1. Embedded Hardware & UI (The Badge)
* **Microcontroller:** Waveshare ESP32-S3 Touch LCD 3.5" Module.
* **Display Driver:** ST7796 TFT Display communicating via internal SPI (`Arduino_GFX_Library`).
* **Power Management:** AXP2101 PMIC communicating via I²C, actively monitoring a 500mAh Li-Po battery for live telemetry.
* **Interaction:** RFID reader for physical "tapping" to trigger digital handshakes.
* **UI Design:** A premium, glassmorphism-inspired C++ graphical interface that displays the user's profile, core interests, live matchmaking progress bars, and successfully connected peers.

### 2. Mechanical Structure (The Enclosure)
* **Chassis:** Custom-engineered 3D-printed enclosure designed for strict plug-fit tolerances, isolating the ESP32 and RFID boards from mechanical shock.
* **Wearability:** Features a structural, modular lanyard attachment loop tested to comfortably support the device weight.
* **Bezel:** A flush top faceplate designed to secure the LCD without cracking the glass while providing a clean, premium viewing window.
* **Accessibility:** Iterated USB-C aperture for seamless power delivery and programming.

### 3. Compute & Web Platform 
* **Web Dashboard:** A responsive web app featuring a warm orange/purple UI.
* **Features:** Allows users to create accounts, customize their core interests (UX, IoT, AI/ML, StartUps, etc.), and track Visited Events and Organized Events.
* **Database:** Relational backend mapping `user_id` to `exhibition_id` and storing historical networking connections.

---

## 📂 Repository Structure

* 📁 **`LCD_wifi/`** - Code handling the ESP32's Wi-Fi connection and backend data fetching to update match scores.
* 📁 **`Linksling_Wifi_RFID/`** - The core integration logic handling physical RFID scans, resolving them over Wi-Fi, and triggering the "Connected" state.
* 📄 **`LCD UI Display/`** - The C++ rendering logic for the ST7796 screen, featuring the hardware-accelerated Graphical User Interface.

---

## 🚀 Getting Started (Arduino IDE Setup)

To flash the code to the ESP32-S3 module, ensure you have the following libraries installed via the Arduino Library Manager:

1. **`Arduino_GFX_Library`** (For ST7796 SPI display driving)
2. **`XPowersLib`** (by lewisxhe - For reading the AXP2101 battery telemetry)
3. **`Wire.h` / `SPI.h`** (Standard Arduino libraries)

### Hardware Initialization Note
The Waveshare 3.5" module uses an internal I/O expander at I²C address `0x20` to control the display backlight. Ensure the backlight initialization block is present in your `setup()` before calling `gfx->begin()`.

```cpp
// Backlight Init Example
Wire.beginTransmission(0x20);
Wire.write(0x03); Wire.write(0xFE);
Wire.endTransmission();
// ... (see source code for full initialization sequence)
