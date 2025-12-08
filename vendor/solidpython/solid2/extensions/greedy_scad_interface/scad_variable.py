from solid2.core.object_base import OpenSCADConstant
from ...core.utils import py2openscad

class ScadValue(OpenSCADConstant) : pass

class ScadVariable(ScadValue):
    registered_variables = {}

    def __init__(self, name, default_value, options_str='', label='', tab=''):
        super().__init__(name)

        builtinVars = ["$fn", "$fa", "$fs", "$vpt", "$vpr", "$vpf", "$vpd"]
        if name not in builtinVars and name in self.registered_variables.keys():
            raise ValueError("Multiple instances of ScadVariable with the same name.")

        def_str = self.get_definition(name, default_value, options_str, label, tab)
        self.registered_variables.update({name : def_str})

    def get_definition(self, name, default_value, options_str, label, tab):
        tab = tab and f'/* [{tab}] */\n'
        label = label and f'//{label}\n'
        options_str = options_str and f' //{options_str}'
        default_value = py2openscad(default_value)

        return f'{tab}{label}{name} = {default_value};{options_str}'

