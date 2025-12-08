#! /usr/bin/env python

import sys
sys.argv.append("--implicit")

from solid2 import square, circle, cylinder, \
                   union, difference, \
                   translate, linear_extrude, rotate_extrude,\
                   scad_inline_parameter_func, shell # type: ignore

#these are the Implicit examples from https://www.implicitcad.org/examples

def ex1():
    return linear_extrude (height = 30, twist = 180, r=2) ( # type: ignore
               union (r=2) ( # type: ignore
                   square(x=[-2,2], y=[-10,10], r=2),
                   square(x=[-10,10], y=[-2,2], r=2),
               )
           )

def ex2():
    #function parameter are a little tricky, but they do work like this:
    twist_func = scad_inline_parameter_func("twist(h) = 90*cos(h*2*pi/40)")

    return linear_extrude (height = 40, twist = twist_func) ( # type: ignore
               difference () (
                   shell(2) (circle (10)),
                   square(x=[0,20], y=[-4,4]),
               )
           ).rotate(0, 0, 90).left(50)

def ex3():
    return union() (
               cylinder(r=19, h=10, _fn=6, center=True),
               cylinder(r=10, h=40),
               rotate_extrude(4*360, translate=[0,38]) ( # type: ignore
                   translate ([10,0])( square([8,4], center=True))
               ),
           ).right(50)

def ex4():
    height_func = scad_inline_parameter_func("height(x, y) = 10 + 5*cos(x) + 5*cos(y)")

    return linear_extrude(height = height_func) (circle(10)).left(100) # type: ignore

def ex5():
    twist_func = scad_inline_parameter_func("twist(h) = 35*cos(h*2*pi/60)")

    return linear_extrude (height = 40, twist = twist_func) ( # type: ignore
               union ( r = 8) ( # type: ignore
                   circle (10),
                   translate ([22,0]) (circle (10)),
                   translate ([0,22]) (circle (10)),
                   translate ([-22,0]) (circle (10)),
                   translate ([0,-22]) (circle (10)),
               )
           ).right(130)

(ex1() + ex2() + ex3() + ex4() + ex5()).save_as_scad()

