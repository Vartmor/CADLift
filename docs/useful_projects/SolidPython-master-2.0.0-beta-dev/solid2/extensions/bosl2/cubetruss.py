from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/cubetruss.scad'}", False)

_cubetruss_size = _OpenSCADConstant('_cubetruss_size')
_cubetruss_strut_size = _OpenSCADConstant('_cubetruss_strut_size')
_cubetruss_bracing = _OpenSCADConstant('_cubetruss_bracing')
_cubetruss_clip_thickness = _OpenSCADConstant('_cubetruss_clip_thickness')
class cubetruss_dist(_Bosl2Base):
    def __init__(self, cubes=None, gaps=None, size=None, strut=None, **kwargs):
       super().__init__("cubetruss_dist", {"cubes" : cubes, "gaps" : gaps, "size" : size, "strut" : strut, **kwargs})

class cubetruss(_Bosl2Base):
    def __init__(self, extents=None, clips=None, bracing=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss", {"extents" : extents, "clips" : clips, "bracing" : bracing, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_corner(_Bosl2Base):
    def __init__(self, h=None, extents=None, bracing=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_corner", {"h" : h, "extents" : extents, "bracing" : bracing, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_support(_Bosl2Base):
    def __init__(self, size=None, strut=None, extents=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_support", {"size" : size, "strut" : strut, "extents" : extents, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_foot(_Bosl2Base):
    def __init__(self, w=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_foot", {"w" : w, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_joiner(_Bosl2Base):
    def __init__(self, w=None, vert=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_joiner", {"w" : w, "vert" : vert, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_uclip(_Bosl2Base):
    def __init__(self, dual=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_uclip", {"dual" : dual, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_segment(_Bosl2Base):
    def __init__(self, size=None, strut=None, bracing=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_segment", {"size" : size, "strut" : strut, "bracing" : bracing, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class cubetruss_clip(_Bosl2Base):
    def __init__(self, extents=None, size=None, strut=None, clipthick=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("cubetruss_clip", {"extents" : extents, "size" : size, "strut" : strut, "clipthick" : clipthick, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

