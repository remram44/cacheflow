import logging
import shutil
import tempfile


logger = logging.getLogger(__name__)


class Executor(object):
    def __init__(self, cache, component_loaders):
        self.cache = cache
        self.component_loaders = component_loaders

    def load_component(self, component_def):
        for loader in self.component_loaders:
            obj = loader.get_component(component_def)
            if obj is not None:
                return obj
        raise KeyError("Missing component")

    def execute(self, workflow, sinks=None, globals=None):
        """Execute a workflow.

        :param workflow: Workflow whose steps will be executed.
        :param sinks: An iterable of step IDs that we want executed, or
        ``None`` to indicate all the sinks need to be executed.
        :param globals: Global values which get passed to every step.
        :return: A dictionary mapping output references to values.
        """
        temp_dir = tempfile.mkdtemp(prefix='cacheflow_')
        logger.info("Executing workflow, temp_dir=%r", temp_dir)

        if globals is None:
            globals = {}

        if sinks is not None and not hasattr(sinks, 'items'):
            e = {}
            sinks = {step_id: e for step_id in sinks}

        # TODO: Only load & execute up to the sinks

        # Load the component
        steps = {}
        for step in workflow.steps.values():
            mod = self.load_component(step.component_def)
            steps[step.id] = mod, dict(step.parameters)
        logger.info("Loaded %d components", len(steps))

        # Store dependencies
        dependencies = {step_id: set() for step_id in workflow.steps}
        dependents = {step_id: [] for step_id in workflow.steps}
        for conn in workflow.connections.values():
            dependencies[conn.to_step_id].add(conn.from_step_id)
            dependents[conn.from_step_id].append((
                conn.from_output_name,
                conn.to_step_id,
                conn.to_input_name,
            ))

        ready = {step_id for step_id in workflow.steps
                 if not dependencies[step_id]}
        to_execute = set(workflow.steps)

        # Execute
        results = {}
        while ready:
            step = workflow.steps[ready.pop()]
            to_execute.discard(step.id)

            # Run the step
            logger.info("Executing step %r", step.id)
            component, inputs = steps.pop(step.id)
            try:
                outputs = component(
                    inputs=inputs, output_names=step.outputs,
                    temp_dir=temp_dir, globals=globals,
                )
            except Exception:
                logger.exception("Got exception running component %r",
                                 component)
                shutil.rmtree(temp_dir)
                raise

            # Store global results
            if sinks is None:
                results[step.id] = outputs
            elif step.id in sinks:
                to_store = sinks[step.id]
                results[step.id] = store = {}
                for k, v in outputs.items():
                    if k in to_store:
                        store[k] = v

            # Pass the outputs to connected steps
            for output, to_step_id, to_input_name in dependents[step.id]:
                deps = dependencies[to_step_id]
                deps.discard(step.id)
                if not deps:
                    ready.add(to_step_id)
                    logger.info("Step %r now ready", to_step_id)
                steps[to_step_id][1].setdefault(to_input_name, []).append(
                    outputs[output]
                )

        shutil.rmtree(temp_dir)

        if to_execute:
            logger.error("Couldn't execute any step, %d remain",
                         len(to_execute))
            raise RuntimeError("Can't execute remaining steps")

        return results
