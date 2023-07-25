#!/usr/bin/env python3
# vi: ts=4
""" Stand-alone test for the WWI vector interface
    Shows some tests, switches to next by key
    Last one uses light pen
    
    uses floating point numbers for convenience,
    not (yet) fixed point fractions as in WWI
    
"""

# 
import RPi.GPIO as gpio
import spidev
import time
import math
import random

#
version = "0.1i"

# pin definitions in BCM numbering
pin_doMove = 17
pin_doDraw = 22
pin_enZ1 = 18
pin_enZ2 = 23
pin_isKey = 27
pin_isGun1 = 25
pin_isGun2 = 24
pin_isGun1on = 4
pin_isGun2on = 7
# SPI pins are defined by SPI interface

 
def floatfix(x):
    """ Converts floating point number to integer for D/A converter
        -1.0 ... +1.0 becomes 2048 +/- 2048
    """
    if (x > 1.0):
        return 4095;
    if (x < -1.0):
        return 0;
    return 2048 - int(x*2047);
    
def setDA(n, val):
    """ sets one D/A converter
        n: 0 or 1 for converter number
        val: float -1.0 ... +1.00
    """
    ival = floatfix(val)
    hival = ival // 256
    loval = ival % 256
    mask = 0x30
    if (n == 0):
        mask = mask | 0x80
    outv = [mask | hival, loval]
    spi.writebytes(outv)
    
    
move_delay = 25   # .0E-6
draw_delay = 55   # .0E-6
 
def delay_us(duration):
    stop = time.perf_counter_ns() + 1000 * duration
    while time.perf_counter_ns() < stop:
        time.sleep(0)
        
 
 
 

def movePoint(posx, posy):
    # move to destination
    setDA(0, posx)
    setDA(1, posy)
    gpio.output(pin_doMove, 1)
    delay_us(move_delay)
    #time.sleep(move_delay*1e-6)
    gpio.output(pin_doMove, 0)
                        
def drawSegment(speedx, speedy):		
    # set speed
    setDA(0, speedx)
    setDA(1, speedy)
    gpio.output(pin_doDraw, 1)
    delay_us(draw_delay)
    #time.sleep(draw_delay * 1e-6)
    gpio.output(pin_doDraw, 0)
 
wasPoint = False        # true after a point drawing

def drawSmallVector(posx, posy, speedx, speedy):
    """ Basic operation: Draw a vector with given speed
        As the endpoint is not directly given,
        but as a speed, the length is limited 
        so that the endpoint can be predicted precise enough.
        The draw mechanism draws for 50µs;
        with maximum speed, it draws 1/8 of the screen width.
        To draw a point, use zero speeds
    """
    movePoint(posx, posy)
    drawSegment(speedx, speedy)

    # reset point drawing flag
    global wasPoint
    wasPoint = False


    
def drawPoint(posx, posy):
    """ draw a point as a vector of length 0
    """

    drawSmallVector(posx, posy, 0.0, 0.0)
    
    # last one was a point drawing    
    global wasPoint
    wasPoint = True


        
"""
    The light gun has a trigger switch for one-shot operation:
    Only the first pulse after display of a point is valid;
    more are to be disabled while the trigger switch is still on.
    
    As no pulses are transmitted before the switch is on,
    the first such pulse (after display of a point) sets a flag
    to disable more (of this light gun).
    
    This flag is reset once the switch is off more than 50msec (debouncing)
"""

wasGunPulse1 = True          # if a pulse was delivered
gunTime1= 0.0
wasGunPulse2 = True          # if a pulse was delivered
gunTime2= 0.0
debounceGunTime = 0.05
    
  
def getLightGuns():
    """
        returns 0 if no light gun detected, or set the (two) lower bits
        
    """  
    global wasPoint, wasGunPulse1, gunTime1, wasGunPulse2, gunTime2, debounceTime
    # light gun signals are evaluated only if there was a point drawing
    if not wasPoint:
        return 0
    
    mask = 0
    # check if this is the first light gun pulse
    if not wasGunPulse1 and gpio.input(pin_isGun1) == 0:
        mask = 1
        wasGunPulse1 = True
    if not wasGunPulse2 and gpio.input(pin_isGun2) == 0:
        mask = mask | 2
        wasGunPulse2 = True
        
    if mask != 0:
        return mask
    
    # print(gpio.input(pin_isGun1on), gpio.input(pin_isGun2on))
    # debounce switch 1 
    if gpio.input(pin_isGun1on) == 0:
        # while switch is on, restart timer
        gunTime1 = time.time()
    else:
        # switch must be off some time (debounce)
        delta = time.time() - gunTime1
        if delta > debounceGunTime:
            wasGunPulse1 = False
            
    # debounce switch 2
    if gpio.input(pin_isGun2on) == 0:
        # while switch is on, restart timer
        gunTime2 = time.time()
    else:
        # switch must be off some time (debounce)
        delta = time.time() - gunTime2
        if delta > debounceGunTime:
            wasGunPulse2 = False

    return 0
        


def drawVector(x0, y0, x1, y1):
    """ General vector drawing
        if length exceeds the (short) maximum,
        a chain of segments is used without repostioning;
        however, to ensure accurate length,
        after half the way the vector is drawn
        from the end.
    """
    # determine distances 
    dx = x1 - x0;
    dy = y1 - y0;
    # required speed, may be larger that +/- 1.0 for long vectors
    sx = dx * 4.05				# more than 4.0 to avoid gaps
    sy = dy * 4.05
    
    # might be a short vector, then draw now (helps debugging)
    if abs(sx) <= 1.0 and abs(sy) <= 1.0 :
       drawSmallVector(x0, y0, sx, sy)
       return
       
    # determine number of segments, at least 1
    xsegs = 1 + math.floor(abs(sx))
    ysegs = 1 + math.floor(abs(sy))
    segs = max(xsegs, ysegs)
    # make it even number to switch exacly at the middle
    if segs % 2 == 1:
        segs += 1
    # reduce speed by number of segments
    sx = sx / segs;
    sy = sy / segs;
 
    # start the chain
    movePoint(x0, y0)
    for i in range(0, segs):
        # half way from the end go backwards
        if i == segs / 2:
            movePoint(x1, y1)
            sx = -sx
            sy = -sy
        drawSegment(sx, sy)

def drawCircle(x0, y0, r):
    """
    Draw a circle with center at (x,y) and radius r.
    TODO: properly truncate at border
    """
    # number of points
    points = int( 36.0 * r)
    # use a minimum of points
    points = max(12, points)

    x1 = x0
    y1 = y0 + r
    #movePoint(x1, y1)
    for i in range(1, points+1):
        if i % 6 == 1:
            movePoint(x1, y1)
        t = math.radians(i * 360/points)
        x2 = x0 + r*math.sin(t)
        y2 = y0 + r*math.cos(t)
        dx = x2 - x1
        dy = y2 - y1
        drawSegment(4.1*dx, 4.1*dy)
        x1 = x2
        y1 = y2
            
 
""" 
    7-segment Charactor Generator
"""
# nominal size is 7.0 and 8.5, but not for small screens
chardeltax = 7.0 / 1024.0;
chardeltay = 8.5 / 1024.0;
mvxtab = [ 0.0, chardeltax, 0.0, -chardeltax, 0.0, chardeltax, 0.0];
mvytab = [ -chardeltay, 0.0, chardeltay, 0.0, chardeltay, 0.0, -chardeltay]
digits = [ 0b1110111, 0b0010001, 0b1101011, 0b0111011, 0b0011101,
                    0b0111110, 0b1111110, 0b0010011, 0b1111111, 0b0111111  ]
                    
def drawCharacter(x0, y0, segs, enlarge=4.0) :
    
    mask = 0x40;
    x1 = x0;
    y1 = y0;
    toMove = True
    # movePoint(x1, y1)
    # drawSegment(0,0)
    for i in range(0, 7):
        dx = mvxtab[i]*enlarge;
        dy = mvytab[i]*enlarge;
        if mask & segs:
            if toMove:
                movePoint(x1, y1)
                toMove = False
            drawSegment(4*dx, 4*dy)
        else:
            toMove = True
        x1 += dx
        y1 += dy
        mask = mask >> 1;
    
    global wasPoint
    wasPoint = False


""" Give navigation point bottom left and right
    need to wait until gun is no longer active
"""
def navi():
    drawPoint(-0.9, -0.8)
    if getLightGuns():
        # time.sleep(0.5)
        return -1
        
    drawPoint(0.9, -0.8)
    if getLightGuns():
        # time.sleep(0.5)
        return +1
    return 0
    

"""
    Bouncing ball 
    The ground line is either shown with points (mode = 1)
    or as a a (long) vector for each point (mode=2)
    Not yet with hole..
"""
def show_bounce(mode) :
  
    gravi = 0.003
    ground = -0.5
    repel = -0.85       # reflection on ground with loss 
    xstep = 0.007       # advance in x direction
    xborder = 0.9       # right border 

    xpos = -xborder        # restart
    ypos = 0.5
    yspeed = 0.0

    while xpos < xborder:
        # compute speed
        yspeed += gravi

        # compute position
        ypos -= yspeed
        if ypos < ground:
            yspeed = yspeed * repel
            ypos = ground
            
        # advance x
        xpos += xstep

        # plot the point
        drawPoint(xpos, ypos)
        # plot the axes
        if (mode == 2):
            drawVector(-xborder, ground, xborder, ground)
            drawVector(-xborder, 0.5, -xborder, ground)
        
        rc = navi()
        if (rc != 0): return rc
 
        # check for stop
        if gpio.input(pin_isKey) == 0:
            time.sleep(0.5)
            return 1;
    if (mode == 1):
        # draw a chain of dots
        for i in range(0,100):
             drawPoint(xborder*(-1+i/50), ground)
    return 0
        
""" 
    OXO / noughts and crosses /  tic-tac-toe
    Radom computer play
"""

oxo_state = []
for i in range(1,10): oxo_state.append(0)

oxo_rad = 0.15

def oxo_show():
    rc = -1
    for i in range(0, 9):
        x = 0.5 * (-1 + i % 3)
        y = 0.5 * (1 - i // 3)
        state = oxo_state[i]
        if state == 0:  # free
                # need a point for the light gun
                drawPoint(x, y)
                if getLightGuns():
                    return i
        if state == 1:
                drawCircle(x, y , oxo_rad)
        if state == 2:
                drawVector(x, y, x+oxo_rad, y+oxo_rad)
                drawVector(x, y, x+oxo_rad, y-oxo_rad)
                drawVector(x, y, x-oxo_rad, y+oxo_rad)
                drawVector(x, y, x-oxo_rad, y-oxo_rad)
    return -1


"""  
    play oxo
"""
def do_oxo() :
    # start pattern
    for i in range(0, 9):
        oxo_state[i] = random.randrange(3)
        
    while gpio.input(pin_isKey) == 1 :
        hit = oxo_show()
        if hit >= 0:
            oxo_state[hit] = random.randrange(1, 3)
        # clear if full
        isfull = True
        for i in range(9) : 
            if oxo_state[i] == 0 :
                isfull = False
                break
        if (isfull) :
            for i in range(9):
                oxo_state[i] = 0
            oxo_show()
            # time.sleep(0.5)
         
        rc = navi()
        if (rc != 0): return rc
    return 0


"""
  Simple ballistic Rocket launch
  without air resistance
"""
def do_rocket(mode) :
    # gravitation 
    grav = 0.0028
    # launch angle in degrees
    launchdir = 87.0
    # fuel left
    fuel = 1.0
    # rocket speed
    xspeed = 0.0
    yspeed = 0.0
    # rocket position
    xpos = -0.9
    ypos = 0.0
    # acceleration per fuel unit
    accel = 0.004
    # 
    burn = 0.04
    
    # upon launch, set inital speeds
    xspeed = 0.01 * math.cos(math.radians(launchdir))
    yspeed = 0.01 * math.sin(math.radians(launchdir))

    
    # main loop: accelerate while fuel, show fuel and speed
    cnt = 99
    while ypos >= -0.1 and ypos < 1.0 and xpos < 1.0 :
        speed = math.sqrt(xspeed*xspeed + yspeed*yspeed)
        cnt += 1
        if cnt > 3:
          cnt = 0
          # accelerate if still fuel
          if fuel > 0.0 :
              # no need to calculate flight angle, just the speed
              xspeed += xspeed / speed * accel
              yspeed += yspeed / speed * accel
              fuel -= burn
        
          # gavitation is always in y direction
          yspeed -= grav
 
          # integrate to positions
          xpos += xspeed
          ypos += yspeed
        
        # always actual point and base line
        drawPoint(xpos, ypos)
        drawVector(-1.0, 0.0, 1.0, 0.0)
        #drawCharacter(0.0, -0.8, digits[mode])

        # show fuel as bar at the left side
        if fuel > 0.0:
            drawVector(-0.99, 0.0, -0.99, fuel)
        # drawPoint(-0.99, fuel)   # show end point
        
        
        # mode 0 and 1: 
        if mode == 0 or mode == 1 :
            # show velocity
            drawVector(0.99, 0.0, 0.99, speed*10.0)
            #drawPoint(0.99, 0.0 + speed*10.0)

        fueli = int(fuel*100)
        speedi = int(speed*1000)
 
        # mode 1 and 2: show fuel, skip to reduce visible luminance
        if cnt == 1 and (mode == 1 or mode == 2) :
           drawCharacter(-0.9, -0.3, digits[fueli // 10])
           drawCharacter(-0.8, -0.3, digits[fueli % 10])
           drawCharacter(0.8, -0.3, digits[speedi // 10])
           drawCharacter(0.9, -0.3, digits[speedi % 10])
         

        # mode 2: speed vector 
        if mode == 2 :
            drawVector(xpos, ypos, xpos + 8*xspeed, ypos + 8*yspeed)          
        
        if gpio.input(pin_isKey) == 0:
            time.sleep(0.5)
            return 1

        rc = navi()
        if (rc != 0): return rc
    return 0


def show_circles():
    drawPoint(0, 0)
    drawCircle(0, 0, 0.9)
    drawCircle(0.5, 0.5, 0.2)
    #drawCircle(0.5, 0.5, 0.6)
    #drawVector(1.0, 1.0, 1.0, -1.0)
    #drawVector(1.0, 1.0, -1.0, 1.0)
    #drawVector(-1.0, -1.0, 1.0, -1.0)
    #drawVector(-1.0, -1.0,  -1.0, 1.0)
    rc = navi()
    return rc
    


def fig1():
    #drawPoint(1.0, 1.0)
    drawVector(1.0, 1.0, -1.0, -1.0)
    drawVector(1.0, -1.0, -1.0, 1.0)
    #drawPoint(-1.0, -1.0)
    drawVector(0.0, -1.0, 0.0, 1.0)
    drawVector(-1.0, 0.0, 1.0, 0.0)
    #drawPoint(-0.5, 0.0);
    #drawPoint(0.0, 0.5);
    drawVector(-0.2, 0.0, 0.0, 0.2)
    drawVector(0.2, 0.0, 0.0, 0.2)
    drawVector(-0.5, 0.0, 0.0, -0.5)
    drawVector(0.5, 0.0, 0.0, -0.5)    
    rc = navi()
    return rc
 
def loop():
    mode = 1
    omode = mode
    while True:
        #drawCharacter(0, 0, digits[8])
        #drawCharacter(-0.5, 0, digits[1])
        #continue;
        if mode > 9:
             mode = 1
        if mode < 1:
             mode = 9
        if omode != mode:
             print("Mode: " + str(mode));
             omode = mode
 
        if mode == 1:
            mode += fig1()
        if mode == 2:
            mode += show_circles()
        if mode == 3:
            mode += show_bounce(1)
        if mode == 4:
            mode += show_bounce(2)
        if mode == 5:
            for i in range(0,10):
                drawCharacter(-0.5 + i * 0.1, 0.0, digits[i])
            rc = navi()
            mode += rc
 
        if mode == 6:
            mode += do_rocket(0)
        if mode == 7:
            mode += do_rocket(1)
        if mode == 8:
            mode += do_rocket(2)
        if mode == 9:
            mode += do_oxo()
 
        if gpio.input(pin_isKey) == 0:
            mode += 1
            print(mode);
            time.sleep(1.0)
            if gpio.input(pin_isKey) == 0:
                return
        
print("Version " + version)
# time of compilation -- how?

# use global variables for gpio and spi
# initialize
gpio.setmode(gpio.BCM)
gpio.setup(pin_doMove, gpio.OUT)
gpio.output(pin_doMove, 0)
gpio.setup(pin_doDraw, gpio.OUT)
gpio.output(pin_doDraw, 0)
gpio.setup(pin_isKey, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(pin_isGun1, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(pin_isGun2, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(pin_isGun1on, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(pin_isGun2on, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(pin_enZ1, gpio.OUT)
gpio.setup(pin_enZ2, gpio.OUT)
# temp: enable both
gpio.output(pin_enZ1, 0)  # inverted: 0 is enable, 1 is disable
gpio.output(pin_enZ2, 0)

spi = spidev.SpiDev()
spi.open(0, 0)
#spi.max_speed_hz = 4000000
 
# run the main loop
try:
    loop()
except KeyboardInterrupt:
    print("Cancelled")
finally:
    gpio.cleanup()
    spi.close()
    print("Stopped.")
 
