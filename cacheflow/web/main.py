import argparse
import json
import logging
import pkg_resources
import tornado.ioloop
import tornado.iostream
from tornado.routing import URLSpec
import tornado.web
from tornado.websocket import WebSocketHandler
import webbrowser

from .. import __version__
from ..base import Step, StepInputConnection, Workflow
from ..cache import NullCache
from ..executor import Executor
from ..storage.controller import WorkflowChangeObserver, WorkflowController
from .base import BaseHandler
from .json import workflow_to_json, json_to_actions, action_to_json


logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super(Application, self).__init__(handlers, **kwargs)

        self.client_sockets = set()

        executor = Executor(NullCache())
        executor.add_components_from_entrypoint()

        workflow = Workflow(
            {
                '01aeb224-8312-4bbe-ba3b-5ea3198f3c5c': Step(
                    '01aeb224-8312-4bbe-ba3b-5ea3198f3c5c',
                    {'type': 'Download'},
                    {
                        'headers': [
                            'accept: application/ld+json; ' +
                            'profile="https://www.w3.org/ns/activitystreams"',
                        ],
                        'url': ['https://framapiaf.org/@remram44'],
                    },
                ),
                '02a716e6-e11c-43c2-b50e-4a80083d0456': Step(
                    '02a716e6-e11c-43c2-b50e-4a80083d0456',
                    {'type': 'script.Python'},
                    {
                        'code': [
                            'with open(webpage.name, \'rb\') as fp:\n' +
                            '    contents = fp.read()\n'
                        ],
                        'webpage': [StepInputConnection(
                            '01aeb224-8312-4bbe-ba3b-5ea3198f3c5c',
                            'file',
                        )],
                    },
                    position=[300, 200],
                ),
                '03bf3df2-e1d3-4c4e-9b99-ad3072bded03': Step(
                    '03bf3df2-e1d3-4c4e-9b99-ad3072bded03',
                    {'type': 'script.Python'},
                    {
                        'code': [
                            'print(len(contents))\n',
                        ],
                        'env': [StepInputConnection(
                            '02a716e6-e11c-43c2-b50e-4a80083d0456',
                            'env',
                        )],
                    },
                    position=[600, 300],
                ),
            },
            {},
        )

        self.controller = WorkflowController(workflow, executor)


class WorkflowWS(WebSocketHandler, WorkflowChangeObserver):
    def open(self):
        self.application.controller.add_change_observer(self)
        logger.info("WebSocket connected")

        # Send components library
        components = []
        for loader in self.application.controller.executor.component_loaders:
            for info, component_def in loader.list_components():
                comp_dict = dict(info, component_def=component_def)
                comp_dict.setdefault('inputs', [])
                comp_dict.setdefault('outputs', [])
                components.append(comp_dict)
        self.write_message({
            'type': 'components_add',
            'components': components,
        })

        # Send current workflow
        self.write_message({
            'type': 'workflow',
            'workflow': workflow_to_json(
                self.application.controller,
            ),
        })

    # DEBUG
    def write_message(self, message):
        logger.info("< %s", message)
        super(WorkflowWS, self).write_message(message)

    def on_message(self, message):
        logger.info("> %s", message)  # DEBUG
        message = json.loads(message)
        type_ = message.pop('type')
        if type_.startswith('workflow_'):
            actions_array = json_to_actions(
                type_, message,
                self.application.controller,
            )
            for action in actions_array:
                self.application.controller.apply_action(action)
        else:
            logger.error("Got invalid message %r", type_)

    def on_close(self):
        self.application.controller.remove_change_observer(self)
        logger.info("WebSocket disconnected")

    def check_origin(self, origin):
        return True

    def on_workflow_action(self, action):
        # TODO: Send incremental updates
        if False:
            message = action_to_json(action, self.application.controller)
        else:
            message = {
                'type': 'workflow',
                'workflow': workflow_to_json(
                    self.application.controller,
                ),
            }
        self.write_message(message)


class Index(BaseHandler):
    def get(self):
        return self.redirect(self.reverse_url('workflow_view', 'default'))


class WorkflowView(BaseHandler):
    async def get(self, workflow_name):
        with pkg_resources.resource_stream(
                'cacheflow',
                'web/ui/index.html',
        ) as fp:
            while True:
                chunk = fp.read(4096)
                try:
                    self.write(chunk)
                    await self.flush()
                except tornado.iostream.StreamClosedError:
                    return
                if len(chunk) != 4096:
                    break


def make_app(debug=False):
    static_dir = pkg_resources.resource_filename('cacheflow', 'web/ui/static')
    return Application(
        [
            URLSpec('/', Index),
            URLSpec('/workflow/([^/]+)', WorkflowView, name='workflow_view'),
            URLSpec(
                '/static/(.*)', tornado.web.StaticFileHandler,
                {'path': static_dir},
            ),
            URLSpec('/workflow', WorkflowWS),
        ],
        # TODO: Security settings (CSRF, cookie, single-user auth token)
        xsrf_cookies=False,
        cookie_secret='1234567890',
        debug=debug,
    )


def main():
    logging.root.handlers.clear()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Web-based workflow system",
    )
    parser.add_argument('--version', action='version',
                        version='cacheflow version %s' % __version__)
    parser.add_argument('-p', '--port', default='7455',
                        help="Port number to listen on")
    parser.add_argument('-b', '--bind', default='127.0.0.1',
                        help="Address to bind on")
    parser.add_argument('--browser', action='store_true', default=True,
                        help="Open web browser to the application")
    parser.add_argument('--no-browser', action='store_false', dest='browser',
                        help="Don't open the web browser")
    parser.add_argument('--debug', action='store_true', default=False,
                        help=argparse.SUPPRESS)

    args = parser.parse_args()
    try:
        port = int(args.port, 10)
    except ValueError:
        return parser.error("Invalid port number")

    url = 'http://localhost:%d/' % port

    app = make_app(debug=args.debug)
    app.listen(port, args.bind)
    loop = tornado.ioloop.IOLoop.current()
    if args.browser and not args.debug:
        loop.call_later(0.01, webbrowser.open, url)
    loop.start()
