from solid2.core.object_base.object_base_impl import BareOpenSCADObject
from solid2.core.object_base.operator_mixin import OperatorMixin
from solid2.extensions.bosl2.bosl2_access_syntax_mixin import Bosl2AccessSyntaxMixin


class Bosl2OperatorMixin(OperatorMixin):
    def __add__(self, x):
        from .std import union
        return self._union_op(x, union)

    def __or__(self, x):
        from .std import union
        return self._union_op(x, union)

    def __radd__(self, x):
        from .std import union
        return self._union_op(x, union)

    def __sub__(self, x):
        from .std import difference
        return self._difference_op(x, difference)

    def __mul__(self, x):
        from .std import intersection
        return self._intersection_op(x, intersection)

    def __and__(self, x):
        from .std import intersection
        return self._intersection_op(x, intersection)


class Bosl2Base(Bosl2AccessSyntaxMixin, Bosl2OperatorMixin, BareOpenSCADObject):
    pass

