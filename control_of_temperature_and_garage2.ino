#define HEAT 7
#define TEMP_SENSOR A0
#define COOLER 9
int measurePeriod = 60000; // 1 minute.
const double refTemp = 23.0;
const int maxCoolerPower = 255;
float temp, coolerPow;
int heatState;
unsigned long prevMillis;
String ssid = "Simulator Wifi";
String password = "";
String link = "https://api.thingspeak.com";
const int port = 80;
String uri = "/update?api_key=TAQQIM5C7XWY8LB8";

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
	pinMode(HEAT, OUTPUT);
  	pinMode(TEMP_SENSOR, INPUT);
  	pinMode(COOLER, OUTPUT);
}
void loop(){
	if(millis() - prevMillis >= measurePeriod){
      	prevMillis = millis();
      	
      	// Calculate temperature in C by converting Analog signal.
      	// Multiply with 5V and divide by 1024 (10bit) resolution
      	// to get mili volts and then substract by delta 0.5
      	// and mutlitply with 100 to get temp in C.
  		temp = ((analogRead(TEMP_SENSOR) * 5.0/1024.0) - 0.5) * 100;
        if(temp > refTemp){
          	heatState = LOW;
          	digitalWrite(HEAT, heatState);
            if(temp < refTemp + 3){
              	coolerPow = 50;
            } else if (temp < refTemp + 10){
            	coolerPow = 70;
            } else {
            	coolerPow = 100;
            }
          	analogWrite(COOLER, maxCoolerPower*(coolerPow/100.0));

        } else { // temp <= 23C
          	coolerPow = 0;
          	analogWrite(COOLER, coolerPow);
          	if (temp < refTemp - 3){
				heatState = HIGH;
            } else { // temp == 23C
              	heatState = LOW;
            }
          	digitalWrite(HEAT, heatState);
        }
      	
  		// Create HTTP request message.
        String httpRequest = "GET " + uri + 
          "&field1="+temp+"&field2="+coolerPow+"&field3="+heatState
          + " HTTP/1.1\r\nHost: " + link + "\r\n\r\n";
        int length = httpRequest.length();

        // Info for Wifi module about packet length.
        Serial.print("AT+CIPSEND=");
        Serial.println(length);

        // Send HTTP GET request to ESP8266.
        Serial.print(httpRequest);
        if (!Serial.find("SEND OK\r\n")){
        }
    }
}
