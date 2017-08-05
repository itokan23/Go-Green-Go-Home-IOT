#include <SoftwareSerial.h>
#include <CmdMessenger.h>
int washcount = 0;
byte leds = 0;
int washPin = 8;
int dryPin = 6;
int EVPin = 2;  
int HVACPin = 10;
int lightPin1  = 7;
int lightPin2 = 5;
int lightPin3 = 4;
int lightPin4 = 3;

SoftwareSerial mySerial(3,EVPin); // pin 2 = TX, pin 3 = RX (unused)

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  mySerial.begin(9600);
  pinMode(HVACPin,OUTPUT); // HVAC
  pinMode(13,OUTPUT); 
  pinMode(washPin,OUTPUT); // Washer
  pinMode(dryPin,OUTPUT); //Dryer
  pinMode(EVPin,OUTPUT); // EV
  pinMode(lightPin1, OUTPUT);
  pinMode(lightPin2, OUTPUT);
  pinMode(lightPin3, OUTPUT);
  pinMode(lightPin4, OUTPUT);
}


void loop() {
  //Listen to Python and actuate brightness of LED
  if( Serial.available() > 0){
    
    float hvac = 0;
    //Serial.readBytesUntil(character, buffer, length)
    float EV = Serial.parseFloat(); // EV charge => LCD Display
    int wash= Serial.parseInt(); // Washer/dryer => DC Motor
    int dry = Serial.parseInt(); // Dryer
    hvac = Serial.parseFloat(); // HVAC => LCD?
    float lights = Serial.parseFloat(); // Lights=> LEDs
    int time = Serial.parseInt(); // Time=>LCD
    //float a = cmdMessenger.readFloatArg();

    String EVstring = String(EV);
    if (EV > 0.0) {
      digitalWrite(EVPin,HIGH);
    }
      if (EV == 0.0) {
      digitalWrite(EVPin,LOW);
    }
    if (wash == 1) {
      digitalWrite(washPin,HIGH);
    }
    if (wash == 0) {
      digitalWrite(washPin,LOW);
    }
    if (dry == 1) {
      digitalWrite(dryPin,HIGH);
    }
    if (dry == 0) {
      digitalWrite(dryPin,LOW);
    }
    if (lights == 1.0) {
      digitalWrite(lightPin1,HIGH);
      digitalWrite(lightPin2,HIGH);
      digitalWrite(lightPin3,HIGH);
      digitalWrite(lightPin4,HIGH);
    }
    if (lights == 0.0) {
      digitalWrite(lightPin1,LOW);
      digitalWrite(lightPin2,LOW);
      digitalWrite(lightPin3,LOW);
      digitalWrite(lightPin4,LOW);
    }
    // don't know how to turn off
    if (hvac > 0.0) {
      digitalWrite(HVACPin,HIGH);
    }
    if (hvac == 0.0) {
      digitalWrite(HVACPin,LOW);
    }
    int soc = 41;
    clearscreen();
    mySerial.write("EV: ");
    mySerial.print(EVstring);
    mySerial.write(" KWH");
    mySerial.write("      Time: ");
    mySerial.print(time);
    mySerial.write(":00");
    delay(2000);
    clearscreen();
    mySerial.write("HVAC: ");
    mySerial.print(hvac);
    mySerial.write(" KW ");
    delay(2000);
    clearscreen();
    delay(100);
    
  }
  //delay(4000); // there is a half second delay in the communication between python and arduino
}

void clearscreen()
{
  mySerial.write(254); // reset cursor
  mySerial.write(128);
  mySerial.write("                "); // print blank
  mySerial.write("                ");
  mySerial.write(254); // reset cursor
  mySerial.write(128);
}





