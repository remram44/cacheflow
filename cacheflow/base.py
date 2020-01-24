from hashlib import sha256

from .cache.core import UNHASHABLE, hash_value


class StepInputConnection(object):
    def __init__(self, source_step_id, source_output_name):
        self.source_step_id = source_step_id
        self.source_output_name = source_output_name

    def __repr__(self):
        return '%s.%s' % (self.source_step_id, self.source_output_name)


class Step(object):
    def __init__(self, id, component_def, inputs, *, position=None):
        self.id = id
        self.component_def = component_def
        self.inputs = inputs
        if position:
            self.position = position
        else:
            self.position = [0, 0]

    def __repr__(self):
        return '<Step {!r} type={!r} inputs={{{}}}>'.format(
            self.id,
            self.component_def.get('type'),
            ', '.join('%s=%r' % p for p in sorted(self.inputs.items())),
        )


class Workflow(object):
    def __init__(self, steps, meta):
        self.steps = steps
        self.meta = meta

    def __repr__(self):
        return '<Workflow\n  steps:{}\n  meta={!r}>'.format(
            ''.join('\n    {!r}'.format(s) for s in self.steps.values()),
            self.meta,
        )


class Component(object):
    """A workflow component, as provided by a `ComponentLoader`.
    """
    def __init__(self, pickling):
        self.outputs = {}
        self.pickling = pickling

    def set_output(self, name, value, hash=None):
        if not hash:
            hash = hash_value(value, self.pickling)
        self.outputs[name] = value, hash

    def execute(self, inputs, output_names, **kwargs):
        """Run on the inputs to provide outputs.
        """
        raise NotImplementedError

    @classmethod
    def compute_hash(cls, input_hashes):
        fqdn = ('%s.%s\n' % (cls.__module__, cls.__name__))
        h = sha256(fqdn.encode())
        for i_n, i_hs in sorted(input_hashes.items()):
            for i_h in i_hs:
                if i_h == UNHASHABLE:
                    return UNHASHABLE
                h.update(('%s\n%s\n' % (i_n, i_h)).encode())
        return h.hexdigest()


class ComponentLoader(object):
    """Component loader, capable of providing workflow components.
    """
    def get_component(self, component_def):
        """Returns a component or None.
        """
        raise NotImplementedError

    def get_component_info(self, component_def):
        raise NotImplementedError

    def list_components(self):
        """Returns an iterable of pairs `(info, component_def)`

        The `info` dict should at least contain an entry `label`.
        """
        return ()


class _SimpleComponentLoaderNamespace(object):
    def __init__(self, table, namespace):
        self.table = table
        self.namespace = namespace

    def __call__(self, name=None, label=None, inputs=None, outputs=None):
        def wrapper(cls):
            if name is None:
                name_ = cls.__name__
            else:
                name_ = name
            if label is None:
                label_ = cls.__name__
            else:
                label_ = label
            self.table[self.namespace + name_] = (
                cls,
                {
                    'label': label_,
                    'inputs': inputs or [], 'outputs': outputs or [],
                },
            )

        return wrapper

    def namespace(self, name):
        return _SimpleComponentLoaderNamespace(
            self.table,
            self.namespace + name + '.',
        )


class SimpleComponentLoader(ComponentLoader, _SimpleComponentLoaderNamespace):
    """Default component loader, allowing to easily register components.
    """
    def __init__(self):
        _SimpleComponentLoaderNamespace.__init__(self, {}, '')

    def get_component(self, component_def):
        if 'type' in component_def:
            try:
                return self.table[component_def['type']][0]
            except KeyError:
                pass
        return None

    def get_component_info(self, component_def):
        if 'type' in component_def:
            try:
                return self.table[component_def['type']][1]
            except KeyError:
                pass
        return None

    def list_components(self):
        res = []
        for name, (_cls, info) in self.table.items():
            res.append((info, {'type': name}))
        return res
