from ..scad_import import use as _use
from ...config import config as _config
from pathlib import Path as _Path

# This loads all the built in OpenSCAD functions
# (like circle, square, color, translate.....)
if not _config.use_implicit_builtins:
    from .openscad_primitives import *
else:
    _use(_Path(__file__).parent / "implicit.primitives", skip_render=True)
