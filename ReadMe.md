# Whirlwind I Vector Graphics Interface

For showing a Whirlwind programme's output, a small hardware
generates vector strokes on two X/Y/Z oszilloskopes
and allows to attach two light guns

## Directories

<dl>
<dt> CAD   <dd> 3D Light gun case 3D files 
<dt> DOC   <dd> Documentation (own and collected)  
<dt> KiCad <dd> Schematics and PCB drawings
<dt> src   <dd> Python and Arduino source
</dl>

## Versions


## Basics

The interface allows to draw (short) vectors for two channels
on an analog x/y/z display, e.g. an oszilloscope.

The D/A converter used has an internal reference of 2.048V and 12 bits
resultion and produces 0..2.047V in steps of 1/4096. 
WWI uses 10 bits plus sign, i.e. +/- 1023.
Thus the coordinate unit corresponds to 1mV internally.
The output state amplifies by 2.5, thus supplies +/- 2.5V and 2.5mV per unit. 

Drawing a vector is done by setting two integrators to the start point,
then provide a speed, start the integrators for 50µs
and provide a strobe for the z axis during that time.
With maximum speed (-1023 or +1023, i.e. 0 or 2.047V), the movement is 1/8 of the full coordinate range -1.0 .. +1.0,
i.e. 256 coordinate units or 250mV. 
Thus coordinate differences must be multiplied by 4 to set the speed. 
Longer vectors must be drawn as (at most) 8 segments.

The display should be setup such that increasing both coordinates  
move the point right and up;
increasing one and decreasing the other gives a reverse stroke.  

The polarity of the z-axis strobe can be selected by a jumper for each channel.

The charcter display function uses a chain of segements to speed up
writing; this requires a very precise setup of the mid voltage
to 1.023V; otherwise the characters are blurred.




  


 

