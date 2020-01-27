from copy import copy

from ..base import Step, StepInputConnection
from . import actions


class ChangeObserver(object):
    def on_workflow_action(self, action):
        pass


class WorkflowController(object):
    def __init__(self, workflow, executor=None):
        self.current_workflow = workflow
        self.executor = executor
        self._change_observers = set()
        self._connected_outputs_cache = None

    def apply_action(self, action):
        self.current_workflow = action.apply(self.current_workflow)
        for observer in self._change_observers:
            observer.on_workflow_action(action)

        # Invalidate cache
        self._connected_outputs_cache = None

    def execute(self):
        workflow = self.current_workflow
        self.executor.load_workflow(workflow)
        self.executor.execute()

    @property
    def steps(self):
        return _StepsProxy(self)

    def add_change_observer(self, observer):
        self._change_observers.add(observer)

    def remove_change_observer(self, observer):
        self._change_observers.discard(observer)

    def add_execution_observer(self, observer):
        if self.executor is not None:
            self.executor.add_execution_observer(observer)

    def remove_execution_observer(self, observer):
        if self.executor is not None:
            self.executor.remove_execution_observer(observer)

    @property
    def _connected_outputs(self):
        if self._connected_outputs_cache is None:
            self._connected_outputs_cache = {}
            for step in self.current_workflow.steps.values():
                for input_name, inputs in step.inputs.items():
                    for idx, input in enumerate(inputs):
                        if isinstance(input, StepInputConnection):
                            self._connected_outputs_cache \
                                .setdefault(input.source_step_id, {}) \
                                .setdefault(
                                    input.source_output_name,
                                    (step.id, input_name, idx),
                                )
        return self._connected_outputs_cache


class _StepsProxy(object):
    def __init__(self, controller):
        self._controller = controller

    def __getitem__(self, step_id):
        if step_id not in self._controller.current_workflow.steps:
            raise KeyError
        return _StepWrapper(self._controller, step_id)

    def __delitem__(self, step_id):
        if step_id not in self._controller.current_workflow.steps:
            raise KeyError
        action = actions.RemoveStep(step_id)
        self._controller.apply_action(action)

    def __setitem__(self, step_id, step):
        if not isinstance(step, Step):
            raise TypeError
        if step.id != step_id:
            raise ValueError
        step = copy(step)
        if step_id in self._controller.current_workflow.steps:
            action = actions.RemoveStep(step_id)
            self._controller.apply_action(action)
        action = actions.AddStep(step)
        self._controller.apply_action(action)

    def __iter__(self):
        return iter(self._controller.current_workflow.steps)

    def __contains__(self, step_id):
        return step_id in self._controller.current_workflow.steps

    def keys(self):
        return iter(self._controller.current_workflow.steps)

    def values(self):
        return (
            _StepWrapper(self._controller, step_id)
            for step_id in self._controller.current_workflow.steps
        )


class _StepWrapper(object):
    def __init__(self, controller, step_id):
        self._controller = controller
        self._step_id = step_id

    @property
    def id(self):
        return self._step_id

    def _step(self):
        return self._controller.current_workflow.steps[self._step_id]

    @property
    def position(self):
        return self._step().position

    @position.setter
    def position(self, position):
        position = tuple(position)
        if len(position) != 2:
            raise TypeError
        action = actions.MoveStep(self._step_id, position)
        self._controller.apply_action(action)

    @property
    def component_def(self):
        return self._step().component_def

    @property
    def inputs(self):
        return _StepInputsProxy(self._controller, self._step_id)

    @property
    def outputs(self):
        return _StepOutputsProxy(self._controller, self._step_id)


class _StepInputsProxy(object):
    def __init__(self, controller, step_id):
        self._controller = controller
        self._step_id = step_id

    def _step(self):
        return self._controller.current_workflow.steps[self._step_id]

    def __getitem__(self, input_name):
        return _StepInputProxy(self._controller, self._step_id, input_name)

    def __setitem__(self, input_name, values):
        if isinstance(values, str):
            values = (values,)
        elif not isinstance(values, (list, tuple)):
            raise TypeError
        step = self._step()
        for idx in reversed(range(len(step.inputs.get(input_name, ())))):
            action = actions.RemoveInput(step.id, input_name, idx)
            self._controller.apply_action(action)
        for idx, value in enumerate(values):
            if isinstance(value, Output):
                if value._controller is not self._controller:
                    raise ValueError("Can't connect steps across workflows")
                action = actions.AddInputConnection(
                    step.id, input_name, idx,
                    value.step_id, value.output_name,
                )
            elif isinstance(value, str):
                action = actions.AddInputParameter(
                    step.id, input_name,
                    idx, value,
                )
            else:
                raise TypeError
            self._controller.apply_action(action)

    def __delitem__(self, input_name):
        step = self._step()
        for idx in reversed(range(len(step.inputs.get(input_name, ())))):
            action = actions.RemoveInput(step.id, input_name, idx)
            self._controller.apply_action(action)

    def _inputs(self):
        step = self._step()

        # Get the connected inputs
        inputs = set(
            input_name
            for input_name, array in step.inputs.items()
            if array
        )

        executor = self._controller.executor
        if executor:
            # Add the declared inputs for this component
            component_info = None
            for loader in executor.component_loaders:
                component_info = loader.get_component_info(step.component_def)
                if component_info is not None:
                    break
            if component_info is not None:
                inputs.update(component_info.get('inputs', ()))

        return inputs

    def __iter__(self):
        return iter(self._inputs())

    def __contains__(self, input_name):
        return input_name in self._inputs()

    def keys(self):
        return iter(self._inputs())

    def values(self):
        return (
            _StepInputProxy(self._controller, self._step_id, input_name)
            for input_name in self._inputs()
        )

    def items(self):
        return (
            (
                input_name,
                _StepInputProxy(self._controller, self._step_id, input_name),
            )
            for input_name in self._inputs()
        )


def _wrap_output(v, controller):
    if isinstance(v, StepInputConnection):
        return Output(
            controller,
            v.source_step_id, v.source_output_name,
        )
    else:
        return v


class _StepInputProxy(object):
    def __init__(self, controller, step_id, input_name):
        self._controller = controller
        self._step_id = step_id
        self._input_name = input_name

    def _step(self):
        return self._controller.current_workflow.steps[self._step_id]

    def append(self, value):
        step = self._step()
        self.insert(len(step.inputs), value)

    def insert(self, idx, value):
        step = self._step()
        if isinstance(value, Output):
            if value._controller is not self._controller:
                raise ValueError("Can't connect steps across workflows")
            action = actions.AddInputConnection(
                step.id, self._input_name, idx,
                value.step_id, value.output_name,
            )
        elif isinstance(value, str):
            action = actions.AddInputParameter(
                step.id, self._input_name,
                idx, value,
            )
        else:
            raise TypeError
        self._controller.apply_action(action)

    def __getitem__(self, idx):
        step = self._step()
        return _wrap_output(step.inputs[idx], self._controller)

    def __setitem__(self, idx, value):
        del self[idx]
        self.insert(idx, value)

    def __delitem__(self, idx):
        step = self._step()
        action = actions.RemoveInput(step.id, self._input_name, idx)
        self._controller.apply_action(action)

    def __iter__(self):
        step = self._step()
        return (
            _wrap_output(v, self._controller)
            for v in step.inputs.get(self._input_name, ())
        )


class _StepOutputsProxy(object):
    def __init__(self, controller, step_id):
        self._controller = controller
        self._step_id = step_id

    def _step(self):
        return self._controller.current_workflow.steps[self._step_id]

    def __getitem__(self, output_name):
        return Output(self._controller, self._step_id, output_name)

    def _outputs(self):
        step = self._step()

        # Get the connected outputs
        outputs = set(
            self._controller._connected_outputs.get(self._step_id, ()),
        )

        executor = self._controller.executor
        if executor:
            # Add the declared outputs for this component
            component_info = None
            for loader in executor.component_loaders:
                component_info = loader.get_component_info(step.component_def)
                if component_info is not None:
                    break
            if component_info is not None:
                outputs.update(component_info.get('outputs', ()))

            # Get the actual outputs for this component
            # TODO: Get list of outputs from Executor

        return outputs

    def __iter__(self):
        return iter(self._outputs())

    def __contains__(self, output_name):
        return output_name in self._outputs()


class Output(object):
    def __init__(self, controller, step_id, output_name):
        self._controller = controller
        self.step_id = step_id
        self.output_name = output_name

    # TODO: Access outputs from Executor?
