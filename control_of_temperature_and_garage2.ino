#define HEAT 7
#define TEMP_SENSOR A0
#define COOLER 9

int measurePeriod = 100; // 1 minute
const double refTemp = 23.0;
const int maxCoolerPower = 255;
float temp;
int coolerPow, heatState;
unsigned long prevMillis;

String ssid     = "Simulator Wifi";
String password = "";
String link     = "https://api.thingspeak.com";
const int port   = 80;
String uri     = "/update?api_key=ODCFILYGY9PA32O1";

void setup(){
  	Serial.begin(115200);
  	Serial.println("AT"); 
    if (!Serial.find("OK")){
      Serial.println("---------GRESKA TEST---------");
    };

    Serial.println("AT+CWJAP=\"" + ssid + "\",\"" + password + "\"");     
    if (!Serial.find("OK")){
      Serial.println("---------GRESKA CWJAP---------");
    };
    Serial.println("AT+CIPSTART=\"TCP\",\"" + link + "\"," + port);
    if (!Serial.find("OK")){
      Serial.println("---------GRESKA CIPSTART---------");
    };
	pinMode(HEAT, OUTPUT);
  	pinMode(TEMP_SENSOR, INPUT);
  	pinMode(COOLER, OUTPUT);
  
  	
}

void loop(){
	if(millis() - prevMillis >= measurePeriod){
      	prevMillis = millis();
  		temp = ((analogRead(TEMP_SENSOR) * 0.00488) - 0.5) * 100;
      	Serial.println(temp);
        if(temp > refTemp){
          	heatState = LOW;
          	digitalWrite(HEAT, heatState);
            if(temp < refTemp + 3){
              	coolerPow = maxCoolerPower*0.5;
            } else if (temp < refTemp + 10){
            	coolerPow = maxCoolerPower*0.7;
            } else {
            	coolerPow = maxCoolerPower;
            }
          	analogWrite(COOLER, coolerPow);

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
      
      	// TODO: poslati podatke o temp, snazi motora i stanju grejaca na Thingspeak.
  		// Kreiranje HTTP zahteva, poruke
        String httpPacket = "GET " + uri + 
          "&field1="+temp+"&field2="+coolerPow+"&field3="+heatState
          + " HTTP/1.1\r\nHost: " + link + "\r\n\r\n";
        int length = httpPacket.length();

        // Obavestenje za ESP koliko je duga poruka
        Serial.print("AT+CIPSEND=");
        Serial.println(length);

        // Slanje poruke ka ESP8266
        Serial.print(httpPacket);
        if (!Serial.find("SEND OK\r\n")){

        }
    }
     
}
