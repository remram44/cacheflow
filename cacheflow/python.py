import ast
import builtins
import logging
import sys

from .base import Component, SimpleComponentLoader


logger = logging.getLogger(__name__)


register = SimpleComponentLoader()


class VarType:
    INPUT = 'input'
    OUTPUT = 'output'
    INPUT_OUTPUT = 'input+output'


class _Frame(object):
    def __init__(self):
        self.globals = set()
        self.nonlocals = set()
        self.locals = set()


# Those nodes are not particularly interesting
_IGNORED_NODES = {
    ast.Constant, ast.FormattedValue, ast.JoinedStr, ast.List,
    ast.Tuple, ast.Set, ast.Dict, ast.Starred, ast.Expr, ast.UnaryOp,
    ast.BinOp, ast.BoolOp, ast.Compare, ast.Call, ast.IfExp,
    ast.Attribute, ast.Subscript, ast.Slice, ast.Assign,
    ast.AnnAssign, ast.AugAssign, ast.Raise, ast.Assert, ast.Delete,
    ast.Pass, ast.If, ast.For, ast.AsyncFor, ast.While, ast.Break,
    ast.Continue, ast.Try, ast.ExceptHandler, ast.With, ast.AsyncWith,
    ast.Return, ast.Yield, ast.YieldFrom, ast.Await,
    # Those are not even nodes
    ast.Load, ast.Store, ast.Del, ast.UAdd, ast.USub, ast.Not,
    ast.Invert, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
    ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor,
    ast.BitAnd, ast.MatMult, ast.And, ast.Or, ast.Eq, ast.NotEq,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In,
    ast.NotIn, ast.keyword, ast.comprehension, ast.alias, ast.withitem,
    ast.arguments, ast.arg,
    # Those are not documented properly
    ast.Module, ast.Interactive, ast.Expression,
}
if sys.version_info >= (3, 8):
    _IGNORED_NODES.update({
        ast.NamedExpr, ast.FunctionType, ast.TypeIgnore,
    })
_IGNORED_NODES = tuple(_IGNORED_NODES)


class _Visitor(ast.NodeVisitor):
    def __init__(self):
        self.vars = {}
        self.frames = []
        self.imports = set()

    def generic_visit(self, node):
        # Those nodes are not particularly interesting
        # They are listed here so that we can properly show a warning if a node
        # we don't know about is encountered
        if isinstance(node, _IGNORED_NODES):
            pass
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                self.maybe_store(node.id)
            elif isinstance(node.ctx, ast.Load):
                if not self.is_local(node.id):
                    self.load(node.id)
            elif isinstance(node.ctx, ast.Del):
                if not self.is_local(node.id):
                    self.del_(node.id)
            else:
                logger.warning("Unknown AST Name context %r", type(node.ctx))
        elif isinstance(node, (
            ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp,
        )):
            previous_frames = len(self.frames)
            for generator in node.generators:
                self.frames.append(_Frame())
                self.visit(generator)
            self.frames.append(_Frame())
            if isinstance(node, ast.DictComp):
                self.visit(node.key)
                self.visit(node.value)
            else:
                self.visit(node.elt)
            del self.frames[previous_frames:]
            return
        elif isinstance(node, ast.Import):
            for item in node.names:
                if item.asname is None:
                    self.maybe_store(item.name)
                else:
                    self.maybe_store(item.asname)
            if not self.frames:
                for item in node.names:
                    self.imports.add(item.name)
            return
        elif isinstance(node, ast.ImportFrom):
            for item in node.names:
                if item.asname is None:
                    self.maybe_store(item.name)
                else:
                    self.maybe_store(item.asname)
            if not self.frames:
                for item in node.names:
                    self.imports.add('%s.%s' % (node.module, item.name))
            return
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.maybe_store(node.name)
            self.frames.append(_Frame())
            super(_Visitor, self).generic_visit(node)
            self.frames.pop(-1)
            return
        elif isinstance(node, ast.Lambda):
            # It's possible for stores to happen in lambdas with `a:=b` syntax
            self.frames.append(_Frame())
            super(_Visitor, self).generic_visit(node)
            self.frames.pop(-1)
            return
        elif isinstance(node, ast.Global):
            for name in node.names:
                self.frames[-1].globals.add(name)
        elif isinstance(node, ast.Nonlocal):
            for name in node.names:
                self.frames[-1].nonlocals.add(name)
        elif isinstance(node, ast.ClassDef):
            self.maybe_store(node.name)
            self.frames.append(_Frame())
            super(_Visitor, self).generic_visit(node)
            self.frames.pop(-1)
            return
        else:
            logger.warning("Unknown AST node %r", type(node))

        super(_Visitor, self).generic_visit(node)

    def is_local(self, name):
        for frame in reversed(self.frames):
            if name in frame.locals:
                return True

        return False

    def maybe_store(self, name):
        if not self.frames:
            self.store(name)
        elif name in self.frames[-1].locals:
            pass
        elif name in self.frames[-1].globals:
            self.store(name)
        elif name in self.frames[-1].nonlocals:
            # Go up
            for frame in reversed(self.frames[:-1]):
                if name in frame.globals:
                    self.store(name)
                elif name in frame.nonlocals:
                    # Keep going up, it exists here but is nonlocal again
                    pass
                elif name in frame.locals:
                    # Game over
                    return
                else:
                    # Keep going up, it doesn't exist here
                    pass

            # This is actually a syntax error if the name doesn't already exist
            self.store(name)
        else:
            self.frames[-1].locals.add(name)

    def store(self, name):
        previous = self.vars.get(name)
        if previous is None:
            self.vars[name] = VarType.OUTPUT
        elif previous == VarType.INPUT:
            self.vars[name] = VarType.INPUT_OUTPUT

    def load(self, name):
        previous = self.vars.get(name)
        if previous is None:
            self.vars[name] = VarType.INPUT

    def del_(self, name):
        previous = self.vars.get(name)
        if previous is None:
            self.vars[name] = VarType.INPUT
        elif previous == VarType.INPUT_OUTPUT:
            self.vars[name] = VarType.INPUT
        elif previous == VarType.OUTPUT:
            del self.vars[name]


def parse_code(code):
    tree = ast.parse(code)
    visitor = _Visitor()
    visitor.visit(tree)
    return {
        'inputs': {
            name for name, type_ in visitor.vars.items()
            if type_ in (VarType.INPUT, VarType.INPUT_OUTPUT)
        },
        'outputs': {
            name for name, type_ in visitor.vars.items()
            if type_ in (VarType.OUTPUT, VarType.INPUT_OUTPUT)
        },
        'imports': visitor.imports,
    }


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


@register('script.Python', inputs=['code', 'env'], outputs=['env', 'streams'])
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
