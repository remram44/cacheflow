import logging
import sys

from .builtin_components import BuiltinComponentsLoader
from .cache import NullCache
from .executor import Executor
from .json import load_workflow
from .python import BuiltinPythonLoader


def main():
    """Entrypoint for the ``cacheflow`` command.
    """
    logging.basicConfig(level=logging.INFO)

    with open(sys.argv[1]) as fp:
        workflow = load_workflow(fp)

    executor = Executor(NullCache(),
                        [BuiltinPythonLoader(), BuiltinComponentsLoader()])
    executor.execute(workflow)