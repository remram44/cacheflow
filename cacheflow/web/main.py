import logging
import os
import tornado.ioloop
import tornado.web
from tornado.routing import URLSpec

from .base import Application, CorsHandler


logger = logging.getLogger(__name__)


class Hello(CorsHandler):
    def get(self):
        return self.send_json({'test': True})

    def post(self):
        obj = self.get_json()
        return self.send_json({'test': True, 'hello': obj['hello'].upper()})


def make_app():
    return Application(
        [
            URLSpec('/hello', Hello),
        ],
        static_path=os.path.join(os.path.dirname(__name__), '../../ui/dist'),
        xsrf_cookies=False,
        cookie_secret='1234567890',
        debug=True,
    )


def main():
    logging.root.handlers.clear()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")

    app = make_app()
    app.listen(7455, '0.0.0.0')
    loop = tornado.ioloop.IOLoop.current()
    loop.start()
