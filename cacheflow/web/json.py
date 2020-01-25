import logging
from uuid import uuid4

from ..base import Step
from ..storage import actions
from ..storage.controller import Output


logger = logging.getLogger(__name__)


def _inputs_to_json(step):
    inputs_dict = {}
    for name, inputs in step.inputs.items():
        input_array = []
        for input in inputs:
            if isinstance(input, Output):
                input_array.append({
                    'step': input.step_id,
                    'output': input.output_name,
                })
            else:
                input_array.append(input)
        inputs_dict[name] = input_array
    return inputs_dict


def workflow_to_json(controller):
    steps = {}
    for step in controller.steps.values():
        steps[step.id] = {
            'component': step.component_def,
            'inputs': _inputs_to_json(step),
            'outputs': list(step.outputs),
            'position': step.position,
        }

    return {'steps': steps, 'meta': controller.current_workflow.meta}


def _unset_input(workflow, step_id, input_name):
    step = workflow.steps[step_id]
    actions_array = []
    for idx in reversed(range(len(step.inputs.get(input_name, ())))):
        actions_array.append(actions.RemoveInput(step_id, input_name, idx))
    return actions_array


def json_to_actions(type_, message, controller):
    if type_ == 'workflow_add_step':
        return [actions.AddStep(
            Step(
                str(uuid4()), message['component_def'], {},
                position=message['position'],
            )
        )]
    elif type_ == 'workflow_remove_step':
        step_id = message['step_id']
        actions_array = []
        # Remove connections from this step
        connected_outputs = controller._connected_outputs.get(step_id, ())
        for dest_step_id, input_name, idx in connected_outputs:
            actions_array.append(actions.RemoveInput(
                dest_step_id,
                input_name,
                idx,
            ))
        # Remove the step
        actions_array.append(actions.RemoveStep(step_id))
        return actions_array
    elif type_ == 'workflow_set_input_parameter':
        step_id = message['step_id']
        input_name = message['input_name']
        actions_array = _unset_input(
            controller.current_workflow,
            step_id, input_name,
        )
        actions_array.append(actions.AddInputParameter(
            step_id,
            input_name,
            0,
            message['value'],
        ))
        return actions_array
    elif type_ == 'workflow_set_input_connection':
        step_id = message['step_id']
        input_name = message['input_name']
        actions_array = _unset_input(
            controller.current_workflow,
            step_id, input_name,
        )
        actions_array.append(actions.AddInputConnection(
            step_id,
            input_name,
            0,
            message['source_step_id'],
            message['source_output_name'],
        ))
        return actions_array
    elif type_ == 'workflow_remove_inputs':
        return _unset_input(
            controller.current_workflow,
            message['step_id'], message['input_name'],
        )
    elif type_ == 'workflow_move_step':
        return [actions.MoveStep(
            message['step_id'],
            message['position'],
        )]
    else:
        logger.error("Got invalid action type %r", type_)
        return ()


def action_to_json(action, controller):
    raise RuntimeError("Untested")  # TODO: action_to_json()

    if isinstance(action, actions.AddStep):
        step = controller.steps[action.step.id]
        return {
            'type': 'workflow_add_step',
            'component': step.component_def,
            'inputs': _inputs_to_json(step),
            'outputs': list(step.outputs),
            'position': step.position,
        }
    elif isinstance(action, actions.RemoveStep):
        return {'type': 'workflow_remove_step', 'step_id': action.step_id}
    elif isinstance(action, actions.AddInputParameter):
        return {
            'type': 'workflow_add_input_parameter',
            'step_id': action.step_id, 'input_name': action.input_name,
            'index': action.index, 'value': action.value,
        }
    elif isinstance(action, actions.AddInputConnection):
        return {
            'type': 'workflow_add_input_connection',
            'step_id': action.step_id, 'input_name': action.input_name,
            'index': action.index,
            'source_step_id': action.source_step_id,
            'source_output_name': action.source_output_name,
        }
    elif isinstance(action, actions.RemoveInput):
        return {
            'type': 'workflow_remove_input',
            'step_id': action.step_id, 'input_name': action.input_name,
            'index': action.index,
        }
    elif isinstance(action, actions.MoveStep):
        return {
            'type': 'workflow_move_step',
            'step_id': action.step_id, 'position': action.position,
        }
    else:
        raise TypeError
