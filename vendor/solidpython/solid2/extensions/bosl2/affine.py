from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/affine.scad'}", False)

class affine2d_identity(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("affine2d_identity", {**kwargs})

class affine2d_translate(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine2d_translate", {"v" : v, **kwargs})

class affine2d_scale(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine2d_scale", {"v" : v, **kwargs})

class affine2d_zrot(_Bosl2Base):
    def __init__(self, ang=None, **kwargs):
       super().__init__("affine2d_zrot", {"ang" : ang, **kwargs})

class affine2d_mirror(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine2d_mirror", {"v" : v, **kwargs})

class affine2d_skew(_Bosl2Base):
    def __init__(self, xa=None, ya=None, **kwargs):
       super().__init__("affine2d_skew", {"xa" : xa, "ya" : ya, **kwargs})

class affine3d_identity(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("affine3d_identity", {**kwargs})

class affine3d_translate(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine3d_translate", {"v" : v, **kwargs})

class affine3d_scale(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine3d_scale", {"v" : v, **kwargs})

class affine3d_xrot(_Bosl2Base):
    def __init__(self, ang=None, **kwargs):
       super().__init__("affine3d_xrot", {"ang" : ang, **kwargs})

class affine3d_yrot(_Bosl2Base):
    def __init__(self, ang=None, **kwargs):
       super().__init__("affine3d_yrot", {"ang" : ang, **kwargs})

class affine3d_zrot(_Bosl2Base):
    def __init__(self, ang=None, **kwargs):
       super().__init__("affine3d_zrot", {"ang" : ang, **kwargs})

class affine3d_rot_by_axis(_Bosl2Base):
    def __init__(self, u=None, ang=None, **kwargs):
       super().__init__("affine3d_rot_by_axis", {"u" : u, "ang" : ang, **kwargs})

class affine3d_rot_from_to(_Bosl2Base):
    def __init__(self, _from=None, to=None, **kwargs):
       super().__init__("affine3d_rot_from_to", {"_from" : _from, "to" : to, **kwargs})

class affine3d_mirror(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("affine3d_mirror", {"v" : v, **kwargs})

class affine3d_skew(_Bosl2Base):
    def __init__(self, sxy=None, sxz=None, syx=None, syz=None, szx=None, szy=None, **kwargs):
       super().__init__("affine3d_skew", {"sxy" : sxy, "sxz" : sxz, "syx" : syx, "syz" : syz, "szx" : szx, "szy" : szy, **kwargs})

class affine3d_skew_xy(_Bosl2Base):
    def __init__(self, xa=None, ya=None, **kwargs):
       super().__init__("affine3d_skew_xy", {"xa" : xa, "ya" : ya, **kwargs})

class affine3d_skew_xz(_Bosl2Base):
    def __init__(self, xa=None, za=None, **kwargs):
       super().__init__("affine3d_skew_xz", {"xa" : xa, "za" : za, **kwargs})

class affine3d_skew_yz(_Bosl2Base):
    def __init__(self, ya=None, za=None, **kwargs):
       super().__init__("affine3d_skew_yz", {"ya" : ya, "za" : za, **kwargs})

