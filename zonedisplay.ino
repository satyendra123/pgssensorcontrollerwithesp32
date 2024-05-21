//EXAMPLE-1 in this we are only showing the vacancy data. in this we are not showing the arrow sign. and we are doing this for displaying the dmd library
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
// EXAMPLE-2 we are using this and it is working fine for me. i am using the DMD3 library to print the arrow sign. because it is very easy top print the bitmap using the DMD3 library. this is working code with zone display
#include <SoftwareSerial.h>
#include <SPI.h>
#include <DMD3.h>
#include <TimerOne.h>
#include <font/TimesNewRoman12.h>

const int ledPin = 13;
DMD3 display;

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

byte const arrow1[] PROGMEM = {
  16, 13,
  B00000001, B00000000,
  B00000011, B00000000,
  B00000111, B00000000,
  B00001111, B00000000,
  B00011111, B11111111,
  B00111111, B11111111,
  B01111111, B11111111,
  B01111111, B11111111,
  B00111111, B00000000,
  B00011111, B00000000,
  B00001111, B00000000,
  B00000111, B00000000,
  B00000011, B00000000,
};

const byte* frames[] = {
  arrow1,
};

#define NUM_FRAMES  (sizeof(frames) / sizeof(frames[0]))
unsigned int frame = 0;

#define ADVANCE_MS  (1000 / NUM_FRAMES)

void scan() {
  display.refresh();
}

void setup() {
  Serial.begin(115200);
  Serial.println("Start...");
  Soft_Serial.begin(9600);
  Timer1.initialize(2000);
  Timer1.attachInterrupt(scan);
  Timer1.pwm(9, 255);
}

void loop() {
  // Continuously display the arrow
  show_arrow(frames[frame]);
  delay(ADVANCE_MS);

  frame = (frame + 1) % NUM_FRAMES;

  // Check for serial data
  if (Soft_Serial.available() > 0) {
    process_serial_data();
  }
}

void process_serial_data() {
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
    // Display vacancy and arrow on the P10 display
    show_text(vacancy);
  }
  memset(buffer, 0, sizeof(buffer));
}

void show_text(int vacancy) {
  display.clear();
  char vacancyText[4];
  sprintf(vacancyText, "%d", vacancy);
  display.setFont(TimesNewRoman12); // Use a smaller font
  display.drawText(10, 0, vacancyText); // Adjust the position for text
  display.refresh(); // Refresh the display after drawing text
  delay(2000);
}

void show_arrow(const byte* arrow) {
  display.clear(); // Clear the display buffer before drawing the arrow
  display.drawBitmap(20, 2, arrow); // Draw arrow at the left side
  display.refresh(); // Refresh the display after drawing arrow
}

EXAMPLE-5 Display the data with the new protocol DD(Start_frame) 01(zone_address) 02(vacancy_data) FF(END_FRAME)
  #include <SoftwareSerial.h>
#include <SPI.h>
#include <DMD3.h>
#include <TimerOne.h>
#include <font/TimesNewRoman12.h>

const int ledPin = 13;
DMD3 display;

const byte TX_PIN = 2;
const byte RX_PIN = 3;

SoftwareSerial Soft_Serial(RX_PIN, TX_PIN);

// Define a struct for your data
struct CommunicationData {
  byte start;
  byte zone_id;
  byte vacancy_data;
  byte end;
};

byte const arrow1[] PROGMEM = {
  16, 13,
  B00000001, B00000000,
  B00000011, B00000000,
  B00000111, B00000000,
  B00001111, B00000000,
  B00011111, B11111111,
  B00111111, B11111111,
  B01111111, B11111111,
  B01111111, B11111111,
  B00111111, B00000000,
  B00011111, B00000000,
  B00001111, B00000000,
  B00000111, B00000000,
  B00000011, B00000000,
};

const byte* frames[] = {
  arrow1,
};

#define NUM_FRAMES  (sizeof(frames) / sizeof(frames[0]))
unsigned int frame = 0;

#define ADVANCE_MS  (1000 / NUM_FRAMES)

void scan() {
  display.refresh();
}

void setup() {
  Serial.begin(115200);
  Serial.println("Start...");
  Soft_Serial.begin(9600);
  Timer1.initialize(2000);
  Timer1.attachInterrupt(scan);
  Timer1.pwm(9, 255);
}

void loop() {
  // Continuously display the arrow
  show_arrow(frames[frame]);
  delay(ADVANCE_MS);

  frame = (frame + 1) % NUM_FRAMES;

  // Check for serial data
  if (Soft_Serial.available() > 0) {
    process_serial_data();
  }
}

void process_serial_data() {
  char buffer[20];
  int bytesRead = Soft_Serial.readBytesUntil('\n', buffer, sizeof(buffer));

  Serial.print("Received raw data: ");
  Serial.println(buffer);
  
  // Check if the start and end bytes are correct
  if (buffer[0] == 'D' && buffer[1] == 'D' && buffer[bytesRead - 2] == 'F' && buffer[bytesRead - 1] == 'F') {
    // Extract the vacancy data
    char vacancyCharHigh = buffer[4]; // Extract the high digit
    char vacancyCharLow = buffer[5];  // Extract the low digit
    //Serial.print(buffer[4]);
    //Serial.print(buffer[5]);
    int vacancyHigh = vacancyCharHigh - '0';
    int vacancyLow = vacancyCharLow - '0';
    int vacancy = vacancyHigh * 10 + vacancyLow;
    Serial.print("Vacancy: ");
    Serial.println(vacancy);
    // Display vacancy and arrow on the P10 display
    show_text(vacancy);
  }
  memset(buffer, 0, sizeof(buffer));
}

void show_text(int vacancy) {
  display.clear();
  char vacancyText[4];
  sprintf(vacancyText, "%d", vacancy);
  display.setFont(TimesNewRoman12); // Use a smaller font
  display.drawText(10, 0, vacancyText); // Adjust the position for text
  display.refresh(); // Refresh the display after drawing text
  delay(2000);
}

void show_arrow(const byte* arrow) {
  display.clear(); // Clear the display buffer before drawing the arrow
  display.drawBitmap(20, 2, arrow); // Draw arrow at the left side
  display.refresh(); // Refresh the display after drawing arrow
}
/* you can use this function to display the animation in the arrow p10 display board
int arrowPos = 0; // Initial position of the arrow

void show_arrow(const byte* arrow) {
  display.clear(); // Clear the display buffer before drawing the arrow
  display.drawBitmap(20 + arrowPos, 2, arrow); // Draw arrow at the adjusted position
  display.refresh(); // Refresh the display after drawing arrow
  arrowPos++; // Increment the position for the next frame
  if (arrowPos >= 10) {
    arrowPos = 0; // Reset the position to restart the animation
  }
}
*/

//EXAMPLE-6 using the arrow animation with zone display data
#include <DMD3.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include <DMD3.h>
#include <TimerOne.h>
#include <font/TimesNewRoman12.h>

const int ledPin = 13;
DMD3 display;

const byte TX_PIN = 2;
const byte RX_PIN = 3;

SoftwareSerial Soft_Serial(RX_PIN, TX_PIN);

// Define a struct for your data
struct CommunicationData {
  byte start;
  byte zone_id;
  byte vacancy_data;
  byte end;
};
// Running stick figure pictures are loosely based on those from this tutorial:
// http://www.fluidanims.com/FAelite/phpBB3/viewtopic.php?f=10&t=102

byte const run1[] PROGMEM = {
  16, 13,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
};


byte const run2[] PROGMEM = {
  16, 13,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000001,
  B00000000, B0000001,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
};


byte const run3[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run4[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run5[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
};


byte const run6[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run7[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000001,
  B00000000, B00000000,
};

byte const run8[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B01111111,
  B00000000, B01111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000011,
  B00000000, B00000001,
};


byte const run9[] PROGMEM = {
  16, 13,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B01111111,
  B00000000, B11111111,
  B00000000, B11111111,
  B00000000, B01111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00000111,
  B00000000, B00000011,
};


byte const run10[] PROGMEM = {
  16, 13,
  B00000000, B00000100,
  B00000000, B00001100,
  B00000000, B00011100,
  B00000000, B00111100,
  B00000000, B01111111,
  B00000000, B11111111,
  B00000001, B11111111,
  B00000001, B11111111,
  B00000000, B11111100,
  B00000000, B01111100,
  B00000000, B00111100,
  B00000000, B00011100,
  B00000000, B00001100,
};

byte const run11[] PROGMEM = {
  16, 13,
  B00000000, B00001000,
  B00000000, B00011000,
  B00000000, B00111000,
  B00000000, B01111000,
  B00000000, B11111111,
  B00000001, B11111111,
  B00000011, B11111111,
  B00000011, B11111111,
  B00000001, B11111000,
  B00000000, B11111000,
  B00000000, B01111000,
  B00000000, B00111000,
  B00000000, B00011000,
};

byte const run12[] PROGMEM = {
  16, 13,
  B00000000, B00010000,
  B00000000, B00110000,
  B00000000, B01110000,
  B00000000, B11110000,
  B00000001, B11111111,
  B00000011, B11111111,
  B00000111, B11111111,
  B00000111, B11111111,
  B00000011, B11110000,
  B00000001, B11110000,
  B00000000, B11110000,
  B00000000, B01110000,
  B00000000, B00110000,
};

byte const run13[] PROGMEM = {
  16, 13,
  B00000000, B00100000,
  B00000000, B01100000,
  B00000000, B11100000,
  B00000001, B11100000,
  B00000011, B11111111,
  B00000111, B11111111,
  B00001111, B11111111,
  B00001111, B11111111,
  B00000111, B11100000,
  B00000011, B11100000,
  B00000001, B11100000,
  B00000000, B11100000,
  B00000000, B01100000,
};

byte const run14[] PROGMEM = {
  16, 13,
  B00000000, B01000000,
  B00000000, B11000000,
  B00000001, B11000000,
  B00000011, B11000000,
  B00000111, B11111111,
  B00001111, B11111111,
  B00011111, B11111111,
  B00011111, B11111111,
  B00001111, B11000000,
  B00000111, B11000000,
  B00000011, B11000000,
  B00000001, B11000000,
  B00000000, B11000000,
};

byte const run15[] PROGMEM = {
  16, 13,
  B00000000, B10000000,
  B00000001, B10000000,
  B00000011, B10000000,
  B00000111, B10000000,
  B00001111, B11111111,
  B00011111, B11111111,
  B00111111, B11111111,
  B00111111, B11111111,
  B00011111, B10000000,
  B00001111, B10000000,
  B00000111, B10000000,
  B00000011, B10000000,
  B00000001, B10000000,
};

byte const run16[] PROGMEM = {
  16, 13,
  B00000001, B00000000,
  B00000011, B00000000,
  B00000111, B00000000,
  B00001111, B00000000,
  B00011111, B11111111,
  B00111111, B11111111,
  B01111111, B11111111,
  B01111111, B11111111,
  B00111111, B00000000,
  B00011111, B00000000,
  B00001111, B00000000,
  B00000111, B00000000,
  B00000011, B00000000,
};
Bitmap::ProgMem frames[] = {
    run1,
    run2,
    run3,
    run4,
    run5,
    run6,
    run7,
    run8,
    run9,
    run10,
    run11,
    run12,
    run13,
    run14,
    run15,
    run16,
};
#define NUM_FRAMES  (sizeof(frames) / sizeof(frames[0]))
unsigned int frame = 0;

#define ADVANCE_MS  (1000 / NUM_FRAMES)

void scan()
{
    display.refresh();
}

void setup() {
    Serial.begin(115200);
  Serial.println("Start...");
  Soft_Serial.begin(9600);
  Timer1.initialize(2000);
  Timer1.attachInterrupt(scan);
  Timer1.pwm(9,255);
}

  void loop() {
  // Continuously display the arrow
  show_arrow(frames[frame]);
  delay(ADVANCE_MS);

  frame = (frame + 1) % NUM_FRAMES;

  // Check for serial data
  if (Soft_Serial.available() > 0) {
    process_serial_data();
  }
}

void process_serial_data() {
  char buffer[8];
  int bytesRead = Soft_Serial.readBytesUntil('\n', buffer, sizeof(buffer));

  Serial.print("Received raw data: ");
  Serial.println(buffer);
  
  // Check if the start and end bytes are correct
  if (buffer[0] == 'D' && buffer[1] == 'D' && buffer[bytesRead - 2] == 'F' && buffer[bytesRead - 1] == 'F') {
    // Extract the vacancy data
    char vacancyCharHigh = buffer[4]; // Extract the high digit
    char vacancyCharLow = buffer[5];  // Extract the low digit
    Serial.print(buffer[4]);
    Serial.print(buffer[5]);
    int vacancyHigh = vacancyCharHigh - '0';
    int vacancyLow = vacancyCharLow - '0';
    int vacancy = vacancyHigh * 10 + vacancyLow;
    Serial.print("Vacancy: ");
    Serial.println(vacancy);
    // Display vacancy and arrow on the P10 display
    show_text(vacancy);
  }
  memset(buffer, 0, sizeof(buffer));
}

void show_text(int vacancy) {
  display.clear();
  char vacancyText[4];
  sprintf(vacancyText, "%d", vacancy);
  display.setFont(TimesNewRoman12); // Use a smaller font
  display.drawText(10, 0, vacancyText); // Adjust the position for text
  display.refresh(); // Refresh the display after drawing text
  delay(2000);
}

void show_arrow(const byte* arrow) {
    display.clear();
    //int x = (32 - pgm_read_byte(frames[frame])) / 2;
    display.drawBitmap(20, 2, frames[frame]);
    frame = (frame + 1) % NUM_FRAMES;
    delay(ADVANCE_MS);
}

// EXAMPLE-7 if i want to display the data horizontally. means in the half section arrow animation sign will be displayed and in the other half section text data will be displayed
#include <DMD3.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include <TimerOne.h>
#include <font/TimesNewRoman12.h>

const int ledPin = 13;
DMD3 display;

const byte TX_PIN = 2;
const byte RX_PIN = 3;

SoftwareSerial Soft_Serial(RX_PIN, TX_PIN);

byte const run1[] PROGMEM = {
  16, 13,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
};


byte const run2[] PROGMEM = {
  16, 13,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000001,
  B00000000, B0000001,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
  B00000000, B0000000,
};


byte const run3[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run4[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run5[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000001,
  B00000000, B00000000,
  B00000000, B00000000,
};


byte const run6[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000011,
  B00000000, B00000000,
  B00000000, B00000000,
};

byte const run7[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000111,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000111,
  B00000000, B00000001,
  B00000000, B00000000,
};

byte const run8[] PROGMEM = {
  16, 13,
  B00000000, B00000000,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00001111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B01111111,
  B00000000, B01111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00001111,
  B00000000, B00000011,
  B00000000, B00000001,
};


byte const run9[] PROGMEM = {
  16, 13,
  B00000000, B00000001,
  B00000000, B00000011,
  B00000000, B00000111,
  B00000000, B00011111,
  B00000000, B00111111,
  B00000000, B01111111,
  B00000000, B11111111,
  B00000000, B11111111,
  B00000000, B01111111,
  B00000000, B00111111,
  B00000000, B00011111,
  B00000000, B00000111,
  B00000000, B00000011,
};


byte const run10[] PROGMEM = {
  16, 13,
  B00000000, B00000100,
  B00000000, B00001100,
  B00000000, B00011100,
  B00000000, B00111100,
  B00000000, B01111111,
  B00000000, B11111111,
  B00000001, B11111111,
  B00000001, B11111111,
  B00000000, B11111100,
  B00000000, B01111100,
  B00000000, B00111100,
  B00000000, B00011100,
  B00000000, B00001100,
};

byte const run11[] PROGMEM = {
  16, 13,
  B00000000, B00001000,
  B00000000, B00011000,
  B00000000, B00111000,
  B00000000, B01111000,
  B00000000, B11111111,
  B00000001, B11111111,
  B00000011, B11111111,
  B00000011, B11111111,
  B00000001, B11111000,
  B00000000, B11111000,
  B00000000, B01111000,
  B00000000, B00111000,
  B00000000, B00011000,
};

byte const run12[] PROGMEM = {
  16, 13,
  B00000000, B00010000,
  B00000000, B00110000,
  B00000000, B01110000,
  B00000000, B11110000,
  B00000001, B11111111,
  B00000011, B11111111,
  B00000111, B11111111,
  B00000111, B11111111,
  B00000011, B11110000,
  B00000001, B11110000,
  B00000000, B11110000,
  B00000000, B01110000,
  B00000000, B00110000,
};

byte const run13[] PROGMEM = {
  16, 13,
  B00000000, B00100000,
  B00000000, B01100000,
  B00000000, B11100000,
  B00000001, B11100000,
  B00000011, B11111111,
  B00000111, B11111111,
  B00001111, B11111111,
  B00001111, B11111111,
  B00000111, B11100000,
  B00000011, B11100000,
  B00000001, B11100000,
  B00000000, B11100000,
  B00000000, B01100000,
};

byte const run14[] PROGMEM = {
  16, 13,
  B00000000, B01000000,
  B00000000, B11000000,
  B00000001, B11000000,
  B00000011, B11000000,
  B00000111, B11111111,
  B00001111, B11111111,
  B00011111, B11111111,
  B00011111, B11111111,
  B00001111, B11000000,
  B00000111, B11000000,
  B00000011, B11000000,
  B00000001, B11000000,
  B00000000, B11000000,
};

byte const run15[] PROGMEM = {
  16, 13,
  B00000000, B10000000,
  B00000001, B10000000,
  B00000011, B10000000,
  B00000111, B10000000,
  B00001111, B11111111,
  B00011111, B11111111,
  B00111111, B11111111,
  B00111111, B11111111,
  B00011111, B10000000,
  B00001111, B10000000,
  B00000111, B10000000,
  B00000011, B10000000,
  B00000001, B10000000,
};

byte const run16[] PROGMEM = {
  16, 13,
  B00000001, B00000000,
  B00000011, B00000000,
  B00000111, B00000000,
  B00001111, B00000000,
  B00011111, B11111111,
  B00111111, B11111111,
  B01111111, B11111111,
  B01111111, B11111111,
  B00111111, B00000000,
  B00011111, B00000000,
  B00001111, B00000000,
  B00000111, B00000000,
  B00000011, B00000000,
};
Bitmap::ProgMem frames[] = {
    run1,
    run2,
    run3,
    run4,
    run5,
    run6,
    run7,
    run8,
    run9,
    run10,
    run11,
    run12,
    run13,
    run14,
    run15,
    run16,
};

#define NUM_FRAMES (sizeof(frames) / sizeof(frames[0]))
unsigned int frame = 0;

#define ADVANCE_MS (1000 / NUM_FRAMES)

unsigned long lastFrameChange = 0;
int currentVacancy = -1; // Keep track of the current vacancy value

void scan() {
    display.refresh();
}

void setup() {
    Serial.begin(9600);
    Serial.println("Start...");
    Soft_Serial.begin(9600);
    Timer1.initialize(2000);
    Timer1.attachInterrupt(scan);
    Timer1.pwm(9, 255);
}



// Placeholder for your Soft_Serial object
// Define Soft_Serial as needed for your setup

void loop() {
    unsigned long currentMillis = millis();

    // Continuously display the arrow
    if (currentMillis - lastFrameChange >= ADVANCE_MS) {
        show_arrow(frames[frame]);
        frame = (frame + 1) % NUM_FRAMES;
        lastFrameChange = currentMillis;
    }

    // Check for serial data
    if (Soft_Serial.available() > 0) {
        process_serial_data();
    }
}

void process_serial_data() {
    char buffer[8];
    int bytesRead = Soft_Serial.readBytesUntil('\n', buffer, sizeof(buffer));

    Serial.print("Received raw data: ");
    Serial.println(buffer);

    // Check if the start and end bytes are correct
    if (buffer[0] == 'D' && buffer[1] == 'D' && buffer[bytesRead - 2] == 'F' && buffer[bytesRead - 1] == 'F') {
        // Extract the vacancy data
        char vacancyCharHigh = buffer[4]; // Extract the high digit
        char vacancyCharLow = buffer[5];  // Extract the low digit
        Serial.print(buffer[4]);
        Serial.print(buffer[5]);
        int vacancyHigh = vacancyCharHigh - '0';
        int vacancyLow = vacancyCharLow - '0';
        int vacancy = vacancyHigh * 10 + vacancyLow;

        Serial.print("Vacancy: ");
        Serial.println(vacancy);

        // Update vacancy display if changed and if vacancy is non-negative
        if (vacancy >= 0 && vacancy != currentVacancy) {
            currentVacancy = vacancy;
            show_text(vacancy);
        }
    }
    memset(buffer, 0, sizeof(buffer));
}

void show_text(int vacancy) {
    // Clear the entire display before updating
    display.clear();
    display.setFont(TimesNewRoman12); // Use a smaller font

    char vacancyText[4];
    sprintf(vacancyText, "%d", vacancy);

    int x = (display.width() - display.textWidth(vacancyText)) / 2; // Center the text horizontally
    display.drawText(x - 10, 0, vacancyText); // Adjust the position for text
    display.refresh(); // Refresh the display after drawing text
}

void show_arrow(const byte* arrow) {
    // Clear the specific area for the arrow
    int x = (display.width() - 32) / 2; // Center the bitmap horizontally
    display.drawBitmap(x + 22, 2, arrow);
    display.refresh();
}

/* // this devides the p10 display vertically
void show_text(int vacancy) {
    // Clear the specific area for the text
   // display.fillRect(0, 0, display.width(), 10, false);
    display.setFont(TimesNewRoman12); // Use a smaller font
    char vacancyText[4];
    sprintf(vacancyText, "%d", vacancy);
    int x = (display.width() - display.textWidth(vacancyText)) / 2; // Center the text horizontally
    display.drawText(x, 0, vacancyText); // Adjust the position for text
    display.refresh(); // Refresh the display after drawing text
}

void show_arrow(const byte* arrow) {
    // Clear the specific area for the arrow
    //display.fillRect(0, 10, display.width(), display.height() - 10, false);
    int x = (display.width() - 16) / 2; // Center the bitmap horizontally
    display.drawBitmap(x, 10, arrow);
    display.refresh();
}
*/
