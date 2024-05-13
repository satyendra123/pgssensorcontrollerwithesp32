#include <SoftwareSerial.h>
#include <SPI.h>
#include <DMD.h>
#include <TimerOne.h>
#include "Arial_black_16.h"

#define DISPLAYS_ACROSS 1   // Number of P1 panels in horizontal
#define DISPLAYS_DOWN   1   // Number of P1 panels in vertical
DMD dmd(DISPLAYS_ACROSS, DISPLAYS_DOWN);

const byte TX_PIN = 2;
const byte RX_PIN = 3;

SoftwareSerial Soft_Serial(RX_PIN, TX_PIN);

// Define a struct for your data
struct CommunicationData {
  byte start;
  byte zone_id;
  byte total_sensor;
  byte sensor_status_1;
  byte sensor_status_2;
  byte total_engaged;
  byte total_disengaged;
  byte total_vacancy;
  byte total_error;
  byte end;
};

void ScanDMD() {
  dmd.scanDisplayBySPI();
}

void setup() {
  Serial.begin(115200);
  Serial.println("Start...");

  Soft_Serial.begin(9600);
  Timer1.initialize(3000);
  Timer1.attachInterrupt(ScanDMD);
}

void loop() {
  if (Soft_Serial.available() > 0) {
    char buffer[20];
    int bytesRead = Soft_Serial.readBytesUntil('\n', buffer, sizeof(buffer));

    Serial.print("Received raw data: ");
    Serial.println(buffer);
    // Check if the start and end bytes are correct
    if (buffer[0] == 'A' && buffer[1] == 'A' && buffer[bytesRead - 2] == '5' && buffer[bytesRead - 1] == '5') {
      // Extract the vacancy byte
      char vacancyCharHigh = buffer[14]; // Extract the high digit
      char vacancyCharLow = buffer[15];  // Extract the low digit
      //Serial.print(buffer[14]);
      //Serial.print(buffer[15]);
      int vacancyHigh = vacancyCharHigh - '0';
      int vacancyLow = vacancyCharLow - '0';
      int vacancy = vacancyHigh * 10 + vacancyLow;
      Serial.print("Vacancy: ");
      Serial.println(vacancy);
      show_text(String(vacancy).c_str(), strlen(String(vacancy).c_str()));
    }
    memset(buffer, 0, sizeof(buffer));
  }
  
  delay(2000);
  dmd.clearScreen(true);
}
void show_text(const char* text, int length) {
  dmd.clearScreen(true);
  dmd.selectFont(Arial_Black_16);
  dmd.drawString(0, 0, text, length, GRAPHICS_NORMAL);
}
