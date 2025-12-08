from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/version.scad'}", False)

BOSL_VERSION = _OpenSCADConstant('BOSL_VERSION')
class bosl_version(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("bosl_version", {**kwargs})

class bosl_version_num(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("bosl_version_num", {**kwargs})

class bosl_version_str(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("bosl_version_str", {**kwargs})

class _version_split_str(_Bosl2Base):
    def __init__(self, x=None, _i=None, _out=None, _num=None, **kwargs):
       super().__init__("_version_split_str", {"x" : x, "_i" : _i, "_out" : _out, "_num" : _num, **kwargs})

class version_to_list(_Bosl2Base):
    def __init__(self, version=None, **kwargs):
       super().__init__("version_to_list", {"version" : version, **kwargs})

class version_to_str(_Bosl2Base):
    def __init__(self, version=None, **kwargs):
       super().__init__("version_to_str", {"version" : version, **kwargs})

class version_to_num(_Bosl2Base):
    def __init__(self, version=None, **kwargs):
       super().__init__("version_to_num", {"version" : version, **kwargs})

class version_cmp(_Bosl2Base):
    def __init__(self, a=None, b=None, **kwargs):
       super().__init__("version_cmp", {"a" : a, "b" : b, **kwargs})

class bosl_required(_Bosl2Base):
    def __init__(self, version=None, **kwargs):
       super().__init__("bosl_required", {"version" : version, **kwargs})

