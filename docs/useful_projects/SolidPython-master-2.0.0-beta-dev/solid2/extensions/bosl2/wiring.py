from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/wiring.scad'}", False)

class _hex_offset_ring(_Bosl2Base):
    def __init__(self, d=None, lev=None, **kwargs):
       super().__init__("_hex_offset_ring", {"d" : d, "lev" : lev, **kwargs})

class _hex_offsets(_Bosl2Base):
    def __init__(self, n=None, d=None, lev=None, arr=None, **kwargs):
       super().__init__("_hex_offsets", {"n" : n, "d" : d, "lev" : lev, "arr" : arr, **kwargs})

class wire_bundle(_Bosl2Base):
    def __init__(self, path=None, wires=None, wirediam=None, rounding=None, wirenum=None, corner_steps=None, **kwargs):
       super().__init__("wire_bundle", {"path" : path, "wires" : wires, "wirediam" : wirediam, "rounding" : rounding, "wirenum" : wirenum, "corner_steps" : corner_steps, **kwargs})

