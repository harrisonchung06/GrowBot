#include <AccelStepper.h>
#include <Servo.h>

#define MOTOR_INTERFACE_TYPE AccelStepper::DRIVER

#define DIR_PIN_X 8
#define PUL_PIN_X 7

#define DIR_PIN_Y 12
#define PUL_PIN_Y 11

#define DIR_PIN_Z 10
#define PUL_PIN_Z 9

#define SWITCH_PIN_R_X 6
#define SWITCH_PIN_L_X 5

#define SWITCH_PIN_R_Y 3
#define SWITCH_PIN_L_Y 4

#define SWITCH_PIN_R_Z 14
#define SWITCH_PIN_L_Z 2

const int MAX_SPEED = 1000;
const int ACCELERATION = 1000; 

AccelStepper x(MOTOR_INTERFACE_TYPE, PUL_PIN_X, DIR_PIN_X);
AccelStepper y(MOTOR_INTERFACE_TYPE, PUL_PIN_Y, DIR_PIN_Y);
AccelStepper z(MOTOR_INTERFACE_TYPE, PUL_PIN_Z, DIR_PIN_Z);

Servo claw;

int MAX_X_STEPS = 0;  
int MAX_Y_STEPS = 0;  
int MAX_Z_STEPS = 0;  
int max_positions[3];

int x_pos;
int y_pos;
int z_pos;

int claw_pos;

String str;

void setup() {
  pinMode(SWITCH_PIN_R_X, INPUT_PULLUP);
  pinMode(SWITCH_PIN_L_X, INPUT_PULLUP);
  pinMode(SWITCH_PIN_R_Y, INPUT_PULLUP);
  pinMode(SWITCH_PIN_L_Y, INPUT_PULLUP);
  pinMode(SWITCH_PIN_R_Z, INPUT_PULLUP);
  pinMode(SWITCH_PIN_L_Z, INPUT_PULLUP);
  
  x.setMaxSpeed(MAX_SPEED);
  x.setAcceleration(ACCELERATION);
  x.setSpeed(MAX_SPEED);   

  y.setMaxSpeed(MAX_SPEED);
  y.setAcceleration(ACCELERATION);
  y.setSpeed(MAX_SPEED);

  z.setMaxSpeed(MAX_SPEED);
  z.setAcceleration(ACCELERATION);
  z.setSpeed(MAX_SPEED);

  claw.attach(13);

  Serial.begin(9600);

  while(1) {
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command == "HOME") { 
        home();
        break;
      }
    }
  }
}

int home() {
  MAX_X_STEPS = 0;
  MAX_Y_STEPS = 0;
  MAX_Z_STEPS = 0;

  int right_switchState_x = digitalRead(SWITCH_PIN_R_X);
  int left_switchState_x = digitalRead(SWITCH_PIN_L_X);

  int right_switchState_y = digitalRead(SWITCH_PIN_R_Y);
  int left_switchState_y = digitalRead(SWITCH_PIN_L_Y);

  int right_switchState_z = digitalRead(SWITCH_PIN_R_Z);
  int left_switchState_z = digitalRead(SWITCH_PIN_L_Z);

  claw_pos = 80;
  claw.write(claw_pos);
  
  
  while (right_switchState_x == LOW) { 
    right_switchState_x = digitalRead(SWITCH_PIN_R_X);
    x.runSpeed();
  }
  
  x.stop();  
  x.setCurrentPosition(0);  
  x.setSpeed(-MAX_SPEED);

  while (left_switchState_x == LOW) {
    left_switchState_x = digitalRead(SWITCH_PIN_L_X);
    x.runSpeed();
  }
  x.stop();

  while (right_switchState_y == LOW) { 
    right_switchState_y = digitalRead(SWITCH_PIN_R_Y);
    y.runSpeed();
  }
  y.stop();  
  y.setCurrentPosition(0);  
  y.setSpeed(-MAX_SPEED);

  while (left_switchState_y == LOW) {
    left_switchState_y = digitalRead(SWITCH_PIN_L_Y);
    y.runSpeed();
  }
  y.stop();

  while (right_switchState_z == LOW) { 
    right_switchState_z = digitalRead(SWITCH_PIN_R_Z);
    z.runSpeed();
  }
  z.stop();  
  z.setCurrentPosition(0);  
  z.setSpeed(-MAX_SPEED);

  while (left_switchState_z == LOW) {
    left_switchState_z = digitalRead(SWITCH_PIN_L_Z);
    z.runSpeed();
  }
  z.stop();
  
  MAX_X_STEPS = x.currentPosition();
  MAX_Y_STEPS = y.currentPosition();
  MAX_Z_STEPS = z.currentPosition();

  x.setCurrentPosition(0);
  y.setCurrentPosition(0);
  z.setCurrentPosition(0);

  max_positions[0] = abs(MAX_X_STEPS);
  max_positions[1] = abs(MAX_Y_STEPS);
  max_positions[2] = abs(MAX_Z_STEPS);

  Serial.print("MAX:");
  for (int i =0; i<3;i++){
    Serial.print(max_positions[i]);
    if (i<2){
      Serial.print(",");
    }
  }
  Serial.println();
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input == "PING"){
      Serial.println("POS:" + String(x.currentPosition()) + "," + String(y.currentPosition()) + "," + String(z.currentPosition()));
    } else if (input.startsWith("CLW:")) {
      int target = input.substring(4).toInt();
      if (target > claw_pos){
        for (int i = claw_pos; i<=target; i++){
          claw.write(i);
          delay(10); 
        }
      } else{
        for (int i = claw_pos; i>=target; i--){
          claw.write(i);
          delay(10); 
        }
      }
      claw_pos = target;
      Serial.println("CLAW_DONE");
    } else {
      String old_input = input;
      input = input.substring(4);  

      int values[6];
      for (int i = 0; i < 6; i++) {
        int commaIndex = input.indexOf(',');
        if (commaIndex != -1 && i < 5) {
          values[i] = input.substring(0, commaIndex).toInt();
          input = input.substring(commaIndex + 1);
        } else {
          values[i] = input.toInt();  
        }
      }

      int dx = 0;
      int dy = 0;
      int dz = 0;
      int vx = 0;
      int vy = 0;
      int vz = 0;
      long target_x = 0;
      long target_y = 0;
      long target_z = 0;
      bool in_bounds = true;

      if (old_input.startsWith("STP:")){
        dx = values[0];
        dy = values[1];
        dz = values[2];
        vx = values[3];
        vy = values[4];
        vz = values[5];

        target_x = x.currentPosition() + dx;
        target_y = y.currentPosition() + dy;
        target_z = z.currentPosition() + dz;

      } else if (old_input.startsWith("POS:")){
        target_x = values[0];
        target_y = values[1];
        target_z = values[2];

        dx = target_x - x.currentPosition();
        dy = target_y - y.currentPosition();
        dz = target_z - z.currentPosition();
        vx = values[3];
        vy = values[4];
        vz = values[5];
      }
      
      if (target_x < 0 || target_x > max_positions[0]) in_bounds = false;
      if (target_y < 0 || target_y > max_positions[1]) in_bounds = false;
      if (target_z < 0 || target_z > max_positions[2]) in_bounds = false;

      if (in_bounds) {
        if (dx != 0) {
          x.setMaxSpeed(abs(vx));
          x.move(dx);
        }
        if (dy != 0) {
          y.setMaxSpeed(abs(vy));
          y.move(dy);
        }
        if (dz != 0) {
          z.setMaxSpeed(abs(vz));
          z.move(dz);
        }

        x.runToPosition();
        y.runToPosition();
        z.runToPosition();

        Serial.println("DONE");
      } else {
        Serial.println("ERR:OUT_OF_BOUNDS");
      }
    } 
  }
}
