from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/tripod_mounts.scad'}", False)

class manfrotto_rc2_plate(_Bosl2Base):
    def __init__(self, chamfer=None, anchor=None, orient=None, spin=None, **kwargs):
       super().__init__("manfrotto_rc2_plate", {"chamfer" : chamfer, "anchor" : anchor, "orient" : orient, "spin" : spin, **kwargs})

