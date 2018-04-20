import builtins

from .base import Module, ModuleLoader


class BuiltinPython(Module):
    """Execute Python code in the current interpreter.
    """
    def __call__(self, inputs, output_names, **kwargs):
        code, = inputs.pop('code')
        local = {}
        for env in inputs.get('env', []):
            local.update(env)
        for k, v in inputs.items():
            local[k] = v[-1]
        local['__builtins__'] = builtins
        exec(compile(code, 'code', 'exec'), local, local)
        out = {}
        for name in output_names:
            if name != 'env':
                out[name] = local[name]
        out['env'] = local
        return out


class BuiltinPythonLoader(ModuleLoader):
    def get_module(self, module):
        if module.get('type') != 'script.python':
            return None
        return BuiltinPython()
