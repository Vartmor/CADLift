#! /usr/bin/env python

from solid2 import text, register_font, set_global_viewport_translation

register_font("11-font/RichEatin.otf")
set_global_viewport_translation([700, 900, 200])

text(font="Rich Eatin'", text="blablub").save_as_scad()

