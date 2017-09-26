// read_potentiometer.ino

/* Analog Read to LED
 * ------------------ 
 *
 * turns on and off a light emitting diode(LED) connected to digital  
 * pin 13 if the potentiometer is above/below 50%. When a cross
 * over 50% occurs, a message is sent over the serial line where our
 * Python program is listening in, waiting to send a message to lambda
 *
 * Andrew Alexander 
 * Created 2017 <http://andrewalexander.io>
 * 
 * 
 * Taken from an script:
 * Created 1 December 2005
 * copyleft 2005 DojoDave <http://www.0j0.org>
 * http://arduino.berlios.de
 *
 */

int potPin = 2;    // select the input pin for the potentiometer
int ledPin = 13;   // select the pin for the LED
int val = 0;       // variable to store the value coming from the sensor
int state = 0;     // variable to hold high or low state (default LOW)
int counter = 0;   // variable to keep track of loops for status reporting

void setup() {
  pinMode(ledPin, OUTPUT);  // declare the ledPin as an OUTPUT
  pinMode(potPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  val = analogRead(potPin);    // read the value from the sensor
  
  if (val >= 512 && state == 0) {
    state = 1;
    Serial.println(val);
    digitalWrite(ledPin, HIGH);
  } else if (val <= 512 && state == 1) {
    state = 0;
    Serial.println(val);
    digitalWrite(ledPin, LOW);
  }
  
  delay(250);
}
