import logging


logger = logging.getLogger(__name__)


class Executor(object):
    def __init__(self, cache, module_loaders):
        self.cache = cache
        self.module_loaders = module_loaders

    def load_module(self, module):
        for loader in self.module_loaders:
            obj = loader.get_module(module)
            if obj is not None:
                return obj
        raise KeyError("Missing module")

    def execute(self, workflow):
        logger.info("Executing workflow")

        # Load the modules
        steps = {}
        for step in workflow.steps.values():
            mod = self.load_module(step.module_def)
            steps[step.id] = mod, dict(step.parameters)
        logger.info("Loaded %d modules", len(steps))

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
        while ready:
            step = workflow.steps[ready.pop()]
            to_execute.discard(step.id)

            # Run the module
            logger.info("Executing step %r", step.id)
            module, inputs = steps[step.id]
            try:
                outputs = module(inputs, step.outputs)
            except Exception:
                logger.exception("Got exception running module %r",
                                 module)
                raise

            for output, to_step_id, to_input_name in dependents[step.id]:
                deps = dependencies[to_step_id]
                deps.discard(step.id)
                if not deps:
                    ready.add(to_step_id)
                    logger.info("Step %r now ready", to_step_id)
                steps[to_step_id][1].setdefault(to_input_name, []).append(
                    outputs[output]
                )

        if to_execute:
            logger.error("Couldn't execute any step, %d remain",
                         len(to_execute))
            raise RuntimeError("Can't execute remaining steps")
