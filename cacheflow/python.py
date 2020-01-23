import builtins
import sys

from .base import Component, SimpleComponentLoader


register = SimpleComponentLoader()


class OutputStreams(object):
    class _Writer(object):
        def __init__(self, output, stream):
            self.output = output
            self.stream = stream

        def write(self, data):
            self.output.append(self.stream, data)

        def flush(self):
            pass

    def __init__(self):
        self.outputs = []

    def append(self, stream, data):
        if self.outputs and self.outputs[-1][0] == stream:
            self.outputs[-1][1].append(data)
        else:
            self.outputs.append((stream, [data]))

    def get(self):
        return [
            (stream, ''.join(data))
            for stream, data in self.outputs
        ]

    def writer(self, stream):
        return self._Writer(self, stream)


# TODO: Figure out caching
# TODO: Figure out isolation
# TODO: Figure out calling different Python versions


@register('script.python')
class BuiltinPython(Component):
    """Execute Python code in the current interpreter.
    """
    def execute(self, inputs, **kwargs):
        code, = inputs.pop('code')
        local = {}
        for env in inputs.get('env', []):
            local.update(env)
        for k, v in inputs.items():
            local[k] = v[-1]
        local['__builtins__'] = builtins
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            streams = OutputStreams()
            sys.stdout = streams.writer('stdout')
            sys.stderr = streams.writer('stderr')

            exec(compile(code, 'code', 'exec'), local, local)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        for name, value in local.items():
            self.set_output(name, value)
        local.pop('__builtins__', None)
        self.set_output('env', local)
        self.set_output('streams', streams.get())
