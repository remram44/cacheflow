import argparse
import logging
import os
import sys

from . import __version__
from .builtin_components import BuiltinComponentsLoader
from .cache import DirectoryCache
from .executor import Executor
from cacheflow.storage.json import load_workflow
from .python import BuiltinPythonLoader


def main():
    """Entrypoint for the ``cacheflow`` command.
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Command-line tool for Cacheflow, the caching workflow "
                    "engine",
    )
    parser.add_argument('--version', action='version',
                        version='cacheflow version %s' % __version__)
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(
        title="additional commands",
        metavar='', dest='cmd',
    )

    parser_run = subparsers.add_parser('run', help="Run a workflow")
    parser_run.add_argument('workflow', action='store')
    parser_run.set_defaults(func=run)

    args = parser.parse_args()

    if not args.func:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    args.func(args)


def run(args):
    with open(args.workflow) as fp:
        workflow = load_workflow(fp)

    cache_loc = os.path.abspath('_cf_cache')
    os.chdir(os.path.dirname(args.workflow))

    executor = Executor(DirectoryCache(cache_loc),
                        [BuiltinPythonLoader(), BuiltinComponentsLoader()])
    executor.execute(workflow)
