difference() {
  translate([0,50, 8.2])
    rotate([-90,3.6,0])
import("/home/rg/SMBdir/HNF/Whirlwind/WWI-vecIF/CAD/WWI-Lightgun-3.stl");
  translate([-23,-50,3])
    rotate([0,0,-5])
      #cube([30, 50, 7]);
  translate([-25, 47-20,9.5])
    rotate([0,90,0])
      #cylinder(d=3, h=10, $fn=36);
}