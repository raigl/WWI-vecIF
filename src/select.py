#!/usr/bin/env python3
# vi: ts=4
""" Select a code to return to shell

    May be used for a simple menu control by numbers
    
    The code is entered by the four switches on the tap boards.
    If the push button is pressed, this programmed terminates
    with the code selected. 
    
    The code can also be set with the lightgun selecting one of 16 points;
    then, the corresponding LEDs are activated.
    
    Result is the bitwise or of the code selected by the lightgun and the keys.
    
"""

# 
import sys
import time
import vecIFbase as base

def drawNumber(x, y, num):
    base.drawCharacter(x, y, base.digits[num // 10], enlarge=8.0)
    base.drawCharacter(x+0.1, y, base.digits[num % 10], enlarge=8.0)
    
def do_show() :
    
    # get LEDs
    res = base.getKeys()
    
    # draw pattern for light gun
    for i in range(0,16):
        x = i % 4
        y = int(i / 4)
        x = -0.6 + x * 0.4
        y = -0.7 + y * 0.4
        drawNumber(x+0.05, y, i)
        base.drawPoint(x, y)
        if 0 < base.getLightGuns():
            for b in [1, 2, 3, 4]:
                m = 2**(b-1)
                base.setKey(b, i&m)
    
    drawNumber(0, 0.9, int(res/2))
             
    return res

def loop():
    res = 0
    while 0 == res % 2:
        res = do_show()
    # wait until PB is released		
    while 1 == base.getKeys() % 2:
        time.sleep(0.1)
    return int(res/2)

# run the main loop
try:
    base.vecIFopen()
    while True:
      for i in [1, 2, 3, 4]:
        base.setKey(i, 1)
        time.sleep(0.1)
      for i in [4, 3, 2, 1]:
        base.setKey(i, 0)
        time.sleep(0.1)
      if 0 == base.getKeys()%2:
        break;
    res = loop()
    sys.exit(res)
except KeyboardInterrupt:
    print("Cancelled")
finally:
    base.vecIFclose()
    print("Stopped.")
 
 
 
 
 
 
 
 
 
