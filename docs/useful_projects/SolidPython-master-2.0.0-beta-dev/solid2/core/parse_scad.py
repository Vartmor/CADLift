import hashlib
import pickle
from functools import partial
from pathlib import Path
from collections import namedtuple

from ..config import config
from .object_base import OpenSCADConstant
from .utils import escape_openscad_identifier
from .object_factory import create_openscad_wrapper_from_symbols

callables_entry = namedtuple("callables_entry", ["name", "args", "kwargs"])


def get_pickle_filename(filename):
    md5 = hashlib.md5()
    md5.update(filename.as_posix().encode('utf-8'))
    filename_hash = md5.hexdigest()

    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
        file_content_hash = d.hexdigest()

    pickle_filename = Path(filename_hash).with_suffix("." + file_content_hash).name
    assert(config.pickle_cache_dir is not None)
    return config.pickle_cache_dir / pickle_filename, filename_hash

def check_pickle_cache(filename):
    if not config.enable_pickle_cache:
        return None, None, False
    assert(config.pickle_cache_dir is not None)

    pickle_filename, _ = get_pickle_filename(filename)

    #create pickle_cache_dir if neccessary
    if not config.pickle_cache_dir.exists():
        config.pickle_cache_dir.mkdir(parents=True)

    #if the file exists, load and return it
    if pickle_filename.exists():
        with pickle_filename.open("rb") as f:
            pickler = pickle.Unpickler(f)
            callables = pickler.load()
            global_vars = pickler.load()
            return callables, global_vars, True

    return None, None, False

def update_pickle_cache(filename, callables, global_vars):
    if not config.enable_pickle_cache:
        return

    pickle_filename, filename_hash = get_pickle_filename(filename)

    #delete old files which correspond to this (absolute) filename(_hash)
    for f in pickle_filename.parent.glob(filename_hash + "*"):
        Path.unlink(f)

    #write the callables and global_vars to disk
    with pickle_filename.open("wb") as f:
        pickler = pickle.Pickler(f)
        pickler.dump(callables)
        pickler.dump(global_vars)

def get_scad_file_as_dict(filename):
    assert(filename.is_absolute())

    #check whether we have a valid up to date pickled version of it
    callables, global_vars, cache_is_valid = check_pickle_cache(filename)
    if not cache_is_valid:
        #otherwise parse the file
        from ..libs.py_scadparser import scad_parser
        modules, functions, global_vars = scad_parser.parseFile(filename)

        callables = []
        for c in modules + functions:
            #args = [p.name for p in c.parameters if not p.optional]
            #kwargs = [p.name for p in c.parameters if p.optional]
            kwargs = [p.name for p in c.parameters]

            callables.append(callables_entry(c.name, [], kwargs))

        #write the read version to disk so we can probably use it the next time
        update_pickle_cache(filename, callables, global_vars)

    #create a wrapper for each callable and add it to the dict
    new_namespace_dict = {}
    if callables:
        for c in callables:
            wrapper = create_openscad_wrapper_from_symbols(c.name, [], c.kwargs)
            new_namespace_dict[escape_openscad_identifier(c.name)] = wrapper

    if global_vars:
        for c in global_vars:
            new_namespace_dict[escape_openscad_identifier(c.name)] = \
                                                        OpenSCADConstant(c.name)

    return new_namespace_dict

