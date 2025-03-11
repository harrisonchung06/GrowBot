#include <AccelStepper.h>
#define MOTOR_INTERFACE_TYPE AccelStepper::DRIVER
#define DIR_PIN_1 9
#define PUL_PIN_1 8
#define SWITCH_PIN_R_1 2
#define SWITCH_PIN_L_1 5

const int MAX_SPEED = 1000;
const int ACCELERATION = 500; 
AccelStepper axis1(MOTOR_INTERFACE_TYPE, PUL_PIN_1, DIR_PIN_1);

int MAX_STEPS = 0;  
int pos;
String str; 

void setup() {
  pinMode(SWITCH_PIN_R_1, INPUT_PULLUP);
  pinMode(SWITCH_PIN_L_1, INPUT_PULLUP);
  axis1.setMaxSpeed(MAX_SPEED);
  axis1.setAcceleration(ACCELERATION);
  axis1.setSpeed(MAX_SPEED);   
  Serial.begin(115200);
  Serial.setTimeout(1);

  while (1){
    if (Serial.available() > 0) {
      str = Serial.readStringUntil('\n');
      if (str.equals("START")){
        break;
      }
    }
  }
  MAX_STEPS = home(); 
}

int home() {
  MAX_STEPS = 0;

  while (digitalRead(SWITCH_PIN_R_1) == HIGH) { 
    axis1.runSpeed();
  }

  axis1.stop();  

  delay(500);

  axis1.setCurrentPosition(0);  
  axis1.setSpeed(-MAX_SPEED);

  while (digitalRead(SWITCH_PIN_L_1) == HIGH) {
    axis1.runSpeed();
  }

  axis1.stop();

  delay(500);

  int current_position = axis1.currentPosition();
  axis1.setCurrentPosition(0);  
  Serial.println(current_position);

  return current_position;
}

void loop(){
  if (Serial.available() > 0) {  
    delay(500);
    pos = Serial.readStringUntil('\n').toInt();   
    axis1.moveTo(pos);
    axis1.runToPosition();
    Serial.println(axis1.currentPosition());
  }
}
