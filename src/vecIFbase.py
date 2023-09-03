#!/usr/bin/env python3
# vi: ts=4
""" Basic functions for vector interface
"""

# 
import RPi.GPIO as gpio
import spidev
import time
import math
import random

#
version = "0.2a"

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
        
def getKeys():
    """ Key inquiry for the push button on the interface board
    and the four switches on the tap board(s).
    
    """
    # very preliminary
    if gpio.input(pin_isKey) == 0:
        return 1
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
    points = max(7, points)

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


print("vecIFbase: Version " + version)
# time of compilation -- how?
def vecIFopen():
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

    spi.open(0, 0)
    spi.max_speed_hz = 4000000
    print ("Initialised gpio and spi")
spi = spidev.SpiDev()

def vecIFclose():
    gpio.cleanup()
    spi.close()
