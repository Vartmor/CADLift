#! /usr/bin/env python

# this is a basic "a mazing box" (mazebox), just tried to reimplement it with
# bosl2. It's based on https://www.thingiverse.com/thing:1481

from math import pi, cos
from solid2.extensions.bosl2 import zcyl, zrot, tube, surface, projection, \
                                    cylindrical_extrude

def mazebox():
    #the maze is 64x90 pixel
    maze_surface = surface(file="maze7.png", center=True, invert=True)
    maze_projection = projection(cut=True) (maze_surface.up(10))

    #make the radius of the cylinder 3 times the maze width
    r = (64 * 3) / (2*pi)
    maze_mask = []
    segs = 10 #number of segments to get a "rounded" maze path

    for i in range(segs):
        maze_offset = maze_projection.offset(-1+cos(i/segs * pi /2))
        maze_mask += cylindrical_extrude(_or=r-(2*i/segs), ir=r-(2*(i+1)/segs)) (maze_offset)

    full_maze_mask = maze_mask + zrot(360/3)(maze_mask) + zrot(2*360/3)(maze_mask)

    maze_tube = tube(_or=r-0.2, ir=r-2.2, h=88, center=True)
    maze_tube_head = zcyl(r=r+5, h=10).down(40)

    return maze_tube + maze_tube_head - full_maze_mask

mazebox().save_as_scad()

