from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/lists.scad'}", False)

class is_homogeneous(_Bosl2Base):
    def __init__(self, l=None, depth=None, **kwargs):
       super().__init__("is_homogeneous", {"l" : l, "depth" : depth, **kwargs})

class is_homogenous(_Bosl2Base):
    def __init__(self, l=None, depth=None, **kwargs):
       super().__init__("is_homogenous", {"l" : l, "depth" : depth, **kwargs})

class _same_type(_Bosl2Base):
    def __init__(self, a=None, b=None, depth=None, **kwargs):
       super().__init__("_same_type", {"a" : a, "b" : b, "depth" : depth, **kwargs})

class min_length(_Bosl2Base):
    def __init__(self, list=None, **kwargs):
       super().__init__("min_length", {"list" : list, **kwargs})

class max_length(_Bosl2Base):
    def __init__(self, list=None, **kwargs):
       super().__init__("max_length", {"list" : list, **kwargs})

class _list_shape_recurse(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("_list_shape_recurse", {"v" : v, **kwargs})

class _list_shape_recurse(_Bosl2Base):
    def __init__(self, v=None, **kwargs):
       super().__init__("_list_shape_recurse", {"v" : v, **kwargs})

class list_shape(_Bosl2Base):
    def __init__(self, v=None, depth=None, **kwargs):
       super().__init__("list_shape", {"v" : v, "depth" : depth, **kwargs})

class in_list(_Bosl2Base):
    def __init__(self, val=None, list=None, idx=None, **kwargs):
       super().__init__("in_list", {"val" : val, "list" : list, "idx" : idx, **kwargs})

class select(_Bosl2Base):
    def __init__(self, list=None, start=None, end=None, **kwargs):
       super().__init__("select", {"list" : list, "start" : start, "end" : end, **kwargs})

class slice(_Bosl2Base):
    def __init__(self, list=None, start=None, end=None, **kwargs):
       super().__init__("slice", {"list" : list, "start" : start, "end" : end, **kwargs})

class last(_Bosl2Base):
    def __init__(self, list=None, **kwargs):
       super().__init__("last", {"list" : list, **kwargs})

class list_head(_Bosl2Base):
    def __init__(self, list=None, to=None, **kwargs):
       super().__init__("list_head", {"list" : list, "to" : to, **kwargs})

class list_tail(_Bosl2Base):
    def __init__(self, list=None, _from=None, **kwargs):
       super().__init__("list_tail", {"list" : list, "_from" : _from, **kwargs})

class bselect(_Bosl2Base):
    def __init__(self, list=None, index=None, **kwargs):
       super().__init__("bselect", {"list" : list, "index" : index, **kwargs})

class repeat(_Bosl2Base):
    def __init__(self, val=None, n=None, i=None, **kwargs):
       super().__init__("repeat", {"val" : val, "n" : n, "i" : i, **kwargs})

class list_bset(_Bosl2Base):
    def __init__(self, indexset=None, valuelist=None, dflt=None, **kwargs):
       super().__init__("list_bset", {"indexset" : indexset, "valuelist" : valuelist, "dflt" : dflt, **kwargs})

class list(_Bosl2Base):
    def __init__(self, l=None, **kwargs):
       super().__init__("list", {"l" : l, **kwargs})

class force_list(_Bosl2Base):
    def __init__(self, value=None, n=None, fill=None, **kwargs):
       super().__init__("force_list", {"value" : value, "n" : n, "fill" : fill, **kwargs})

class reverse(_Bosl2Base):
    def __init__(self, list=None, **kwargs):
       super().__init__("reverse", {"list" : list, **kwargs})

class list_rotate(_Bosl2Base):
    def __init__(self, list=None, n=None, **kwargs):
       super().__init__("list_rotate", {"list" : list, "n" : n, **kwargs})

class shuffle(_Bosl2Base):
    def __init__(self, list=None, seed=None, **kwargs):
       super().__init__("shuffle", {"list" : list, "seed" : seed, **kwargs})

class repeat_entries(_Bosl2Base):
    def __init__(self, list=None, N=None, exact=None, **kwargs):
       super().__init__("repeat_entries", {"list" : list, "N" : N, "exact" : exact, **kwargs})

class list_pad(_Bosl2Base):
    def __init__(self, list=None, minlen=None, fill=None, **kwargs):
       super().__init__("list_pad", {"list" : list, "minlen" : minlen, "fill" : fill, **kwargs})

class list_set(_Bosl2Base):
    def __init__(self, list=None, indices=None, values=None, dflt=None, minlen=None, **kwargs):
       super().__init__("list_set", {"list" : list, "indices" : indices, "values" : values, "dflt" : dflt, "minlen" : minlen, **kwargs})

class list_insert(_Bosl2Base):
    def __init__(self, list=None, indices=None, values=None, **kwargs):
       super().__init__("list_insert", {"list" : list, "indices" : indices, "values" : values, **kwargs})

class list_remove(_Bosl2Base):
    def __init__(self, list=None, ind=None, **kwargs):
       super().__init__("list_remove", {"list" : list, "ind" : ind, **kwargs})

class list_remove_values(_Bosl2Base):
    def __init__(self, list=None, values=None, all=None, **kwargs):
       super().__init__("list_remove_values", {"list" : list, "values" : values, "all" : all, **kwargs})

class idx(_Bosl2Base):
    def __init__(self, list=None, s=None, e=None, step=None, **kwargs):
       super().__init__("idx", {"list" : list, "s" : s, "e" : e, "step" : step, **kwargs})

class pair(_Bosl2Base):
    def __init__(self, list=None, wrap=None, **kwargs):
       super().__init__("pair", {"list" : list, "wrap" : wrap, **kwargs})

class triplet(_Bosl2Base):
    def __init__(self, list=None, wrap=None, **kwargs):
       super().__init__("triplet", {"list" : list, "wrap" : wrap, **kwargs})

class combinations(_Bosl2Base):
    def __init__(self, l=None, n=None, _s=None, **kwargs):
       super().__init__("combinations", {"l" : l, "n" : n, "_s" : _s, **kwargs})

class permutations(_Bosl2Base):
    def __init__(self, l=None, n=None, **kwargs):
       super().__init__("permutations", {"l" : l, "n" : n, **kwargs})

class list_to_matrix(_Bosl2Base):
    def __init__(self, v=None, cnt=None, dflt=None, **kwargs):
       super().__init__("list_to_matrix", {"v" : v, "cnt" : cnt, "dflt" : dflt, **kwargs})

class flatten(_Bosl2Base):
    def __init__(self, l=None, **kwargs):
       super().__init__("flatten", {"l" : l, **kwargs})

class full_flatten(_Bosl2Base):
    def __init__(self, l=None, **kwargs):
       super().__init__("full_flatten", {"l" : l, **kwargs})

class set_union(_Bosl2Base):
    def __init__(self, a=None, b=None, get_indices=None, **kwargs):
       super().__init__("set_union", {"a" : a, "b" : b, "get_indices" : get_indices, **kwargs})

class set_difference(_Bosl2Base):
    def __init__(self, a=None, b=None, **kwargs):
       super().__init__("set_difference", {"a" : a, "b" : b, **kwargs})

class set_intersection(_Bosl2Base):
    def __init__(self, a=None, b=None, **kwargs):
       super().__init__("set_intersection", {"a" : a, "b" : b, **kwargs})

