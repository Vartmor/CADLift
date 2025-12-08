#! /usr/bin/env python

from solid2 import sphere, cube, translate, background, \
                   scad_inline, scad_render_to_file, \
                   set_global_viewport_translation, \
                   set_global_viewport_rotation, \
                   set_global_viewport_distance, \
                   set_global_variable


#set steps in OpenSCAD to 1000

ball_radius = 100

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3(self.x + other.x,
                       self.y + other.y,
                       self.z + other.z)

    def __mul__(self, factor):
        return Vector3(self.x * factor,
                       self.y * factor,
                       self.z * factor)

    def tolist(self):
        return [self.x, self.y, self.z]

#this is our little physics engine
def get_bouncing_ball_data(pos=Vector3(), vel=Vector3(5.0, 5.0, 200.0)):
    data = []
    gravity = Vector3(0.0, 0.0, -8.0)
    for _ in range(1000):
        vel = (vel + gravity) * 0.995
        pos += vel
        if pos.z < ball_radius:
            vel.z = vel.z * -1
            pos.z = ball_radius

        data.append(pos.tolist())

    return data

set_global_viewport_translation([700, 900, 200])
set_global_viewport_rotation([80, 0, 20])
set_global_viewport_distance(6000)

#store pre computed data in global OpenSCAD variable
set_global_variable("bouncing_ball_data", get_bouncing_ball_data())

#get "dynamic ball position over time" from the data set
ball_pos_over_time = scad_inline("bouncing_ball_data[$t * 1000]")

#do some regular solid stuff with it
ball = translate(ball_pos_over_time)(sphere(ball_radius))
floor = background(cube([2000, 2000, 0.01]))

#render it with the pre computed data stored in the header
scad_render_to_file(ball + floor)

# I think if you really want to do something like this you could put the data
# into a seprate .scad file and include it into the main .scad file. You should
# also be able inject OpenSCAD functions (or modules) and use them...
#
# No clue what this could be good for, but....... I guess it might be possible
# to plug a -- more complex :-p -- physics engine into it and render animated
# movies....
#
# ....and print them with a 4d printer....?!?

