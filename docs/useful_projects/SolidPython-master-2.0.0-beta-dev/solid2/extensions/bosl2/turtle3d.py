from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/turtle3d.scad'}", False)

class _transpart(_Bosl2Base):
    def __init__(self, T=None, **kwargs):
       super().__init__("_transpart", {"T" : T, **kwargs})

class _rotpart(_Bosl2Base):
    def __init__(self, T=None, **kwargs):
       super().__init__("_rotpart", {"T" : T, **kwargs})

class _turtle3d_state_valid(_Bosl2Base):
    def __init__(self, state=None, **kwargs):
       super().__init__("_turtle3d_state_valid", {"state" : state, **kwargs})

class turtle3d(_Bosl2Base):
    def __init__(self, commands=None, state=None, transforms=None, full_state=None, repeat=None, **kwargs):
       super().__init__("turtle3d", {"commands" : commands, "state" : state, "transforms" : transforms, "full_state" : full_state, "repeat" : repeat, **kwargs})

class _turtle3d_repeat(_Bosl2Base):
    def __init__(self, commands=None, state=None, repeat=None, **kwargs):
       super().__init__("_turtle3d_repeat", {"commands" : commands, "state" : state, "repeat" : repeat, **kwargs})

class _turtle3d_command_len(_Bosl2Base):
    def __init__(self, commands=None, index=None, **kwargs):
       super().__init__("_turtle3d_command_len", {"commands" : commands, "index" : index, **kwargs})

class _turtle3d(_Bosl2Base):
    def __init__(self, commands=None, state=None, index=None, **kwargs):
       super().__init__("_turtle3d", {"commands" : commands, "state" : state, "index" : index, **kwargs})

class _turtle3d_rotation(_Bosl2Base):
    def __init__(self, command=None, angle=None, center=None, **kwargs):
       super().__init__("_turtle3d_rotation", {"command" : command, "angle" : angle, "center" : center, **kwargs})

class _tupdate(_Bosl2Base):
    def __init__(self, state=None, tran=None, pretran=None, **kwargs):
       super().__init__("_tupdate", {"state" : state, "tran" : tran, "pretran" : pretran, **kwargs})

class _turtle3d_command(_Bosl2Base):
    def __init__(self, command=None, parm=None, parm2=None, state=None, index=None, **kwargs):
       super().__init__("_turtle3d_command", {"command" : command, "parm" : parm, "parm2" : parm2, "state" : state, "index" : index, **kwargs})

class _turtle3d_list_command(_Bosl2Base):
    def __init__(self, command=None, arcsteps=None, movescale=None, lastT=None, lastPre=None, index=None, **kwargs):
       super().__init__("_turtle3d_list_command", {"command" : command, "arcsteps" : arcsteps, "movescale" : movescale, "lastT" : lastT, "lastPre" : lastPre, "index" : index, **kwargs})

class turtle3d(_Bosl2Base):
    def __init__(self, commands=None, state=None, transforms=None, full_state=None, repeat=None, **kwargs):
       super().__init__("turtle3d", {"commands" : commands, "state" : state, "transforms" : transforms, "full_state" : full_state, "repeat" : repeat, **kwargs})

