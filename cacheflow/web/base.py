import json
import logging
import tornado.web


logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """Base class for all request handlers.
    """
    def get_json(self):
        type_ = self.request.headers.get('Content-Type', '')
        if not type_.startswith('application/json'):
            raise tornado.web.HTTPError(400, "Expected JSON")
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError:
            raise tornado.web.HTTPError(400, "Invalid JSON")

    def send_json(self, obj):
        if isinstance(obj, list):
            obj = {'results': obj}
        elif not isinstance(obj, dict):
            raise ValueError("Can't encode %r to JSON" % type(obj))
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        return self.finish(json.dumps(obj))

    def send_error_json(self, status, message):
        logger.info("Sending error %s JSON: %s", status, message)
        self.set_status(status)
        return self.send_json({'error': message})


class CorsHandler(BaseHandler):
    def prepare(self):
        super(BaseHandler, self).prepare()
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')

    def options(self):
        # CORS pre-flight
        self.set_status(204)
        return self.finish()


class Application(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super(Application, self).__init__(handlers, **kwargs)
