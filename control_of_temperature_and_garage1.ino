#include <Servo.h>
#define SERVO 5
#define TRIGGER 2
#define ECHO 3
long duration; // Variable for the duration of sound wave travel.
float distance;
int flag = 0; // Variable to send IFTTT request only once
String ssid = "Simulator Wifi";
String password = "";
String link  = "https://maker.ifttt.com";
const int port = 80;
String uri = "/trigger/garage_opened/with/key/dZj6Bwm8AeLdMt3SC7TevIq9it3-oevKOurZNNMgQhx";
Servo servo;

void setup(){
  Serial.begin(115200);
  Serial.println("AT"); 
  if (!Serial.find("OK")){
    Serial.println("---------Error TEST---------");
  };
  Serial.println("AT+CWJAP=\"" + ssid + "\",\"" + password + "\"");     
  if (!Serial.find("OK")){
    Serial.println("---------Error CWJAP---------");
  };
  Serial.println("AT+CIPSTART=\"TCP\",\"" + link + "\"," + port);
  if (!Serial.find("OK")){
    Serial.println("---------Error CIPSTART---------");
  };
  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);
  servo.attach(SERVO);

}
void loop(){
	digitalWrite(TRIGGER, LOW);
  	delayMicroseconds(2);
  	digitalWrite(TRIGGER, HIGH);
  	delayMicroseconds(10);
  	digitalWrite(TRIGGER, LOW);
  	duration = pulseIn(ECHO, HIGH);
  
    // Calculating the distance.
  	// Speed of sound wave divided by 2 (go and back).
    distance = duration * 0.034 / 2;
    if(distance >= 5.0 && distance <= 15.0){
		servo.write(90);
      	if(flag == 0){
          
        	// Create HTTP request message.
            String httpRequest = "GET " + uri +
              " HTTP/1.1\r\nHost: " + link + "\r\n\r\n";
            int length = httpRequest.length();

            // Info for Wifi module about packet length.
            Serial.print("AT+CIPSEND=");
            Serial.println(length);

            // Send HTTP GET request to ESP8266.
            Serial.print(httpRequest);
            if (!Serial.find("SEND OK\r\n")){
            }
        }
      	flag++;
    } else {
      	flag = 0;
      	servo.write(0);
    }
}
