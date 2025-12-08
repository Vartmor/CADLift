from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/nema_steppers.scad'}", False)

class nema_motor_info(_Bosl2Base):
    def __init__(self, size=None, **kwargs):
       super().__init__("nema_motor_info", {"size" : size, **kwargs})

class nema_stepper_motor(_Bosl2Base):
    def __init__(self, size=None, h=None, shaft_len=None, details=None, atype=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("nema_stepper_motor", {"size" : size, "h" : h, "shaft_len" : shaft_len, "details" : details, "atype" : atype, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

class nema_mount_mask(_Bosl2Base):
    def __init__(self, size=None, depth=None, l=None, atype=None, anchor=None, spin=None, orient=None, **kwargs):
       super().__init__("nema_mount_mask", {"size" : size, "depth" : depth, "l" : l, "atype" : atype, "anchor" : anchor, "spin" : spin, "orient" : orient, **kwargs})

