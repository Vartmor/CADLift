#! /usr/bin/env python

from solid2 import cube, text, translate, union, scad_render_to_file, scad_inline, \
                   CustomizerDropdownVariable, CustomizerSliderVariable

#register all the custom variables you want to use
objects = CustomizerDropdownVariable("objects", 4, [2, 4, 6])
side = CustomizerSliderVariable("side", 4)
cube_pos = CustomizerSliderVariable("cube_pos", [5, 5, 5])
cube_size = CustomizerSliderVariable("cube_size", 5)
customizedText = CustomizerDropdownVariable("text", "customize me!",
                                            ["customize me!", "Thank you!"])

#use scad_inline to use them
scene = union()
scene += scad_inline("""
                    for (i = [1:objects]){
                        translate([2*i*side,0,0]){
                            cube(side);
                        }
                    }
                    """)

scene += translate(cube_pos) (
            cube(cube_size * 2))

scene += translate([0, -20, 0]) (
            text(str(customizedText)))

scad_render_to_file(scene)

