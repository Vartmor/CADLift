#! /usr/bin/env python

from solid2 import cube, sphere, difference, set_global_fn

set_global_fn(72)

difference()(
    cube([10, 20, 30]),
    sphere(10)
).save_as_scad()

# this is very very basic but you can make this as complex as in OpenSCAD.
# You can really just use "python as OpenSCAD". You just need to call
# .save_as_scad() at last to write it to a *.scad file.
#
# If you execute this file it will create examples/01-basics.scad with the this
# content:
#
#        $fn = 72;
#
#        difference() {
#            cube(size = [10, 20, 30]);
#            sphere(r = 10);
#        }
#
