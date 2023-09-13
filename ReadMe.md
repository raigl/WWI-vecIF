# Whirlwind I Vector Graphics Interface

For showing a Whirlwind programme's output, a small hardware
generates vector strokes on X/Y/Z oszilloskopes
and allows to attach light guns.
Guy Fedorkow's WWI simulator (https://github.com/raigl/WWI-vecIF) running on a Raspberry (B+) 
can drive the interface and run some original WWI programmes.


## Directories

<dl>
<dt> CAD   <dd> 3D Light gun case 3D files 
<dt> DOC   <dd> Documentation (own and collected)  
<dt> KiCad <dd> Schematics and PCB drawings
<dt> src   <dd> Python and Arduino source
</dl>

## Versions

0.3     Working prototype

1.0     Redesigned


## Basics

The interface allows to draw (short) vectors for two channels
on an analog x/y/z display, e.g. an oszilloscope.
Points are drawn as zero-length vectors.

The D/A converter used has an internal reference of 2.048V, 12 bits
resolution and produces 0..2.047V in steps of 1/4096. 
WWI uses 10 bits plus sign, i.e. +/- 1023.
Thus the coordinate unit corresponds to 1mV internally.
The output state amplifies by 3 (and shifts to zero base), 
thus supplies +/- 3V and 3mV per unit. 

Drawing a vector is done by setting two integrators to the start point,
then provide a speed and start the integrators for 50µs,
which at the same time provides a strobe for the z axis.
With maximum speed (-1023 or +1023, i.e. 0 or 2.047V), the movement is 1/8 of the full coordinate range -1.0 .. +1.0,
i.e. 256 coordinate units or 250mV. 
Thus coordinate differences must be multiplied by 4 to set the speed. 
Longer vectors must be drawn as segments.

The display should be setup such that increasing both coordinates
moves the point right and up.

Character display not done by hardware as in WWI,
but by software as a chain of segments;
this requires a precise setup of the mid voltage
to 1.023V; otherwise the characters are blurred.

Vector drawing was inspried by the Vectrex gaming console.
Original WWI hardware used a more elaborate method:
A fixed ramp generator (for each coordinate) was multiplied by
the vector delta coordinate provided. 
The advantage is that the strobe at start and end points could be
slightly before and after the end of the ramp, ensuring
precise start and end points.


## Displays
 
To display the vectors, the display device must have analog inputs for X/Y mode
and a Z input for intensitiy modulation.

To better mimic the original, the vector interface board provides
a display bus connector to be used with one or more display tap boards,
which are located directly near a display.

Each display tap board has two switches to select one or both intensification
lines (the original had 15). 

A light gun (light pen) for interactive mode can be connected to a display tap board
and configured for one of two light gun inputs.

Four more switches with lamps (LEDs) can be set by either the user or WWI 
programme.

Displays could in particular be oszilloscopes with a trace blanking
or unblanking input (Z-input).
The amplitude of the X and Y signals is &plusmn;3V which can be attenuated
with a potentiometer on the board.
Z output is 5V (TTL) digital output with 50µs active pulses.
Polarity can be configured on the tap board.

Displays that work without modifications are:
- Grundig GO-40Z oszilloscope (with Z-option)
- Tektronix 1740A oszilloscope 
- Tektronix 611 storage display unit

The Tektronix 611 can be swiched to non-storage mode and is normally 
internally wired for +/- 1V sensitivity; 
thus the potentimeters on the tap board are required.

Several other oscilloscopes have a Z option, but often require
at least 20V to blank the trace.
For this cases, the tap board has provisions for a voltage converter
and corresponding output amplifier.
Sometimes (e.g. Hameg) are designed for blanking small parts of the trace
only, as internally a diode clamps the coupling capacitor output.

A Hameg HM512 was succesfully modified by reversing the diode and also
adding internally a small amplifier to obtain larger voltage swing
from the Z-input. 

## I²C Bus

The interface board has a connected to access the Rapi's (second) I²C bus,
shifted to 5V operation.

With upto eight PCF8574, each can drive 8 swiches and lamps.

Note that the WWI had no console, but was to a large extend controlled
by panel switches and lights.
  

## 5V only operation

The board can be driven by a 5V Arduino.
In this case, JP3 must be cut and changed.
The voltage stablizer U9 (LP 2950-3.3) must be used.
The 3.3V pins are then supplied with 5V.
 

