
def _base_fn(name, *args):
    from solid2.core.object_base import scad_inline as scad_inline
    from solid2.core.utils import py2openscad as py2openscad

    params = py2openscad(args)[1:-1]
    return scad_inline(f'{name}({params})')

def cos(n):         return _base_fn("cos", n)
def sin(n):         return _base_fn("sin", n)
def tan(n):         return _base_fn("tan", n)
def acos(n):        return _base_fn('acos', n)
def asin(n):        return _base_fn('asin', n)
def atan(n):        return _base_fn('atan', n)
def atan2(n, m):    return _base_fn('atan2', n, m)

def abs(n):         return _base_fn('abs', n)
def ceil(n):        return _base_fn('ceil', n)
def exp(n):         return _base_fn('exp', n)
def floor(n):       return _base_fn('floor', n)
def len(n):         return _base_fn('len', n)
def ln(n):          return _base_fn('ln', n)
def log(n):         return _base_fn('log', n)
def norm(v):        return _base_fn('norm', v)
def pow(n, m):      return _base_fn('pow', n, m)
def round(n):       return _base_fn('round', n)
def sign(n):        return _base_fn('sign', n)
def sqrt(n):        return _base_fn('sqrt', n)

def min(*args):     return _base_fn('min', *args)
def max(*args):     return _base_fn('max', *args)

def concat(*args):  return _base_fn('concat', *args)
def cross(*args):   return _base_fn('cross', *args)
def lookup(*args):  return _base_fn('lookup', *args)
def rands(*args):   return _base_fn('rands', *args)
def not_(*args):    return _base_fn('!', *args)

