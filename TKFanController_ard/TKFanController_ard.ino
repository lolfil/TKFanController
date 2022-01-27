byte frontFanCtrlPin = 3;
byte rearFanCtrlPin = 11;
byte turboModeButton = 14;
byte silentModeButton = 15;
byte modeReader = 16;

int duty = 50;
char buf[10];

int readline(int readch, char *buffer, int len) {
    static int pos = 0;
    int rpos;

    if (readch > 0) {
        switch (readch) {
            case '\r': // Ignore CR
                break;
            case '\n': // Return on new-line
                rpos = pos;
                pos = 0;  // Reset position index ready for next time
                return rpos;
            default:
                if (pos < len-1) {
                    buffer[pos++] = readch;
                    buffer[pos] = 0;
                }
        }
    }
    return 0;
}

void setup() 
{
  Serial.begin(9600);
  TCCR2B = (TCCR2B & 0xF8) | 0x01; // timer 2 (pins 11,3) TCCR2B = TCCR2B & B11111000 | B00000001;
  
  pinMode(LED_BUILTIN, OUTPUT);
  
  pinMode(frontFanCtrlPin, OUTPUT);
  pinMode(rearFanCtrlPin, OUTPUT);
  
  pinMode(turboModeButton, OUTPUT);
  analogWrite(turboModeButton, 255);
  
  pinMode(silentModeButton, OUTPUT);
  analogWrite(silentModeButton, 128);
  
  pinMode(modeReader, INPUT);

  analogWrite(frontFanCtrlPin, duty);
  analogWrite(rearFanCtrlPin, duty);
}

void loop() 
{
  int mode = analogRead(modeReader);
  if (mode > 500 && mode < 900 && duty != 50)//silent mode 
  {      
    duty = 50;
    analogWrite(rearFanCtrlPin, duty);
    analogWrite(frontFanCtrlPin, duty); 
  }
  else if (mode > 950 && duty != 255) // turbo mode
  {
    duty = 255;      
    analogWrite(rearFanCtrlPin, duty);
    analogWrite(frontFanCtrlPin, duty); 
  }
  else if (mode < 50) // normal mode
  {
    if (readline(Serial.read(), buf, 10) > 0)
    {      
      duty = atoi(buf);
    }
    if (duty > 30)
    {
      digitalWrite(LED_BUILTIN, HIGH);    
    }
    else
    {
      digitalWrite(LED_BUILTIN, LOW);    
    }
    if (duty >= 30 && duty <= 255 )
    {
      analogWrite(frontFanCtrlPin, duty);
      analogWrite(rearFanCtrlPin, duty);
    }
  } 
  delay(100);
}
