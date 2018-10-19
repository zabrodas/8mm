#include <Stepper.h>

Stepper stepper(2048, 2,3,4,5);

void doStep(int cnt){
  stepper.step(cnt);
}
void stepperInit() {
  stepper.setSpeed(10);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Stepper control");
  stepperInit();
}

int param=0;
int cnt=0;
void loop() {

        if (Serial.available()>0) {
                int cmd = Serial.read();
                if (cmd>='0' && cmd<='9') {
                  param=param*10+cmd-'0';
                } else {
                  //Serial.print((char)cmd); Serial.print(param,DEC);
                  switch (cmd) {
                    case 'S': stepper.setSpeed(param); break;
                    case '>': case '+': if (param==0) param=1; doStep(param); cnt+=param; cnt&=2047; break;
                    case '<': case '-': if (param==0) param=1; doStep(-param); cnt-=param; cnt&=2047; break;
                    case 'C': cnt=0; break;
                    case 'T': 
                      for (int i=0; i<param; i++) {
                        Serial.print(i); Serial.print(' ');
                        if (i%10==0) delay(500);
                      }
                      break;
                    default:  Serial.println("-error command"); break;
                  }
                  if (cmd=='>' || cmd=='<') delay(200);
                  Serial.print(cnt); Serial.println('.');
                  param=0;
                  //Serial.print('>');
                }
        }
}
