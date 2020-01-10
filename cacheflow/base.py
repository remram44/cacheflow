class Component(object):
    """A workflow component, as provided by a `ComponentLoader`.
    """
    def __call__(self, inputs, output_names, **kwargs):
        """Run on the inputs to provide outputs.
        """
        raise NotImplementedError


class ComponentLoader(object):
    """Component loader, capable of providing workflow components.
    """
    def get_component(self, component_def):
        """Returns a component or None.
        """
        raise NotImplementedError


class Workflow(object):
    # TODO: Add more indexes in here (connection from step, ...)
    # TODO: Provide an abstract base for this too (for SQL backend)
    def __init__(self, steps, connections, meta):
        self.steps = steps
        self.connections = connections
        self.meta = meta

    def __repr__(self):
        return '<Workflow\n  steps:{}\n  connections:{}\n  meta={!r}>'.format(
            ''.join('\n    {!r}'.format(s) for s in self.steps.values()),
            ''.join('\n    {!r}'.format(c) for c in self.connections.values()),
            self.meta,
        )


class Step(object):
    def __init__(self, id, component_def, inputs, outputs, parameters):
        self.id = id
        self.component_def = component_def
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters

    def __repr__(self):
        return '<Step {!r} inputs={!r} outputs={!r} parameters={!r}>'.format(
            self.id,
            sorted(self.inputs),
            sorted(self.outputs),
            list(self.parameters),
        )


class Connection(object):
    def __init__(self, id,
                 from_step_id, from_output_name, to_step_id, to_input_name):
        self.id = id
        self.from_step_id = from_step_id
        self.from_output_name = from_output_name
        self.to_step_id = to_step_id
        self.to_input_name = to_input_name

    def __repr__(self):
        return '<Connection {!r} {!r}.{!r} --> {!r}.{!r}>'.format(
            self.id,
            self.from_step_id,
            self.from_output_name,
            self.to_step_id,
            self.to_input_name,
        )
