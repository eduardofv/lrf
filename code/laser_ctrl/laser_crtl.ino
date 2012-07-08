
#include <Servo.h>

#define LASER_PIN       13 //Pin
#define LASER_OFF      HIGH
#define LASER_ON       LOW
#define LASER_ON_CMD   '+'
#define LASER_OFF_CMD  '-'

#define SERVO_PIN      9
Servo laser_servo;

#define MAX_CMD_LEN    10


void sweep(int stp)
{
  for(int i=30;i<=110;i+=stp)
  {
    Serial.println(i);
    laser_servo.write(i);
    
    delay(500);
  } 
  
}

String servo_cmd()
{
  String ret="OK ";
  //String cmd = String(MAX_CMD_LEN);
  char cmd[MAX_CMD_LEN];
  int index=0;
  boolean finished = false;
  
  while(index<MAX_CMD_LEN && !finished)
  {
    byte b = Serial.read();
    if( b==13 )
      b=0;
    finished = b==0;
    //cmd.setCharAt(index++,char(b));
    cmd[index++] = b;
  }
  
  Serial.print(cmd);
  /*
  if(finished) 
    Serial.print("finished");
  else
    Serial.print("not finished");
  */
  
  
  //End of Cmd reached
  if(finished)
  {
    if(cmd[0]=='s'){
      int s=10;
      
      if(cmd[1]=='1') s=1;
      if(cmd[1]=='0') s=10;
      if(cmd[1]=='2') s=2;
      if(cmd[1]=='5') s=5;
      
      sweep(s);
    }
    else{   
      Serial.println("moving");
      //int deg = atoi(cmd.toCharArray());
      int deg = atoi(cmd);
      Serial.println(deg);
      laser_servo.write(deg);
      delay(50);
    }

    ret="OK";
  }
  else //reached max len
  {
    ret = "NAK";
  }
  
  return ret;  
}

void setup(){
  Serial.begin(9600);
  pinMode(LASER_PIN,OUTPUT);
  digitalWrite(LASER_PIN,LASER_OFF);
  
  laser_servo.attach(SERVO_PIN);
}

void loop(){
  if(Serial.available() > 0 ){
    delay(300);
    Serial.println("lrf>");
    byte cmd = Serial.read();
    switch(cmd)
    {
      //LASER OFF
      case '-':
        digitalWrite(LASER_PIN,LASER_OFF);
        Serial.println("OK");
        break;
      //LASER ON
      case '+':0
        digitalWrite(LASER_PIN,LASER_ON);
        Serial.println("OK");
        break;
      //Laser cmd
      case 'l':
         Serial.println(servo_cmd());
         break;
      default:
        Serial.println("NAK");      
    }
  }
}
