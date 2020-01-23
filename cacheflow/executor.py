import logging
from pkg_resources import iter_entry_points
import tempfile

from .base import StepInputConnection
from .cache.core import hash_value, UNHASHABLE, Pickling


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


def hash_dict_list(dct, pickling):
    return {
        k: [(e, hash_value(e, pickling)) for e in v]
        for k, v in dct.items()
    }


class Executor(object):
    def __init__(self, cache):
        self.cache = cache
        self.component_loaders = []

        self.workflow = None
        self.steps = {}
        self.step_hashes = ()

        self.temp_dir = tempfile.TemporaryDirectory(prefix='cacheflow_')
        self.pickling = Pickling(self.temp_dir.name)

    def add_components_from_entrypoint(self):
        for entry_point in iter_entry_points('cacheflow'):
            try:
                logger.info(
                    "Getting component loader from %r...",
                    entry_point.name,
                )
                loader = entry_point.load()
            except Exception:
                logger.exception(
                    "Components from plugin %r from %s %s failed to load",
                    entry_point.name,
                    entry_point.dist.project_name, entry_point.dist.version,
                )
            else:
                self.component_loaders.append(loader)

    def add_components_loader(self, loader):
        self.component_loaders.append(loader)

    def _load_component(self, component_def):
        for loader in self.component_loaders:
            cls = loader.get_component(component_def)
            if cls is not None:
                return cls
        logger.warning("Can't find component: %r", component_def)
        raise KeyError("Missing component")

    def _make_component(self, component_def):
        return self._load_component(component_def)(pickling=self.pickling)

    def load_workflow(self, workflow):
        """Load a workflow for execution.

        :param workflow: Workflow whose steps will be executed.
        """
        logger.info("Loading workflow...")
        self.workflow = workflow

        self._compute_dependency_maps()
        step_hashes = self._compute_step_hashes()

        # Remove steps that no longer exist
        outdated_steps = set(self.steps)
        outdated_steps.difference_update(self.workflow.steps)
        if outdated_steps:
            for step_id in outdated_steps:
                del self.steps[step_id]
            logger.info("Discarded %d old steps", len(outdated_steps))

        # Load all steps
        created = 0
        replaced = 0
        for step in self.workflow.steps.values():
            if step.id in self.steps:
                if step_hashes[step.id] == self.step_hashes[step.id]:
                    # This step is up to date!
                    continue
                replaced += 1

            self.steps[step.id] = self._make_component(step.component_def)
            created += 1
        if replaced:
            logger.info("Discarded %d changed steps", replaced)
        if created:
            logger.info("Created %d steps", created)

        self.step_hashes = step_hashes

    def _compute_dependency_maps(self):
        self.dependencies = {}
        self.dependents = {}

        for step in self.workflow.steps.values():
            # Process inputs
            self.dependencies[step.id] = deps = set()
            self.dependents[step.id] = []
            for name, inputs in step.inputs.items():
                for input in inputs:
                    if isinstance(input, StepInputConnection):
                        # Input is a connection: record the dependency
                        deps.add(input.source_step_id)
                        self.dependents[input.source_step_id].append((
                            input.source_output_name,
                            step.id,
                            name,
                        ))

        self.sources = {step_id for step_id in self.workflow.steps
                        if not self.dependencies[step_id]}
        self.sinks = {step_id for step_id in self.workflow.steps
                      if not self.dependents[step_id]}

    def _compute_step_hashes(self):
        step_hashes = {}

        # TODO: Have this not be recursive (similarly to the execution code)
        def compute_hash(step_id):
            step = self.workflow.steps[step_id]

            # Build a dictionary of input hashes
            input_hashes = {}
            for name, inputs in sorted(step.inputs.items()):
                if not inputs:
                    continue
                input_hashes_list = []
                for input in inputs:
                    if isinstance(input, StepInputConnection):
                        # Recursively compute that hash
                        if input.source_step_id not in step_hashes:
                            compute_hash(input.source_step_id)

                        # Use the source's hash for input connections
                        value = '&%s\n%s' % (
                            input.source_output_name,
                            step_hashes[input.source_step_id],
                        )
                    else:
                        # Use the value itself for constant parameters
                        value = '=\n%s', hash_value(input, self.pickling)
                    input_hashes_list.append(value)
                input_hashes[name] = input_hashes_list

            # Use Component's hashing function to build a hash
            component_cls = self._load_component(step.component_def)
            step_hashes[step.id] = component_cls.compute_hash(input_hashes)

        for step_id in self.sinks:
            compute_hash(step_id)

        if set(step_hashes) != set(self.workflow.steps):
            raise RuntimeError("Couldn't compute all step hashes (cycle?)")

        return step_hashes

    def execute(self, sinks=None, globals=None):
        """Execute a workflow.

        :param sinks: An iterable of step IDs that we want executed, or
        ``None`` to indicate all the sinks need to be executed.
        :param globals: Global values which get passed to every step.
        :return: A dictionary mapping output references to values.
        """
        if self.workflow is None:
            raise ValueError("No workflow loaded")

        logger.info("Executing workflow, temp_dir=%r", self.temp_dir.name)

        if globals is None:
            globals = {}

        step_inputs = {}  # step_id: (set(missing inputs), [inputs])
        for step in self.workflow.steps.values():
            inputs = {
                name: [
                    (v, hash_value(v, self.pickling))
                    for v in values
                    if not isinstance(v, StepInputConnection)
                ]
                for name, values in step.inputs.items()
            }
            step_inputs[step.id] = set(self.dependencies[step.id]), inputs

        if sinks:
            to_execute = set(sinks)

            # Also add transitive dependencies of the sinks
            open_list = list(sinks)
            while open_list:
                process_list, open_list = open_list, []
                for step_id in process_list:
                    for dep_id in self.dependencies[step_id]:
                        if dep_id not in to_execute:
                            to_execute.add(dep_id)
                            open_list.append(dep_id)
        else:
            # Execute everything
            sinks = self.workflow.steps
            to_execute = set(self.workflow.steps)

        ready = {step_id for step_id in to_execute
                 if not self.dependencies[step_id]}

        # Execute
        results = {}
        while ready:
            step = self.workflow.steps[ready.pop()]
            to_execute.discard(step.id)

            # Run the step
            component = self.steps[step.id]
            inputs = step_inputs[step.id][1]
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
            outputs = None
            if step_hash != UNHASHABLE:
                try:
                    outputs = self.cache.retrieve(
                        (step_hash, 'outputs'),
                        pickling=self.pickling,
                    )
                except KeyError:
                    pass
                else:
                    logger.info("Got step %r from cache", step.id)
            if outputs is None:
                logger.info("Executing step %r", step.id)
                try:
                    component.execute(
                        inputs={
                            n: [e[0] for e in v]
                            for n, v in inputs.items()
                        },
                        temp_dir=self.temp_dir.name, globals=globals,
                        cache=internal_cache,
                    )
                except Exception:
                    logger.exception("Got exception running component %r",
                                     component)
                    raise
                outputs = component.outputs
                if step_hash != UNHASHABLE:
                    self.cache.store(
                        (step_hash, 'outputs'), outputs,
                        pickling=self.pickling,
                    )

            # Store global results
            if step.id in sinks:
                store = {}
                for k, v in outputs.items():
                    store[k] = v[0]
                results[step.id] = store

            # Pass the outputs to connected steps
            for output, to_step_id, to_input_name in self.dependents[step.id]:
                deps = step_inputs[to_step_id][0]
                deps.discard(step.id)
                if not deps:
                    ready.add(to_step_id)
                    logger.info("Step %r now ready", to_step_id)
                try:
                    value = outputs[output]
                except KeyError:
                    raise KeyError("Step %r did not set an output %r" % (
                        step.id, output,
                    )) from None
                else:
                    step_inputs[to_step_id][1] \
                        .setdefault(to_input_name, []) \
                        .append(value)

        if to_execute:
            logger.error("Couldn't execute any step, %d remain",
                         len(to_execute))
            raise RuntimeError("Can't execute remaining steps")

        return results
