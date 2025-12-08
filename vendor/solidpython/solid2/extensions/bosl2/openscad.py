from .bosl2_base import Bosl2Base as _Bosl2Base

class union(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("union", {**kwargs})

class difference(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("difference", {**kwargs})

class intersection(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("intersection", {**kwargs})

class intersection_for(_Bosl2Base):
    def __init__(self, n=None, **kwargs):
       super().__init__("intersection_for", {"n" : n, **kwargs})

class translate(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("translate", {"v" : v, **kwargs})

class scale(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("scale", {"v" : v, **kwargs})

class rotate(_Bosl2Base):
    def __init__(self, a=None, v=None, **kwargs):
       super().__init__("rotate", {"a" : a, "v" : v, **kwargs})

class mirror(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("mirror", {"v" : v, **kwargs})

class resize(_Bosl2Base):
    def __init__(self, newsize=None, auto=None, **kwargs):
       super().__init__("resize", {"newsize" : newsize, "auto" : auto, **kwargs})

class color(_Bosl2Base):
    def __init__(self, c=None, alpha=None, **kwargs):
       super().__init__("color", {"c" : c, "alpha" : alpha, **kwargs})

class minkowski(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("minkowski", {**kwargs})

class offset(_Bosl2Base):
    def __init__(self, r=None, delta=None, chamfer=None, _fn=None, **kwargs):
       super().__init__("offset", {"r" : r, "delta" : delta, "chamfer" : chamfer, "_fn" : _fn, **kwargs})

class hull(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("hull", {**kwargs})

class render(_Bosl2Base):
    def __init__(self, convexity=None, **kwargs):
       super().__init__("render", {"convexity" : convexity, **kwargs})

class linear_extrude(_Bosl2Base):
    def __init__(self, height=None, center=None, convexity=None, twist=None, slices=None, scale=None, **kwargs):
       super().__init__("linear_extrude", {"height" : height, "center" : center, "convexity" : convexity, "twist" : twist, "slices" : slices, "scale" : scale, **kwargs})

class rotate_extrude(_Bosl2Base):
    def __init__(self, angle=None, convexity=None, _fn=None, **kwargs):
       super().__init__("rotate_extrude", {"angle" : angle, "convexity" : convexity, "_fn" : _fn, **kwargs})

class projection(_Bosl2Base):
    def __init__(self, cut=None, **kwargs):
       super().__init__("projection", {"cut" : cut, **kwargs})

class surface(_Bosl2Base):
    def __init__(self, file=None, center=None, convexity=None, invert=None, **kwargs):
       super().__init__("surface", {"file" : file, "center" : center, "convexity" : convexity, "invert" : invert, **kwargs})

class child(_Bosl2Base):
    def __init__(self, index=None, vector=None, range=None, **kwargs):
       super().__init__("child", {"index" : index, "vector" : vector, "range" : range, **kwargs})

class children(_Bosl2Base):
    def __init__(self, index=None, vector=None, range=None, **kwargs):
       super().__init__("children", {"index" : index, "vector" : vector, "range" : range, **kwargs})

class import_stl(_Bosl2Base):
    def __init__(self, file=None, origin=None, convexity=None, layer=None, **kwargs):
       super().__init__("import_stl", {"file" : file, "origin" : origin, "convexity" : convexity, "layer" : layer, **kwargs})

class import_dxf(_Bosl2Base):
    def __init__(self, file=None, origin=None, convexity=None, layer=None, **kwargs):
       super().__init__("import_dxf", {"file" : file, "origin" : origin, "convexity" : convexity, "layer" : layer, **kwargs})

class _import(_Bosl2Base):
    def __init__(self, file=None, origin=None, convexity=None, layer=None, **kwargs):
       super().__init__("_import", {"file" : file, "origin" : origin, "convexity" : convexity, "layer" : layer, **kwargs})

class assign(_Bosl2Base):
    def __init__(self, **kwargs):
       super().__init__("assign", {**kwargs})

class multmatrix(_Bosl2Base):
    def __init__(self, m=None, **kwargs):
       super().__init__("multmatrix", {"m" : m, **kwargs})

class polygon(_Bosl2Base):
    def __init__(self, points=None, paths=None, convexity=None, **kwargs):
       super().__init__("polygon", {"points" : points, "paths" : paths, "convexity" : convexity, **kwargs})

class circle(_Bosl2Base):
    def __init__(self, r=None, d=None, _fn=None, **kwargs):
       super().__init__("circle", {"r" : r, "d" : d, "_fn" : _fn, **kwargs})

class square(_Bosl2Base):
    def __init__(self, size=None, center=None, **kwargs):
       super().__init__("square", {"size" : size, "center" : center, **kwargs})

class sphere(_Bosl2Base):
    def __init__(self, r=None, d=None, _fn=None, **kwargs):
       super().__init__("sphere", {"r" : r, "d" : d, "_fn" : _fn, **kwargs})

class cube(_Bosl2Base):
    def __init__(self, size=None, center=None, **kwargs):
       super().__init__("cube", {"size" : size, "center" : center, **kwargs})

class cylinder(_Bosl2Base):
    def __init__(self, r=None, h=None, r1=None, r2=None, d=None, d1=None, d2=None, center=None, _fn=None, **kwargs):
       super().__init__("cylinder", {"r" : r, "h" : h, "r1" : r1, "r2" : r2, "d" : d, "d1" : d1, "d2" : d2, "center" : center, "_fn" : _fn, **kwargs})

class polyhedron(_Bosl2Base):
    def __init__(self, points=None, faces=None, convexity=None, triangles=None, **kwargs):
       super().__init__("polyhedron", {"points" : points, "faces" : faces, "convexity" : convexity, "triangles" : triangles, **kwargs})

class text(_Bosl2Base):
    def __init__(self, text=None, size=None, font=None, halign=None, valign=None, spacing=None, direction=None, language=None, script=None, _fn=None, **kwargs):
       super().__init__("text", {"text" : text, "size" : size, "font" : font, "halign" : halign, "valign" : valign, "spacing" : spacing, "direction" : direction, "language" : language, "script" : script, "_fn" : _fn, **kwargs})

