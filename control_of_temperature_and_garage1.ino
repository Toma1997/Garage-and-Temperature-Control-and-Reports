#include <Servo.h>
#define SERVO 5
#define TRIGGER 2
#define ECHO 3
long duration; // variable for the duration of sound wave travel
float distance;

Servo servo;
void setup(){
  Serial.begin(115200);
  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);
  servo.attach(SERVO);

}

void loop(){
  	servo.write(0);
	digitalWrite(TRIGGER, LOW);
  	delayMicroseconds(2);
  	digitalWrite(TRIGGER, HIGH);
  	delayMicroseconds(10);
  	digitalWrite(TRIGGER, LOW);
  	duration = pulseIn(ECHO, HIGH);
  
    // Calculating the distance
  	// Speed of sound wave divided by 2 (go and back).
    float distance = duration * 0.034 / 2; 
    Serial.println(distance);
    if(distance >= 5.0 && distance <= 15.0){
		servo.write(90);
      	// Inform via email that garage opened.
    }
}
