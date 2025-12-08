#! /usr/bin/env python

# run extopenscad with -r 2 to get proper results:
#       extopenscad -r 2 examples/14-implicitCAD.escad

# this is the same example as 06-functions.py but with nice smooth implicitCAD
# roundings....

# this is how you activate the "implicit mode" of ExpSolid
# I couldn't figure out a nicer way to set a parameter which can be accessed
# during the import routine of exp_solid
#
# alternatively you can call the whole script with the --implicit parameter:
#   python3 examples/14-implicitCAD.py --implicit

import sys
sys.argv.append("--implicit")

from solid2 import cylinder, cube, difference, union

def wheel():
    return cylinder(r=35, h=15, center=True).rotate(0, 90, 0)

def axle():
    a = cylinder(r=10, h=130, center=True).\
            rotate(0, 90, 0)

    w1 = wheel().left(67)
    w2 = wheel().right(67)

    return w1 + w2 + a

def torso():
    bottom = cube(100, 250, 50, center=True, r=10)
    top = cube(80, 100, 60, center=True, r=10)

    window_cube = cube(200, 55 ,50, center=True, r=10).down(10)
    top = difference(r=10) ( # type: ignore
                top,
                (union(r=10) (window_cube, window_cube.rotate(0, 0, 90))) # type: ignore
            )

    return union(r=10)(bottom, top.up(50)) # type: ignore

def car():
    t = torso()

    front_axle = axle().down(20).back(80)

    rear_axle = front_axle.forward(160)

    return union(r=3)(t, front_axle, rear_axle) # type: ignore

car().save_as_scad()

