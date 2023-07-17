/*
    CRT vector interface for Whirlwind
    
Versions:
    0.1a:   new hardware
    0.1c:   inverted voltages 
    1.1a:   with PCB, light pin low active
*/

#include <limits.h>
const char version [] = "1.1b";

#include <SPI.h>
#define SPI_speed 1000000       // SPI clock speed < 4 MHz
// #define SPI_MOSI 17
// #define SPI_SCK 13
// #define SPI_SS 10


// control pins
const int pinPos = A3;   
const int pinMove = A2;
// light gun pin
const int lightPin = 4;

// Key to cycle through modes
const int keyPin = 3;

// Toggle debug output to serial
bool do_debug = false;

/*
    Wait for a short  (< 0.3sec) keypress
*/
void wait_key() {
    while (digitalRead(keyPin) == HIGH);
        delay(300);     // debounce and skip short press
}

/*
    Sets D/A outputs by SPI
    Inputs is an integer fixed point number between -1 and +1,
    i.e. scaled by 10^15: -INT_MAX .. +INT_MAX
    that sets the output to 2.5V +/- 2.5V V.
    As the DA converter expects a 12-bit integer between 0 and 4095,
    -32768 correpsonds to 0, and +32768 to 4095.  
    The value is negated for hardware reasons.
*/
void setDAbySPI(int valx, int valy) {
  unsigned int sendword;

  // activate chip select 
  digitalWrite(SS, LOW);

  // send 16 bits
  SPI.beginTransaction(SPISettings(SPI_speed, MSBFIRST, SPI_MODE0));
  
  sendword = 2048 - valx / 16; 
  // Serial.println(sendword, HEX);
  SPI.transfer16(sendword | 0x3000 | 0x8000);            // DA0 

  SPI.endTransaction();
          
  // deactivate cip select   
  digitalWrite(SS, HIGH); 
  // delayMicroseconds(20);
  
  // activate chip select 
  digitalWrite(SS, LOW);

  // send 16 bits
  SPI.beginTransaction(SPISettings(SPI_speed, MSBFIRST, SPI_MODE0));
  
   sendword = 2048 - valy / 16; 
  // Serial.println(sendword, HEX);
  SPI.transfer16(sendword | 0x3000 | 0x0000);   // DA1 
  SPI.endTransaction();

  digitalWrite(SS, HIGH);

}

/*  Illuminate a point
    x and y are fixed point as in WWI, i.e. scaled by 2^-15
    32767 is +0.99997 and -32767 is -0.99997
    Produce a strobe for 50µs, then set the negative for AC inputs.
*/
void showPoint(int x, int y) {
    // draw twice for more intensity
    drawVector(x, y, 0, 0);
     
/*
    // second strobe  
    digitalWrite(pinMove, HIGH);
    delayMicroseconds(60);
    digitalWrite(pinMove, LOW);
  */      
}

/*  Draw a (short) vector
 *   
 */
void drawVector(int x, int y, int speedx, int speedy) {
    setDAbySPI(x, y);
    digitalWrite(pinPos, HIGH);
    delayMicroseconds(30 );
    digitalWrite(pinPos, LOW);
    setDAbySPI(speedx, speedy);             
    // delayMicroseconds(30);
    digitalWrite(pinMove, HIGH);
    delayMicroseconds(60); 
    digitalWrite(pinMove, LOW);         
}
   
/* convert floating point to fixed point, i.e. 
*/
int floatfix(float x) {
    if (x >= 1.0)
        return 32767;
    if (x <= -1.0)
        return -32767;
    return round(x * 32767);
}

/*  
    Illuminate a point by float input 
*/
void showFPoint(float x, float y) {
    showPoint(floatfix(x), floatfix(y));
  
}

const float xslope = 4.0, yslope = 4.0;
void drawFVector(float x0, float y0, float x1, float y1) {  
    const float xmax = 1.0 / xslope; 
    const float ymax = 1.0 / yslope;
    float dx = x1 - x0;
    float dy = y1 - y0;
    if (abs(dx) < 0.01 + xmax && abs(dy) < 0.01 + ymax) {
        drawVector(floatfix(x0), floatfix(y0), floatfix(xslope*dx), floatfix(yslope*dy));
        return;
    }
    /*
    dx = dx / 4.0;
    dy = dy / 4.0;
    drawFVector(x0, y0, x0+dx, y0+dy);
    x0 += dx;
    y0 += dy; 
    drawFVector(x0, y0, x0+dx, y0+dy);
    x0 += dx;
    y0 += dy; 
    drawFVector(x0, y0, x0+dx, y0+dy);
    x0 += dx;
    y0 += dy; 
    drawFVector(x0, y0, x0+dx, y0+dy);

    */
    // use same length segments
    int xsegs = abs(dx * xslope)+0.99;
    int ysegs = abs(dy * yslope)+0.99;
    int segs = xsegs;
    if (ysegs > segs)
        segs = ysegs;
    if (segs < 1) {
        Serial.print("??? segs=");
        Serial.print(segs);
        Serial.print(" dx=");
        Serial.print(dx);
        Serial.print(" ");
        Serial.print(dx*xslope);
        Serial.print(" dy=");
        Serial.print(dy);
        Serial.print(" ");
        Serial.println(dy*yslope); 
    }
    dx = dx / segs;
    dy = dy / segs;
    
    while (segs > 0)  {

       float x1 = x0 + dx;
       float y1 = y0 + dy;
       drawFVector(x0, y0, x1, y1);
       x0 = x1;
       y0 = y1; 
       --segs;
    }
    
}
                    

/**
  Draw an arc with center at (x,y) and radius r.
  Start with angle (startArc) and end at (endArc). 
  
**/
void draw_arc(float x0, float y0, float r, float startArc, float endArc) {
    // the number of points for a full circle
    int points = 60.0 * r;
    // use a minimum of points
    if (points < 6) points = 6;
    long int start = millis();
    float x1 = x0;
    float y1 = y0 + r;
    for (int i = 1; i<=points; ++i) {
        float t;
        t = i * (6.282 / points);
        print(t, i, points)
        float x2 = x0+r*sin(t);
        float y2 = y0+r*cos(t);
        drawFVector(x1, y1, x2, y2);
        x1 = x2;
        y1 = y2;
    }  

}

/**
  Draw a circle with center at (x,y) and radius r. 
**/
void draw_circle(float x0, float y0, float r) {
    // number of vectors
    int points = 60.0 * r;
    // use a minimum of points
    if (points < 6) points = 6;
    
    float x1 = x0;
    float y1 = y0 + r;
    for (int i = 1; i<=points; ++i) {
        float t;
        t = i * (6.282 / points);
        float x2 = x0+r*sin(t);
        float y2 = y0+r*cos(t);
        drawFVector(x1, y1, x2, y2);
        x1 = x2;
        y1 = y2;
    }  

}
 
/*
  Draw a straight line by a given number of points (not a vector)
*/
void draw_line_points(float x1, float y1, float x2, float y2, int points) {
    int cnt;
    float ix = (x2 - x1) / points;
    float iy = (y2 - y1) / points;
    for (cnt = 1; cnt <= points; ++cnt) {
        float x, y;
        x = x1 + ix * cnt;
        y = y1 + iy * cnt;
        showFPoint(x, y);
    }
}

/* 
  Draw a line with default number of points
*/
void draw_line(float x1, float y1, float x2, float y2) {
    drawFVector(x1, y1, x2, y2);
    return;
    float len = sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));
    // use 40 per full horizontal and vertical line, thus 56 per diagonal
    int points = len*20.0;
    if (do_debug) {
        Serial.print("Line points:");
        Serial.println(points);
        }
    draw_line_points(x1, y1, x2, y2, points);
}


/* 
 *  7-segment Charactor Generator
 *  
 */
const float chardelta = 50.0 / 1024.0;
float mvxtab[8] = { 0, chardelta, 0, -chardelta, 0, chardelta, 0};
float mvytab[8] = { -chardelta, 0, chardelta, 0, chardelta, 0, -chardelta };
void drawCharacter(float x0, float y0, byte segs) {
    
    byte mask = 0x40;
    float x1 = x0;
    float y1 = y0;
    float x2, y2;
    // Serial.println(segs, BIN);
    for (int i=0; i < 8; ++i) {
        x2 = x1 + mvxtab[i];
        y2 = y1 + mvytab[i];

        if (mask & segs) {
            /*
            Serial.print(mvxtab[i]);
            Serial.print(":");
            Serial.print(mvytab[i]);
            Serial.print(" ");
            Serial.print(x1);
            Serial.print("/");
            Serial.print(y1);
            Serial.print(" -> ");
            Serial.print(x2);
            Serial.print("/");
            Serial.print(y2);
            Serial.print(" & ");
            Serial.println(mask);
            */
            drawFVector(x1, y1, x2, y2);
        }
        mask = mask >> 1;
        x1 = x2;
        y1 = y2;
    }
}

byte digits[10] = { 0b1110111, 0b0010001, 0b1101011, 0b0111011, 0b0011101,
                    0b0111110, 0b1111110, 0b0010011, 0b1111111, 0b0111111  };


void drawRect(float x, float y, float dx, float dy) {
   draw_line(x-dx, y-dy, x+dx, y-dy);
   draw_line(x-dx, y+dy, x+dy, y+dy);   
   draw_line(x+dx, y-dy, x-dx, y-dy);
   draw_line(x-dx, y+dy, x+dx, y+dy);                
}

/** 
    OXO / noughts and crosses /  tic-tac-toe
    Radom computer play
**/

enum oxo_what { oxo_free, oxo_nought, oxo_cross};
enum oxo_what oxo_state[9];
const float oxo_rad = 0.15;

int oxo_show() {
    int rc = -1;
    int i;
    for (i = 0; i < 9; ++i) {
        float x = 0.5 * (-1 + i % 3);
        float y = 0.5 * (1 - i / 3);
        if (do_debug) {
            Serial.print(i);
            Serial.print(": ");
            Serial.print(x);
            Serial.print(", ");
            Serial.print(y);
            Serial.print(" -> ");
            Serial.println(oxo_state[i]);
        }
        switch (oxo_state[i]) {
            case oxo_free: 
                // need point for light gun
                showFPoint(x, y);
                if (digitalRead(lightPin) == LOW)
                    rc = i;
                break;
            case oxo_nought:
                draw_circle(x, y , oxo_rad);
                // showFPoint(x, y);
                break;
            case oxo_cross:
                // drawRect(x, y, oxo_rad*1.3, oxo_rad*1.3);
                // as four lines from the middle
                drawFVector(x, y, x+oxo_rad, y+oxo_rad);
                drawFVector(x, y, x+oxo_rad, y-oxo_rad);
                drawFVector(x, y, x-oxo_rad, y+oxo_rad);
                drawFVector(x, y, x-oxo_rad, y-oxo_rad);
                // showFPoint(x, y);
                break;
        }  
    }
    return rc;
}

/*  
    play oxo
*/
void do_oxo() {
    // testing: just show a random pattern
    for (int i=0; i < 9; ++i) {
        oxo_state[i] = (enum oxo_what) random (oxo_free, oxo_cross+1);
        }
    while (digitalRead(keyPin) == HIGH) {
        int hit = oxo_show();
        if (hit >= 0)
            oxo_state[hit] = (enum oxo_what) random (oxo_nought, oxo_cross+1);
        // clear if full
        bool isfull = true;
        for (int i=0; i < 9; ++i) { 
            if (oxo_state[i] == oxo_free) {
                isfull = false;
                break;
            }
        }
        if (isfull) {
            for (int i=0; i < 9; ++i)
                oxo_state[i] = oxo_free;
        } 
    }
    
    // delay(300);
}
    

/**
    Bouncing ball 
    The ground line is drawn stepwise with each y-point
**/

void do_bounce() {
  
    const float gravi = 0.02;
    const float ground = -0.5;
    const float repel = -0.8;     // reflection on ground with loss 
    const float xstep = 0.02;      // advance in x direction
    const float xborder = 0.9;    // right border = - left border

    static float xpos = 1.0;       // restart
    static float ypos; 
    static float yspeed;  

    
   // compute speed
    yspeed += gravi;

    // compute position
    ypos -= yspeed;
    if (ypos < ground) {
        yspeed = yspeed * repel;
        ypos = ground;
    }            
        
    // advance x
    xpos += xstep;
    
    // check if start or restart 
    if (xpos > xborder) {
        xpos = -xborder;
        ypos = 0.6;
        yspeed = 0.1;
        // Serial.println("Ground ");
    }

    // plot the point
    showFPoint(xpos, ypos);
    // plot the x-axis
    showFPoint(xpos, ground);

    if (do_debug) {
        Serial.print("x:");
        Serial.print(xpos);
        Serial.print(", y:");
        Serial.print(ypos);
        Serial.print(", v:");
        Serial.print(yspeed);
        Serial.println();
        delay(50);
    }
       
}

// convert degreed to radians
float deg2rad(float x) {
    return 6.282*x/360;
}

/*
  Simple ballistic Rocket launch
  without air resistance
*/
void do_rocket(int mode) {
    // gravitation 
    const float grav = 0.003;
    // launch angle in degrees
    const float launchdir = 87.0;
    // fuel left
    float fuel = 1.0;
    // rocket speed
    float xspeed = 0.0, yspeed = 0.0;
    // rocket position
    float xpos = -0.9, ypos = 0.0;
    // acceleration per fuel unit
    const float accel = 0.005;
    // 
    const float burn = 0.05;
    
    // upon launch, set inital speeds
    xspeed = 0.01*cos(deg2rad(launchdir));
    yspeed = 0.01*sin(deg2rad(launchdir));

    
    // main loop: accelerate while fuel, show fuel and speed
    while (ypos >= -0.1 && ypos < 1.0 & xpos < 1.0) {
        float speed = sqrt(xspeed*xspeed + yspeed*yspeed);
        // accelerate if still fuel
        if (fuel > 0.0) {
            // no need to calculate flight angle, just the speed
            xspeed += xspeed / speed * accel;
            yspeed += yspeed / speed * accel;
            fuel -= burn;
        }
        // gavitation is always in y direction
        yspeed -= grav;
        
        // integrate to positions
        xpos += xspeed;
        ypos += yspeed;
        
        if (do_debug) {
            Serial.print("speed:");
            Serial.print(xspeed);
            Serial.print(",");
            Serial.print(yspeed);
            Serial.print(" pos:");
            Serial.print(xpos);
            Serial.print(",");
            Serial.print(ypos);
            Serial.print(" fuel:");
            Serial.print(fuel);
            Serial.print(" speed:");
            Serial.print(speed);
            Serial.println();
        }

        /*
         * Display the current state
         */

        // always actual point and base line
        showFPoint(xpos, ypos);
        drawFVector(-1.0, 0.0, 1.0, 0.0);
        drawCharacter(0.0, -0.8, digits[mode]);

        // show fuel as bar at the left side
        drawFVector(-0.99, 0.0, -0.99, fuel);
        showFPoint(-0.99, fuel);   // show end point
        
        
        // mode 0 and 1: 
        if (mode == 0 || mode == 1) {   
            // show velocity
            drawFVector(0.99, 0.0, 0.99, speed*10.0);
            showFPoint(0.99, 0.0 + speed*10.0);
            delay(5);   // compensate for the character display)
        }


        int fueli = fuel*100;
        int speedi = speed*1000;
        
        // mode 1 and 2:
        if (mode == 1 || mode == 2) {
           drawCharacter(-0.9, -0.3, digits[fueli / 10]);
           drawCharacter(-0.8, -0.3, digits[fueli % 10]);
           drawCharacter(0.8, -0.3, digits[speedi / 10]);
           drawCharacter(0.9, -0.3, digits[speedi % 10]);
        } 

        // mode 2: speed vector 
        if (mode == 2) {
            drawFVector(xpos, ypos, xpos + 5*xspeed, ypos + 5*yspeed);          
        }
        if (digitalRead(keyPin) == LOW)
            return;
        
    }
    
    
}


/*
    Central loop
*/
enum Modes{ mode_line, mode_cir, mode_digits, mode_bounce, mode_rocket0, mode_rocket1, mode_rocket2, mode_oxo};
int mode = mode_line;
int oldmode = -1;
void loop() { 

    check_key();                    // advances mode
    switch (mode) {
        case mode_line:
            if (mode != oldmode)
                Serial.println("Line mode");
            draw_line(1.0, 1.0, -1.0, -1.0);
            draw_line(1.0, -1.0, -1.0, 1.0);
            draw_line(0.0, -1.0, 0.0, 1.0);
            draw_line(-1.0, 0.0, 1.0, 0.0);
            draw_line(-0.5, 0.0, 0.0, 0.5);
            draw_line(0.5, 0.0, 0.0, 0.5);
            draw_line(-0.5, 0.0, 0.0, -0.5);
            draw_line(0.5, 0.0, 0.0, -0.5);

            break;
            
        case mode_cir:
            if (mode != oldmode)
                Serial.println("Circle mode");
            draw_circle(0, 0, 1.0);
            draw_circle(0.5, 0.5, 0.2);
            break;
        case mode_digits:
            if (mode != oldmode)
                Serial.println("Digits mode");
            for (int i = 0; i < 10 ;  ++i) {
                drawCharacter(-0.5 + i * 0.1, 0.0, digits[i]);
            }
            delay(20);
            break;
        case mode_bounce:
            if (mode != oldmode)
                Serial.println("Bounce mode");
            do_bounce();
            break;
        case mode_rocket0:
            if (mode != oldmode)
                Serial.println("Rocket mode 0");
            do_rocket(0);
            break;
        case mode_rocket1:
            if (mode != oldmode)
                Serial.println("Rocket mode 1");
            do_rocket(1);
            break;
        case mode_rocket2:
            if (mode != oldmode)
                Serial.println("Rocket mode 2");
            do_rocket(2);
            break;
        case mode_oxo:
            if (mode != oldmode)
                Serial.println("OXO mode");
            do_oxo();
            break;
        default:
            Serial.print("Mode reset: ");
            Serial.println(mode);
            mode = 0;
            oldmode = -1;
            return;
    }
    oldmode = mode;
        
}

/*  
    Check key to advance mode
*/
// very dsimple version
void check_key() {
  if (digitalRead(keyPin) == HIGH)
    return;
  // debounce key press
  delay(30);    
  if (digitalRead(keyPin) == HIGH)
    return;
  // wait for release
  while (digitalRead(keyPin) == LOW)
    ;
  delay(20);    // debounce key relase
  mode += 1;    // any overflow corrected in loop()
  Serial.print("---------> new mode:");
  Serial.println(mode);

  
}


/**
  Initialisierung
**/

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  // Serial I/O
  Serial.begin(115200);
  int tries = 20;
  while (--tries && !Serial) {
      // wait for serial port to connect. Needed for native USB
      delay(100);
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
  }

  // Banner with version information
  Serial.println();
  Serial.println();
  Serial.print("CRT Test ");
  Serial.print(version);
  Serial.print(" Compiled: ");
  Serial.print(__DATE__);
  Serial.print(" ");
  Serial.println(__TIME__);
  Serial.println(MOSI);

  // SPI
  digitalWrite(SS, HIGH);
  pinMode(SS, OUTPUT);
  pinMode(MOSI, OUTPUT);
  pinMode(SCK, OUTPUT);
  
  // SPI initialisieren
  SPI.begin();


  // Position signal
  digitalWrite(pinPos, LOW);
  pinMode(pinPos, OUTPUT);

  // Move signal
  digitalWrite(pinMove, LOW);
  pinMode(pinMove, OUTPUT);
  
  // key pin
  pinMode(keyPin, INPUT_PULLUP);
  digitalWrite(keyPin, HIGH);

  // light gun pin
  pinMode(lightPin, INPUT_PULLUP);
  digitalWrite(lightPin, HIGH);
  
  // set debug mode if key is pressed on reset
  if (digitalRead(keyPin) == LOW)
    do_debug = true;

    

}
