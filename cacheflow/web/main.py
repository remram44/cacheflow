import argparse
import logging
import pkg_resources
import tornado.ioloop
import tornado.iostream
from tornado.routing import URLSpec
import tornado.web
import webbrowser

from .. import __version__
from ..base import Step, StepInputConnection, Workflow
from ..cache import NullCache
from ..executor import Executor
from ..storage.controller import WorkflowController
from .base import BaseHandler
from . import api


logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super(Application, self).__init__(handlers, **kwargs)

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
            URLSpec('/workflow', api.WorkflowWS),
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
