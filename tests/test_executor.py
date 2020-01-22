import unittest

from cacheflow import Executor
from cacheflow.base import Workflow, Component, ComponentLoader, \
    Step, StepInputConnection
from cacheflow.cache import NullCache


class MockComponent(Component):
    def __getattribute__(self, name):
        if name != Component.compute_hash.__name__:
            raise AttributeError(name)
        return object.__getattribute__(self, name)


class MockLoader(ComponentLoader):
    def get_component(self, component_def):
        return MockComponent


class TestLoading(unittest.TestCase):
    def executor(self):
        executor = Executor(NullCache)
        executor.add_components_loader(MockLoader())
        return executor

    def test_simple(self):
        """Test loading workflows."""
        executor = self.executor()
        executor.load_workflow(Workflow(
            {
                'one': Step('one', {'type': 'mock'}, {}),
                'two': Step('two', {'type': 'mock'}, {'i': ['v']}),
            },
            {},
        ))
        self.assertEqual(set(executor.steps), {'one', 'two'})
        self.assertEqual(executor.dependencies, {'one': set(), 'two': set()})
        self.assertEqual(executor.dependents, {'one': [], 'two': []})

        executor = self.executor()
        executor.load_workflow(Workflow(
            {
                'one': Step('one', {'type': 'mock'}, {}),
                'two': Step('two', {'type': 'mock'},
                            {'i': [StepInputConnection('one', 'o')]}),
            },
            {},
        ))
        self.assertEqual(set(executor.steps), {'one', 'two'})
        self.assertEqual(executor.dependencies, {'one': set(), 'two': {'one'}})
        self.assertEqual(
            executor.dependents,
            {'one': [('o', 'two', 'i')], 'two': []},
        )

        executor = self.executor()
        executor.load_workflow(Workflow(
            {},
            {},
        ))
        self.assertEqual(set(executor.steps), set())
        self.assertEqual(executor.dependencies, {})
        self.assertEqual(executor.dependents, {})

    def test_replace(self):
        """Test loading multiple workflows into the same executor."""
        executor = self.executor()

        executor.load_workflow(Workflow(
            {
                'one': Step('one', {'type': 'mock'}, {}),
                'two': Step('two', {'type': 'mock'}, {'i': ['v']}),
            },
            {},
        ))
        steps1 = {
            step_id: (id(comp), executor.step_hashes[step_id])
            for step_id, comp in executor.steps.items()
        }
        self.assertEqual(
            steps1, {
                'one': (steps1['one'][0], 'e654a5214e9805a3325ea921433c5d88' +
                        'b7e49fd075fad6c5153e7c589795b43d'),
                'two': (steps1['two'][0], 'a4b199ebd6b64a671b2d965080f779f2' +
                        '2317214ccf14c1cfae42b193cfbd4e4f'),
            }
        )

        executor.load_workflow(Workflow(
            {
                'one': Step('one', {'type': 'mock'}, {}),
                'two': Step('two', {'type': 'mock'}, {'i': ['x']}),
            },
            {},
        ))
        steps2 = {
            step_id: (id(comp), executor.step_hashes[step_id])
            for step_id, comp in executor.steps.items()
        }
        self.assertEqual(
            steps2, {
                # 'one' has same id()
                'one': (steps1['one'][0], 'e654a5214e9805a3325ea921433c5d88' +
                        'b7e49fd075fad6c5153e7c589795b43d'),
                # 'two' has different id()
                'two': (steps2['two'][0], 'c8ee525a0040b7cdda23a3ea68a3631c' +
                                          '3024ff39207a9952380bb57303885db7'),
            }
        )

        executor.load_workflow(Workflow(
            {
                'one': Step('one', {'type': 'mock'}, {}),
                'two': Step('two', {'type': 'mock'},
                            {'i': [StepInputConnection('one', 'o')]}),
            },
            {},
        ))
        steps3 = {
            step_id: (id(comp), executor.step_hashes[step_id])
            for step_id, comp in executor.steps.items()
        }
        self.assertEqual(
            steps3, {
                # 'one' has same id()
                'one': (steps1['one'][0], 'e654a5214e9805a3325ea921433c5d88' +
                        'b7e49fd075fad6c5153e7c589795b43d'),
                # 'two' has different id()
                'two': (steps3['two'][0], 'bbe5ecf88727384438ba89c42803a1fc' +
                                          '19beabed488efe0d0e313a322fe51967'),
            }
        )
