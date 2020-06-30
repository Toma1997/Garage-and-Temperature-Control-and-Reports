String ssid     = "Simulator Wifi";
String password = "";
String link     = "api.thingspeak.com";
const int port   = 80;
String uri     = "/update?api_key=&field1=";

void setup() {
  
  Serial.begin(115200);   
  Serial.println("AT"); 
  delay(10); 
  if (!Serial.find("OK")){
  	Serial.println("---------GRESKA TEST---------");
  };
    
  Serial.println("AT+CWJAP=\"" + ssid + "\",\"" + password + "\"");
  delay(10);      
  if (!Serial.find("OK")){
  	Serial.println("---------GRESKA CWJAP---------");
  };
  Serial.println("AT+CIPSTART=\"TCP\",\"" + link + "\"," + port);
  delay(50);
  if (!Serial.find("OK")){
    Serial.println("---------GRESKA CIPSTART---------");
  };
  
               
}

void loop() {
  
  double tempC = analogRead(A0);
  tempC = ((5*tempC/1023)-0.5)*100;
  
  
  // Kreiranje HTTP zahteva, poruke
  String httpPacket = "GET " + uri + "50" + " HTTP/1.1\r\nHost: " + link + "\r\n\r\n";
  int length = httpPacket.length();
  
  // Obavestenje za ESP koliko je duga poruka
  Serial.print("AT+CIPSEND=");
  Serial.println(length);
  delay(10); 
  
  // Slanje poruke ka ESP8266
  Serial.print(httpPacket);
  delay(10);
  if (!Serial.find("SEND OK\r\n")){
  
  };
  
  delay(60000);
}