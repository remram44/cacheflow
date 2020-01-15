import yaml

from ..base import Workflow, Step, StepInputConnection


__all__ = ['load_workflow']


class InvalidWorkflowJson(ValueError):
    """Workflow JSON is invalid.
    """


def check_keys(obj, required, optional, msg=''):
    if msg:
        msg = "%s: "
    if not isinstance(obj, dict):
        raise InvalidWorkflowJson(
            "%sExpected 'dict', got %r" % (msg, type(obj))
        )
    unknown_keys = set(obj)
    unknown_keys.difference_update(required)
    unknown_keys.difference_update(optional)
    if unknown_keys:
        raise InvalidWorkflowJson(
            "%sUnrecognized keys: %s" % (
                msg,
                ', '.join(sorted(unknown_keys)),
            )
        )
    missing_keys = set(required)
    missing_keys.difference_update(obj)
    if missing_keys:
        raise InvalidWorkflowJson(
            "%sMissing required keys: %s" % (
                msg, ', '.join(sorted(missing_keys))
            )
        )


def load_workflow(fileobj):
    """Loads a workflow from a JSON file.
    """
    try:
        obj = yaml.safe_load(fileobj)
    except yaml.YAMLError:
        raise InvalidWorkflowJson("Invalid YAML")

    check_keys(obj, ['steps'], ['meta'])

    steps = {}
    not_sink_steps = set()
    for step_id, step in obj['steps'].items():
        check_keys(
            step,
            ['component'],
            ['inputs', 'outputs', 'parameters', 'description'],
            "Step %r" % step_id,
        )

        inputs = {}

        # Read parameters
        for i, param in enumerate(step.get('parameters', [])):
            if not isinstance(param, dict):
                raise InvalidWorkflowJson(
                    "Step %r: Parameter #%d: not a dict" % (step_id, i)
                )
            if len(param) != 1:
                raise InvalidWorkflowJson(
                    "Step %r: Parameter #%d: "
                    "invalid dict size (should be 1)" % (step_id, i)
                )
            [(name, value)] = param.items()
            if not isinstance(value, str):
                raise InvalidWorkflowJson(
                    "Step %r: Parameter #%d (%r): value not a string" % (
                        step_id, i, name,
                    ),
                )
            inputs.setdefault(name, []).append(value)

        # Read inputs
        has_inputs = False
        for i, input in enumerate(step.get('inputs', [])):
            if not isinstance(input, dict):
                raise InvalidWorkflowJson(
                    "Step %r: Input #%d: not a dict" % (step_id, i)
                )
            if len(input) != 1:
                raise InvalidWorkflowJson(
                    "Step %r: Input #%d: "
                    "invalid dict size (should be 1)" % (step_id, i)
                )
            [(name, ref)] = input.items()
            if '.' not in ref:
                raise InvalidWorkflowJson(
                    "Step %r: Input #%d (%r): "
                    "invalid input reference (should be <step>.<output>)" % (
                        step_id, i, name,
                    )
                )
            source_step_id, source_output_name = ref.split('.', 1)
            inputs.setdefault(name, []).append(
                StepInputConnection(
                    source_step_id, source_output_name,
                )
            )
            has_inputs = True

        if has_inputs:
            not_sink_steps.add(step_id)

        # Store step
        steps[step_id] = Step(step_id, step['component'], inputs)

    return Workflow(steps, obj.get('meta', {}))
