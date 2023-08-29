Whirlwind I Hardware Vector Interface

Author: Rainer Glaschick, Paderborn
Date: 2023-05-13 2023-08-29
Version: 1.0c

\CSS all .over {text-decoration: overline;}

Revision target
===============
For the transition to the revised Interface that will be version 1.0,
the planned changes are described below. 

Using a display bus and additional tap boards better models the 
original situation, even if there are currently only two displays useable.

In any case, the selection of the output intensification is done
via switches on (or connected to) the tap boards (and not per software).

To have a bank of switches and LEDs, the I²C bus is available on a second
connector (4 pins). 

 
Output
------

Instead of two outputs for X/Y/Z and two connectors for Lightguns,
a display bus is used with tap boards. 
The number of pins depends on the amount of logic in the tap boards 
and corresponding flexibility.

In case that rugged connections with proper (round, not ribbon) cables
are required, use of the common 15-pin D-SUB connectors is proposed
using these lines:
- X, Y 
- Z1, Z2  
- L1, L2
- +5V
- GPIO27 (Push-Button)
- GPIO5, GPIO6, GPIO20, GPIO21
- 3x GND

Inversion of the intensification signals Z1 and Z2 is provided
on the tap boards, as this uses only two MOS-FETs (and a switch).

The GPIO27 is the same as the key on the interface and may be connected
to ground by a momentary push button on the tap board. 
No LEDs should be connected to this button.
Preferred use is as exit if pressed more than 1 sec (software feature).

The other four GPIO lines are logically open-collector lines that can sink
upto 2mA each. 
If grounded by a switch (or key), software can determine the low state
(which also lights the LED) and act accordingly.
 
All GPIO-lines have pullup resistors of 15k (5V) and 10k (3.3V) 
and are bidirectional converted from 3.3V to 5V, see NXP AN10441.

As a soldering option, instead of GPIO20 and GPIO21, the inverted
intensification signals may be used, as this is just a layout option.

If a smaller connector is desired, a 9 pin D-Sub may be used;
the pin layout provides X, Y, Z1, Z2, L1, L2, 5V and 2x ground,
thus no keys or lamps and no inverted intensification.

On the board, a 2.54mm 2x8 pin header for ribbon connectors is used,
pin 16 unused.  


Tap board
-----------

A tap board has at least:
- two trim potentioemeters (10 kΩ) for the X and Y outputs 
- two (manual) switches to select Z1 or Z2 or both.
- one light gun connection
- one pushbutton 
- four switches with LEDs

To select both, Z1 and Z2, schottky diodes driving a 6.8kΩ resistor 
should work well, although (short) vectors and character segments
might be slightly shortened. 
In that case, CMOS invertes should be used.
(The time constant for a 100pF load is 0.68µs, which is less than 2%
of the 50µs strobe signal).
Another configuration switch (not to be used during normal operation)
inverts the intensification signal. 

The pushbutton and the switches are described in the previous section.

While two lightguns driving the same line will not damage the system, 
a configuration jumper should be used to select the light gun input line,
not a switch to change it while in operation. 

A special tap board may contain a voltage booster providing 30V from the 5V
supply to have a larger voltage swing at the Z connector to the display,
in particular for older oscilloscopes.


I²C Bus
--------

By providing the I²C bus on a connector of its own,
a bank of panel switches and lights may be connected.
Upto 8 PCF 8574 port expanders for 8 lamps or switches may
be used. 

As with the tap board, the outputs of the port expander
are open-drain, here with a dynamic and static pullup. 

So each line will lighten the lamp if connected to ground,
and either the user or the computer can connect to ground (and light the lamp).

It the computer wants to find out the switches, it would temporarily
switch all off and see which ones are still on.
Same procedure for the user. 



Reference voltage
-----------

A reference of 1.024V is required for the integrators to define
the zero speed for displaying points.

The output amplifiers are designed for a 3.3V reference to 
change the internal 1.024&plusmn;1.024V to symmetrical &plusmn;3.076V. 

The board may either use a LP2950-3.3 linear regulator from 5V,
or use the 3.3V from the Raspi board directly.

For the integrator's 1.024V, either a trim pot is used to calibrate
the voltage.

The output's zero voltage and amplitude is normally not very critical.
A voltage divider with 12kΩ and 10kΩ is used giving fairly good results.
Place for two larger resistors, e.g. 100kΩ and 150kΩ, is provided for 
better results, depending on the accuracy of the 3.3V reference.


5V protection
-------------

A 0.5A fuse is inserted just before the connector to the Raspi.
Normally more current can be drawn, only limited by the power supply
(minus the current drawn be the Raspi and connected USB perpherals)
and the copper tracks on the Raspi.  
So the tap boards should not use more then 0.4A together,
i.e. 0.2A or 1W each for two.

Integrator switches
--------

The standard 4066 CMOS switches actually work fine; the vertical detours
seen on the TEK 611 have not manifested on the oscilloscopes used so far. 
And because it is only on the horizontal signal, it might be 
a hardware problem of the TEK 611,
Although the datasheet for the 4066 gives gives 50mV crosstalk from the 
control signal to the data path, it is in the integration path and thus
will not propagate to the output. 
Although Analog Devices produces a better chip (ADG431), a change 
seems currently not justified, as the 4066 is far better available.


Intensivation strobe length
----------------------------

A trim potentiometer will allow to precisely set the strobe length of 
a vector draw. 
Note that the starting (negative) slope of the intensivation signal
must not be delayed, at this would compromise the starting point of the vector,
in particular the stroke of a character.

Drawing points is not affected. 



Ribbon input connector
-----------------------

Changed from 26 to 40 pins.

This allows to use additional pins connected to the bus.

                            



 

Introduction
============

To connect a Whirlwind I (WWI) machine (emulated or simulated) to a physical CRT
not in raster, but in X-Y-Z-mode,
a hardware interface supports drawing of vectors.
Single points are drawn as zero-length vectors.

The board has a dual 12-Bit D/A converter (MCP 4822) controlled by SPI,
and two digital inputs to set the starting point and to draw a (short) vector
with a given velocity. 

As a vector is drawn by setting the direction and velocity,
the destination point is not defined by its absoulte coordinates.
Although the analog hardware is quite precise, 
the vector size is limited to a fraction of the sceen.
Thus, long vectors must be composed from shorter ones, 
as to restart at a known location.  

The board can handle two CRT's and lightguns.

The design was inspired by the Vectrex game console, 
but allows to set a starting point directly. 

Design
======

The interface is essentially an settable integrator 
for X and Y deflection voltages.
The output of the board provides &plusmn;2.5V on its (analog) output.

Normal use is as follows:
- Transmit x and y coordinates of the starting point via SPI to the A/D converter
- Strobe the 'doMOVE' signal to set initial values of the integrators
- Transmit x and y values for the speed via SPI
- Strobe the 'doDRAW' signal to draw the vector with the actually set speed

The x and y coordinates are 12 bit values producing an output range 
of &plusmn;2.5V. Thus:
- 2047 is 0V
- 0000 is -2.5V
- 4096 is +2.5V
- 1024 is -1.25V 
- 3072 is +1.25V.

The duration of the 'doMOVE' signal must be at least 30µs long to have the
initial value settled, due to the output resitance of the op amp of about 100Ω
to load the 10nF integration capacitor.

It must be inactive again before the draw signal is used.

While the 'doDRAW' (and the 'doMOVE') signal is inactive, the integrators are halted,
i.e. do not change their current value for seconds. 
Once the 'doDRAW' signal is active, the current x and y values
give the (relative) speed at which the coordinates are changed.
These are also 12-Bit values with the same encoding as above,
i.e. 2047 is zero, which means no change.
The values of 0 and 4095 mean full speed in decreasing and increasing
the coordinate voltages.

As the time constant of the integrators is 20kΩ*10nF=200µs,
a 400µs strobe with maximum speed input (0 or 4097) would be requied
to move from one border to the other one. 
Shorter vectors could be drawn either by decreasing the speed voltage
or strobe time.
As the controlling computer may not be able to produce short pulses
with e.g. 1µs resolution or accuracy, 
the 'MOVE' pulse is automatically truncated (internally) to 50µs.
Thus, the maximum possible move is a difference of 0.25 in either direction
which is 12.5% of the screen width.
To draw a line from one border to the other, eight or more moves must be used. 
It is assumend that normally the controlling computer will generate 
a 60µs pulse and set the speed to control the length of the vector
according to a 50µs move.
Note that WWI could only draw vectors of half the length.

Although the interface would allow to chain moves without repositioning
the starting point, the time to set the starting point should be
invested.  

An intensification signal for the electron beam (z-axis) 
is automatically generated while the integration runs,
i.e. during the 'doDRAW' signal, thus truncated to 50µs.


Single point display
++++++++++++++++++++

In order to show a single point, the starting point is moved to
and a vector of zero speed drawn.


Calculating the speed amount
+++++++++++++++++++++++++++++

For each dimension, the speed is calculated by the difference
of the end and start coordinate.

Using fixed point numbers for coordinates, the middle of the screen
is at (0.0, 0.0) and (-1.0, -1.0) is the lower left corner.

Thus, a maximum speed of -1.0 or +1.0 moves the point by 0.25.

In WWI, the vector length is given in upto 31 steps of 2\<sup>-8\</sup> units.
To move the point one unit, thus the speed must be 4\<sup>-6\</sup> per unit.
As the resolution is 11 bit (without sign), the vector length in the range of 0..31
is  multiplied by 64 (and added to 2048 finally). 
 

Vector intensities
++++++++++++++++++

To draw vectors of uniform intensity, the effective speed in the
direction of the movement must be the same for all vectors.
Then, the length of the vector is determined by the duration 
of movement. 

This may be one reason that the vectors in WWI are limited in length, 
so that long vectors -- if ever required -- are shown as a chain
of short ones of uniform intensity. 

Drawing circles
+++++++++++++++

Circles should be drawn as short vectors. 
A number of 60 vectors for a full screen circle is in general
visibly satisfying.
Multiplying the radius (in the range of 0.0 to 1.0) with 60.0
and truncating the result as integer number of points will speed up
small circles.
A minimum of 6 points is recommended. 

Character display
+++++++++++++++++

Character display is currently done in software by drawing
those vectors that are intensified;
thus it takes upto 0.7ms  per character, as a single line uses 30µs + 60µs = 90µs. 



Lightgun
++++++++

The lightgun uses a 3-pin connector with ground, +5V and a single input.

The sensor OPL801-OC can be connected without electronics;
the input has a pull-up of 4.7kΩ to 5V.

As the controlling computer might not be quick enough to catch a short pulse,
it sets a flipflop which is reset with each new position move.

In order to avoid false triggers if the lightgun is pointed outside
the screen, only the starting edge is used to set the flip-flop.
Continuous light still generates one signal when beginning,
but it is unlikely that the right time window will accidentially be used.

There is no electrical correlation of the lightgun with a specific screen.
Nevertheless is this no source of confusion, i.e. by giving a trigger
if the lighted dot is on a different screen. Of course, if the user of 
lightgun 2 normally used for screen 2 picks a dot on screen 1, this will
be valid and sensed. But as the flag is valid only until the next change
in coordinates, it will not be determined by screen 2 unless both show
the same dots, in which case it is what is expected.



More CRTs
+++++++++

To support two (or more) CRTs and lightguns,
the deflection circuits remain the same,
as the X and Y signals are common to all.

Two additional GPIO outputs enable the corresponding Z-Signals.
The polarity is selected for each on board.

One additional input is required for the second light pen. 

 



Mechanical and electrical hints
+++++++++++++++++++++++++++++++

The interface is a small board with the following connectors:

Output is a 8-pin connector for the X-, Y- and Z-signals plus
a ground pin for each for easier cable connection.
The signals are &plusmn;2.5V to ground.

Input is wired to 26-pin Raspberry double row pinning 
for simple connection to the latter;
to use an Arduino, a shield providing this connector is recommended.

The SPI interface must use the levels defined by VADC, which is normally
either 3.3V or 5.0V. The D/A-converter works from 2.7 to 5.5V,
as it has an internal referece of 2.048V. 
So it may be used with Raspberry Pi boards at 3.3V 
and also with older design that use 5V logical levels.

The +5V input is used as supply for the internal logic and as reference 
for the conversion to &plusmn;2.5V; 
the necessary negative supply is generated on board.

The two logic inputs may be any logic; <2V for inactive
and >3V for active. 


The GPIO Pins used are (besides SPI):
- 17: Move to vector start position
- 22: Draw vector for 50µs
- 23: Enable Z-strobe 1
- 24: Lightgun 1 input
- 25: Lightgun 2 input
- 18: Enable Z strobe 2
- 27: Keyswitch on board



Various
=======

Z-inputs
++++++++

For some Oszilloscopes with Z-input (e.g. HM 512-2),
the signal is assumed to be short negative pulses
darkening a (small part) of the signal shown
as a time or event marker.
As the coupling is via capacitor to the high voltage,
a clamp diode is required to determine the default without pulses.
This diode is often such that negative pulses reduce the intensity,
so that normally the beam is visible.
To support positive pulses to show the beam, the diode
must be reversed. 
If a switch is used, check for sufficient voltage withstanding,
or use an appropriate relay. 


Split power
+++++++++++

The current design uses a D/A converter (MCP4821) that runs equally well
from 3.3V and 5.0V supplies, including logic, if 1.024&plusmn;1.024V are selected.

All logic in- and outputs use MOS-FETs (2N7000) that allow both voltage levels. 

The analog section uses the output voltage range of the D/A converter,
i.e. 0V to 2.048V, with 1.024V as analog reference zero.
An output stage converts this to &plusmn;2.5V;
the required negative supply is provided on board.






 
