import yaml


class Workflow(object):
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
    def __init__(self, id, module_def, inputs, outputs, parameters):
        self.id = id
        self.module_def = module_def
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


def check_keys(obj, allowed_keys):
    keys = set(obj)
    keys.difference_update(allowed_keys)
    if keys:
        raise ValueError("Unrecognized keys: %s" % ', '.join(sorted(keys)))


def load_workflow(fileobj):
    obj = yaml.load(fileobj)

    check_keys(obj, ['meta', 'steps'])

    steps = {}
    connections = {}
    input_refs = []
    output_refs = {}
    for step in obj['steps']:
        check_keys(step, ['module', 'inputs', 'outputs', 'parameters',
                          'description'])
        step_id = len(steps)

        # Read inputs, which can also have the target of a connection
        inputs = set()
        for input in step.get('inputs', []):
            if isinstance(input, dict):
                [(name, ref)] = input.items()
                inputs.add(name)
                input_refs.append((step_id, name, ref))
            elif isinstance(input, str):
                inputs.add(input)
            else:
                raise ValueError("Invalid input")

        # Read outputs, which can also have a ref name for connection
        outputs = set()
        for output in step.get('outputs', []):
            if isinstance(output, dict):
                [(name, ref)] = output.items()
                outputs.add(name)
                if ref in output_refs:
                    raise ValueError("Duplicate output reference %s" % ref)
                output_refs[ref] = step_id, name
            else:
                raise ValueError("Invalid output")

        # Read parameters
        parameters = {}
        for param in step.get('parameters', []):
            if not isinstance(param, dict):
                raise ValueError("Invalid parameter")
            [(name, value)] = param.items()
            parameters.setdefault(name, []).append(value)

        # Store step
        steps[step_id] = Step(step_id, step['module'], inputs, outputs,
                              parameters)

    # Store connections
    for to_step_id, to_input_name, ref in input_refs:
        from_step_id, from_output_name = output_refs[ref]
        connections[len(connections)] = Connection(
            len(connections),
            from_step_id,
            from_output_name,
            to_step_id,
            to_input_name,
        )

    return Workflow(steps, connections, obj.get('meta', {}))
