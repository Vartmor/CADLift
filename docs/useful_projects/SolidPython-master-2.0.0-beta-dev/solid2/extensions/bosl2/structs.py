from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/structs.scad'}", False)

class struct_set(_Bosl2Base):
    def __init__(self, struct=None, key=None, value=None, grow=None, **kwargs):
       super().__init__("struct_set", {"struct" : struct, "key" : key, "value" : value, "grow" : grow, **kwargs})

class _format_key(_Bosl2Base):
    def __init__(self, key=None, **kwargs):
       super().__init__("_format_key", {"key" : key, **kwargs})

class struct_remove(_Bosl2Base):
    def __init__(self, struct=None, key=None, **kwargs):
       super().__init__("struct_remove", {"struct" : struct, "key" : key, **kwargs})

class struct_val(_Bosl2Base):
    def __init__(self, struct=None, key=None, default=None, **kwargs):
       super().__init__("struct_val", {"struct" : struct, "key" : key, "default" : default, **kwargs})

class struct_keys(_Bosl2Base):
    def __init__(self, struct=None, **kwargs):
       super().__init__("struct_keys", {"struct" : struct, **kwargs})

class echo_struct(_Bosl2Base):
    def __init__(self, struct=None, name=None, **kwargs):
       super().__init__("echo_struct", {"struct" : struct, "name" : name, **kwargs})

class is_struct(_Bosl2Base):
    def __init__(self, x=None, **kwargs):
       super().__init__("is_struct", {"x" : x, **kwargs})

class echo_struct(_Bosl2Base):
    def __init__(self, struct=None, name=None, **kwargs):
       super().__init__("echo_struct", {"struct" : struct, "name" : name, **kwargs})

