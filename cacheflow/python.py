import builtins

from .base import Module, ModuleLoader


class BuiltinPython(Module):
    """Execute Python code in the current interpreter.
    """
    def __call__(self, inputs, output_names, **kwargs):
        code, = inputs.pop('code')
        local = {k: v[-1] for k, v in inputs.items()}
        local['__builtins__'] = builtins
        exec(compile(code, 'code', 'exec'), local, local)
        out = {}
        for name in output_names:
            out[name] = local[name]
        return out


class BuiltinPythonLoader(ModuleLoader):
    def get_module(self, module):
        if module.get('type') != 'script.python':
            return None
        return BuiltinPython()
