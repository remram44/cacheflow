import argparse
import logging
import os
import sys
import yaml

from . import __version__
from .cache import DirectoryCache
from .executor import Executor
from cacheflow.storage.json import InvalidWorkflowJson, workflow_from_json


logger = logging.getLogger(__name__)


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
    try:
        with open(args.workflow) as fp:
            try:
                obj = yaml.safe_load(fp)
            except yaml.YAMLError:
                raise InvalidWorkflowJson("Invalid YAML")
        workflow = workflow_from_json(obj)
    except InvalidWorkflowJson as e:
        logger.error("Error loading workflow: %s", e)
        sys.exit(1)

    cache_loc = os.path.abspath('_cf_cache')
    os.chdir(os.path.dirname(args.workflow))

    executor = Executor(DirectoryCache(cache_loc))
    executor.add_components_from_entrypoint()
    executor.load_workflow(workflow)
    executor.execute()
