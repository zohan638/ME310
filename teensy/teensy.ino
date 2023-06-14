#include<Servo.h>
Servo ESC1;
Servo ESC2;

int int_call = 0;
int speed_val = 0;
const int interrupt_pin = 20;
unsigned long startTime = 0;

void setup(){
  ESC1.attach(3,1000,2000);
  ESC2.attach(4,1000,2000);
  pinMode(interrupt_pin, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(interrupt_pin), pin_ISR, CHANGE);
  Serial1.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentTime = millis();
  
  if (int_call != 1 && Serial1.available()){
    int temp_val = Serial1.parseInt();
    speed_val = map(temp_val, 0,100,0,180);
    Serial1.println(speed_val*100/180);
    ESC1.write(speed_val);
    ESC2.write(160);
    startTime = millis();
  }
  else if (int_call == 1){
    Serial1.println("Error Recieved... HALTING");
    while (int_call == 1){
      speed_val = 0;
      ESC1.write(speed_val);
      ESC2.write(speed_val);
      digitalWrite(LED_BUILTIN, HIGH);
    }
    digitalWrite(LED_BUILTIN, LOW);
  }
  else{                              
    if (int(speed_val*100/180) == 25){
      unsigned long elapsedTime = (currentTime - startTime) / 1000;
      if (elapsedTime >= static_cast<unsigned long>(3)){
        ESC2.write(0);
      }
      if (elapsedTime >= static_cast<unsigned long>(10)){
        ESC2.write(160);
        startTime = millis();
      } 
    }
    else if (int(speed_val*100/180) == 27){
      unsigned long elapsedTime = (currentTime - startTime) / 1000;
      if (elapsedTime >= static_cast<unsigned long>(10)){
        ESC2.write(0);
      }
      if (elapsedTime >= static_cast<unsigned long>(20)){
        ESC2.write(160);
        startTime = millis();
      } 
    }
    else{
      ESC1.write(speed_val);
      ESC2.write(speed_val);
    }
  }
}

void pin_ISR(){
  int_call = digitalRead(interrupt_pin);
}
