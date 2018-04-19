from .base import Module, ModuleLoader


class Download(Module):
    """Download a file.
    """
    def __call__(self, inputs, output_names, **kwargs):
        url, = inputs['url']
        if url.startswith('file://'):
            return {'file': url[7:]}
        else:
            raise NotImplementedError


class BuiltinModulesLoader(ModuleLoader):
    TABLE = dict(
        download=Download(),
    )

    def get_module(self, module):
        return self.TABLE.get(module.get('type'))
