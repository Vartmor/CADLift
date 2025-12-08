from .object_base import OpenSCADObject
from .utils import escape_openscad_identifier

# =========================
# = creating the wrappers =
# =========================
def check_signature(name, args_def, kwargs_def, *args, **kwargs):
    #check whether the args and kwargs fit a function signature definition
    #defined with args_def and kwargs_def. args_def and kwargs_def are lists
    #of all parameter names the function {name} accepts

    filtered_kwargs = {k: kwargs[k] for k in kwargs if not k.startswith("_")}
    if len(args) + len(filtered_kwargs) > len(args_def) + len(kwargs_def):
        raise TypeError(f"too many arguments to {name}(...)")

    full_args_tuples = list(zip(args_def + kwargs_def, args))
    full_args_tuples += list(zip(filtered_kwargs.keys(), filtered_kwargs.values()))

    full_args_names = [x[0] for x in full_args_tuples]

    args_def_copy = args_def[:]
    kwargs_def_copy = kwargs_def[:]

    while full_args_names and (args_def_copy or kwargs_def_copy):
        a = full_args_names.pop()

        if a in args_def_copy:
            args_def_copy.remove(a)

        elif a in kwargs_def_copy:
            kwargs_def_copy.remove(a)

        else:
            raise TypeError(f"{name}(...) has no parameter {a} or it is " +\
                            f"already occupied by a positional argument")

    #are there still unmatched parameters left?
    if full_args_names:
        if not args_def_copy and not kwargs_def_copy:
            raise TypeError(f"{name}(...) too many arguments")
        else:
            assert(False)

    #are there still unmet args in args_def?
    if args_def_copy and not full_args_names:
        raise TypeError(f"not enough parameters to {name}(...)")

def create_openscad_wrapper_from_symbols(name, args, kwargs):

    #this is the function we'll bind to the init function of the new class
    #that we'll create to represent the openscad function
    def init_func(self, *args, **kwargs):
        def legacy_patch(kwargs):
            # this function patches the kwargs to be backward compatible
            import keyword
            if "segments" in kwargs.keys():
                kwargs["_fn"] = kwargs.pop("segments")
            keys_to_replace = []

            #replace keyword_ with _keyword
            for k in kwargs.keys():
                if k.endswith("_") and keyword.iskeyword(k[:-1]):
                    keys_to_replace.append(k)
            for k in keys_to_replace:
                kwargs["_" + k[:-1]] = kwargs.pop(k)

            #replace __[0-9]... with _[0-9]
            keys_to_replace = []
            for k in kwargs.keys():
                if k.startswith("__") and k[2].isdigit():
                    keys_to_replace.append(k)
            for k in keys_to_replace:
                kwargs["_" + k[2:]] = kwargs.pop(k)

        legacy_patch(kwargs)

        #check whether the *args and **kwargs meet our parameter definitions
        check_signature(name, args_def, kwargs_def, *args, **kwargs)

        #zip the args with the def dicts and update it with kwargs
        #to get a single complete kwargs list
        params = dict(zip(args_def + kwargs_def, args))
        params.update(kwargs)

        #call OpenSCADObject ctor
        return super(self.__class__, self).__init__(name, params)


    #escape all identifiers
    name = escape_openscad_identifier(name)
    args_def = list(map(escape_openscad_identifier, args))
    kwargs_def = list(map(escape_openscad_identifier, kwargs))

    #create the class and bind an "instance of" _init_func it's __init__ function
    class_declaration = type(name, (OpenSCADObject,), {"__init__" : init_func})

    #add the function signature as __doc__ string, so ExpSolidNamespace can
    #display it
    param_str = ",".join([str(x) for x in args])
    param_str += "," if param_str else ''
    param_str += ",".join([str(x) + "=..." for x in kwargs])
    class_declaration.__doc__ = f'{name}({param_str})'

    return class_declaration

