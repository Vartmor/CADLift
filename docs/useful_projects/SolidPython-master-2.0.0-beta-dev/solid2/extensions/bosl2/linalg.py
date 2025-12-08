from solid2.core.object_base import OpenSCADConstant as _OpenSCADConstant
from solid2.core.scad_import import extra_scad_include as _extra_scad_include
from pathlib import Path as _Path

from .bosl2_base import Bosl2Base as _Bosl2Base

_extra_scad_include(f"{_Path(__file__).parent.parent / 'bosl2/BOSL2/linalg.scad'}", False)

class is_matrix(_Bosl2Base):
    def __init__(self, A=None, m=None, n=None, square=None, **kwargs):
       super().__init__("is_matrix", {"A" : A, "m" : m, "n" : n, "square" : square, **kwargs})

class is_matrix_symmetric(_Bosl2Base):
    def __init__(self, A=None, eps=None, **kwargs):
       super().__init__("is_matrix_symmetric", {"A" : A, "eps" : eps, **kwargs})

class is_rotation(_Bosl2Base):
    def __init__(self, A=None, dim=None, centered=None, **kwargs):
       super().__init__("is_rotation", {"A" : A, "dim" : dim, "centered" : centered, **kwargs})

class echo_matrix(_Bosl2Base):
    def __init__(self, M=None, description=None, sig=None, sep=None, eps=None, **kwargs):
       super().__init__("echo_matrix", {"M" : M, "description" : description, "sig" : sig, "sep" : sep, "eps" : eps, **kwargs})

class column(_Bosl2Base):
    def __init__(self, M=None, i=None, **kwargs):
       super().__init__("column", {"M" : M, "i" : i, **kwargs})

class submatrix(_Bosl2Base):
    def __init__(self, M=None, idx1=None, idx2=None, **kwargs):
       super().__init__("submatrix", {"M" : M, "idx1" : idx1, "idx2" : idx2, **kwargs})

class ident(_Bosl2Base):
    def __init__(self, n=None, **kwargs):
       super().__init__("ident", {"n" : n, **kwargs})

class diagonal_matrix(_Bosl2Base):
    def __init__(self, diag=None, offdiag=None, **kwargs):
       super().__init__("diagonal_matrix", {"diag" : diag, "offdiag" : offdiag, **kwargs})

class transpose(_Bosl2Base):
    def __init__(self, M=None, reverse=None, **kwargs):
       super().__init__("transpose", {"M" : M, "reverse" : reverse, **kwargs})

class outer_product(_Bosl2Base):
    def __init__(self, u=None, v=None, **kwargs):
       super().__init__("outer_product", {"u" : u, "v" : v, **kwargs})

class submatrix_set(_Bosl2Base):
    def __init__(self, M=None, A=None, m=None, n=None, **kwargs):
       super().__init__("submatrix_set", {"M" : M, "A" : A, "m" : m, "n" : n, **kwargs})

class hstack(_Bosl2Base):
    def __init__(self, M1=None, M2=None, M3=None, **kwargs):
       super().__init__("hstack", {"M1" : M1, "M2" : M2, "M3" : M3, **kwargs})

class block_matrix(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("block_matrix", {"M" : M, **kwargs})

class linear_solve(_Bosl2Base):
    def __init__(self, A=None, b=None, pivot=None, **kwargs):
       super().__init__("linear_solve", {"A" : A, "b" : b, "pivot" : pivot, **kwargs})

class linear_solve3(_Bosl2Base):
    def __init__(self, A=None, b=None, **kwargs):
       super().__init__("linear_solve3", {"A" : A, "b" : b, **kwargs})

class matrix_inverse(_Bosl2Base):
    def __init__(self, A=None, **kwargs):
       super().__init__("matrix_inverse", {"A" : A, **kwargs})

class rot_inverse(_Bosl2Base):
    def __init__(self, T=None, **kwargs):
       super().__init__("rot_inverse", {"T" : T, **kwargs})

class null_space(_Bosl2Base):
    def __init__(self, A=None, eps=None, **kwargs):
       super().__init__("null_space", {"A" : A, "eps" : eps, **kwargs})

class qr_factor(_Bosl2Base):
    def __init__(self, A=None, pivot=None, **kwargs):
       super().__init__("qr_factor", {"A" : A, "pivot" : pivot, **kwargs})

class _qr_factor(_Bosl2Base):
    def __init__(self, A=None, Q=None, P=None, pivot=None, col=None, m=None, n=None, **kwargs):
       super().__init__("_qr_factor", {"A" : A, "Q" : Q, "P" : P, "pivot" : pivot, "col" : col, "m" : m, "n" : n, **kwargs})

class _swap_matrix(_Bosl2Base):
    def __init__(self, n=None, i=None, j=None, **kwargs):
       super().__init__("_swap_matrix", {"n" : n, "i" : i, "j" : j, **kwargs})

class back_substitute(_Bosl2Base):
    def __init__(self, R=None, b=None, transpose=None, **kwargs):
       super().__init__("back_substitute", {"R" : R, "b" : b, "transpose" : transpose, **kwargs})

class _back_substitute(_Bosl2Base):
    def __init__(self, R=None, b=None, x=None, **kwargs):
       super().__init__("_back_substitute", {"R" : R, "b" : b, "x" : x, **kwargs})

class cholesky(_Bosl2Base):
    def __init__(self, A=None, **kwargs):
       super().__init__("cholesky", {"A" : A, **kwargs})

class _cholesky(_Bosl2Base):
    def __init__(self, A=None, L=None, n=None, **kwargs):
       super().__init__("_cholesky", {"A" : A, "L" : L, "n" : n, **kwargs})

class det2(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("det2", {"M" : M, **kwargs})

class det3(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("det3", {"M" : M, **kwargs})

class det4(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("det4", {"M" : M, **kwargs})

class determinant(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("determinant", {"M" : M, **kwargs})

class norm_fro(_Bosl2Base):
    def __init__(self, A=None, **kwargs):
       super().__init__("norm_fro", {"A" : A, **kwargs})

class matrix_trace(_Bosl2Base):
    def __init__(self, M=None, **kwargs):
       super().__init__("matrix_trace", {"M" : M, **kwargs})

class echo_matrix(_Bosl2Base):
    def __init__(self, M=None, description=None, sig=None, sep=None, eps=None, **kwargs):
       super().__init__("echo_matrix", {"M" : M, "description" : description, "sig" : sig, "sep" : sep, "eps" : eps, **kwargs})

