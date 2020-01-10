import logging
import shutil
import tempfile

from .cache.core import hash_value


logger = logging.getLogger(__name__)


class InternalCache(object):
    def __init__(self, cache, step_hash):
        self.cache = cache
        self.step_hash = step_hash

    def has_key(self, key):
        return self.cache.has_key((self.step_hash, 'internal', key))

    def retrieve(self, key):
        return self.cache.retrieve((self.step_hash, 'internal', key))

    def store(self, key, value):
        self.cache.store((self.step_hash, 'internal', key), value)


def hash_dict_list(dct):
    return {k: [(e, hash_value(e)) for e in v] for k, v in dct.items()}


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

        # Compute dependency map
        # TODO: Just have this in Workflow
        wf_dependencies = {step_id: set() for step_id in workflow.steps}
        for conn in workflow.connections.values():
            wf_dependencies[conn.to_step_id].add((
                conn.from_step_id,
                conn.from_output_name,
                conn.to_input_name,
            ))

        if sinks is not None:
            e = {}
            sinks = {step_id: e for step_id in sinks}

        # Steps to load
        if sinks:
            open_steps = set(sinks)
        else:
            open_steps = set(workflow.steps)

        # Load the component, store dependencies
        steps = {}  # loaded steps
        dependencies = {}  # non-ready dependencies of a step
        dependents = {}  # steps to notify on completion
        closed_steps = set()  # steps already loaded
        while open_steps:
            open_steps_, open_steps = open_steps, []
            closed_steps.update(open_steps_)
            for step_id in open_steps_:
                step = workflow.steps[step_id]
                # Load component
                component = self.load_component(step.component_def)
                steps[step.id] = component, hash_dict_list(step.parameters)
                # Record dependencies
                dependencies[step.id] = deps = set()
                for s, o, i in wf_dependencies[step.id]:
                    deps.add(s)
                    dependents.setdefault(s, []).append((o, step.id, i))
                    if s not in closed_steps:
                        open_steps.append(s)
                dependencies[step.id] = deps

        logger.info("Loaded %d components", len(steps))

        ready = {step_id for step_id in steps
                 if not dependencies[step_id]}
        to_execute = set(steps)

        # Execute
        results = {}
        while ready:
            step = workflow.steps[ready.pop()]
            to_execute.discard(step.id)

            # Run the step
            component, inputs = steps.pop(step.id)
            for k, v in inputs.items():
                if len(v) > 1:
                    raise ValueError("Multiple values for input '%s'" % k)
            step_hash = component.compute_hash({
                n: [e[1] for e in v] for n, v in inputs.items()
            })
            internal_cache = InternalCache(
                self.cache,
                step_hash,
            )
            try:
                outputs = self.cache.retrieve((step_hash, 'outputs'))
            except KeyError:
                logger.info("Executing step %r", step.id)
                try:
                    component.execute(
                        inputs={n: [e[0] for e in v] for n, v in inputs.items()},
                        output_names=step.outputs,
                        temp_dir=temp_dir, globals=globals,
                        cache=internal_cache,
                    )
                except Exception:
                    logger.exception("Got exception running component %r",
                                     component)
                    shutil.rmtree(temp_dir)
                    raise
                outputs = component.outputs
                self.cache.store((step_hash, 'outputs'), outputs)
            else:
                logger.info("Got step %r from cache", step.id)

            # Store global results
            if sinks is None:
                results[step.id] = {k: v[0] for k, v in outputs.items()}
            elif step.id in sinks:
                to_store = sinks[step.id]
                store = {}
                for k, v in outputs.items():
                    if k in to_store:
                        store[k] = v[0]
                results[step.id] = store

            # Pass the outputs to connected steps
            if step.id in dependents:
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
