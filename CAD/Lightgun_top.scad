difference() {
  translate([0,-50, 2])
    rotate([90,3.6,0])
import("/home/rg/SMBdir/HNF/Whirlwind/WWI-vecIF/CAD/WWI-Lightgun-1.stl");
  translate([-19,0,-5])
    rotate([0,0,5])
      cube([30, 50, 12]);
  translate([-25, -47+20, 3.5])
    rotate([0,90,0])
      #cylinder(d=3, h=10, $fn=36);
}