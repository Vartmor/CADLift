#! /usr/bin/env python

from solid2 import cylinder, cube

# as soon as the objects get more sophisticated it makes sense to use functions
# to hierarchically assemble them.
# You can use python functions pretty much the same way as OpenSCAD modules
# except the children stuff. This is not possible with SolidPython but you
# can pass other OpenSCAD objects as parameters to a function.
#
# This simple example assembles a car similar to the one from the OpenSCAD
# tutorial:

def wheel():
    return cylinder(r=35, h=15, center=True).rotate(0, 90, 0)

def axle():
    a = cylinder(r=10, h=120, center=True).rotate(0, 90, 0)

    w1 = wheel().left(70)
    w2 = wheel().right(70)

    return w1 + w2 + a

def torso():
    bottom = cube(100, 250, 50, center=True)
    top = cube(80, 100, 60, center=True)

    window_cube = cube(200, 55 ,50, center=True).down(10)
    top -= (window_cube + window_cube.rotate(0, 0, 90))

    return bottom + top.up(50)

def car():
    t = torso()

    front_axle = axle().down(20).back(80)

    rear_axle = axle().down(20).forward(80)

    return t + front_axle + rear_axle

car().save_as_scad()

