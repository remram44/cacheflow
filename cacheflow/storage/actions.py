from copy import copy

from ..base import Workflow, StepInputConnection


class ActionError(ValueError):
    """Error applying a workflow action.
    """


class BaseAction(object):
    def __init__(self, steps):
        self.steps = steps

    def apply(self, workflow):
        raise NotImplementedError


class AddStep(BaseAction):
    def __init__(self, step):
        super(AddStep, self).__init__(())
        self.step = step

    def apply(self, workflow):
        if self.step.id in workflow.steps:
            raise ActionError("Can't add step that's already there")
        steps = dict(workflow.steps)
        steps[self.step.id] = self.step
        return Workflow(steps=steps, meta=workflow.meta)


class RemoveStep(BaseAction):
    def __init__(self, step_id):
        super(RemoveStep, self).__init__((step_id,))
        self.step_id = step_id

    def apply(self, workflow):
        if self.step_id not in workflow.steps:
            raise ActionError("Can't remove step that's not there")
        steps = dict(workflow.steps)
        del steps[self.step_id]
        return Workflow(steps=steps, meta=workflow.meta)


class AddInputParameter(BaseAction):
    def __init__(self, step_id, input_name, index, value):
        super(AddInputParameter, self).__init__((step_id,))
        self.step_id = step_id
        self.input_name = input_name
        self.index = index
        self.value = value

    def apply(self, workflow):
        if self.step_id not in workflow.steps:
            raise ActionError("Can't add input to step that's not there")
        steps = dict(workflow.steps)
        steps[self.step_id] = step = copy(steps[self.step_id])
        inputs = step.inputs.get(self.input_name, ())
        if not (0 <= self.index <= len(inputs)):
            raise ActionError("Invalid index to insert input parameter")
        inputs = inputs[:self.index] + (self.value,) + inputs[self.index:]
        step.inputs[self.input_name] = inputs
        return Workflow(steps, workflow.meta)


class AddInputConnection(BaseAction):
    def __init__(self, step_id, input_name, index,
                 source_step_id, source_output_name):
        super(AddInputConnection, self).__init__((step_id,))
        self.step_id = step_id
        self.input_name = input_name
        self.index = index
        self.source_step_id = source_step_id
        self.source_output_name = source_output_name

    def apply(self, workflow):
        if self.step_id not in workflow.steps:
            raise ActionError("Can't add input to step that's not there")
        steps = dict(workflow.steps)
        steps[self.step_id] = step = copy(steps[self.step_id])
        inputs = step.inputs.get(self.input_name, ())
        if not (0 <= self.index <= len(inputs)):
            raise ActionError("Invalid index to insert input connection")
        conn = StepInputConnection(
            self.source_step_id,
            self.source_output_name,
        )
        inputs = inputs[:self.index] + (conn,) + inputs[self.index:]
        step.inputs[self.input_name] = inputs
        return Workflow(steps, workflow.meta)


class RemoveInput(BaseAction):
    def __init__(self, step_id, input_name, index):
        super(RemoveInput, self).__init__((step_id,))
        self.step_id = step_id
        self.input_name = input_name
        self.index = index

    def apply(self, workflow):
        if self.step_id not in workflow.steps:
            raise ActionError("Can't remove input to step that's not there")
        steps = dict(workflow.steps)
        steps[self.step_id] = step = copy(steps[self.step_id])
        inputs = step.inputs.get(self.input_name, ())
        if not (0 <= self.index < len(inputs)):
            raise ActionError("Invalid input to remove from step")
        inputs = inputs[:self.index] + inputs[self.index + 1:]
        step.inputs[self.input_name] = inputs
        return Workflow(steps, workflow.meta)


class MoveStep(BaseAction):
    def __init__(self, step_id, position):
        super(MoveStep, self).__init__((step_id,))
        self.step_id = step_id
        self.position = position

    def apply(self, workflow):
        if self.step_id not in workflow.steps:
            raise ActionError("Can't move step that's not there")
        steps = dict(workflow.steps)
        steps[self.step_id] = step = copy(steps[self.step_id])
        step.position = self.position
        return Workflow(steps, workflow.meta)
