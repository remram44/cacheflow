import logging
import os
import tornado.ioloop
import tornado.web
from tornado.routing import URLSpec
from tornado.websocket import WebSocketHandler

from ..base import Workflow, Step, StepInputConnection


logger = logging.getLogger(__name__)


def to_json(workflow):
    # Translate the list of steps
    steps = {}
    for step in workflow.steps.values():
        inputs_dict = {}
        for name, inputs in step.inputs.items():
            input_array = []
            for input in inputs:
                if isinstance(input, StepInputConnection):
                    input_array.append({
                        'step': input.source_step_id,
                        'output': input.source_output_name,
                    })
                else:
                    input_array.append(input)
            inputs_dict[name] = input_array
        steps[step.id] = {
            'component': step.component_def,
            'inputs': inputs_dict,
            'outputs': set(),
            'position': step.position,
        }

    # Fill in inputs and outputs
    for step in workflow.steps.values():
        # Put all the ports that are connected
        for inputs in step.inputs.values():
            for input in inputs:
                if isinstance(input, StepInputConnection):
                    steps[input.source_step_id]['outputs'].add(
                        input.source_output_name,
                    )
        # FIXME: Get additional information from executor/controller
        if step.component_def['type'] == 'script.python':
            steps[step.id]['inputs'].setdefault('env', [])
            steps[step.id]['outputs'].add('env')
        elif step.component_def['type'] == 'download':
            steps[step.id]['inputs'].setdefault('url', [])
            steps[step.id]['inputs'].setdefault('headers', [])
            steps[step.id]['outputs'].add('file')
    for step in steps.values():
        step['outputs'] = sorted(step['outputs'])

    return {'steps': steps, 'meta': workflow.meta}


class Application(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super(Application, self).__init__(handlers, **kwargs)
        self.workflow = Workflow(
            {
                '01aeb224-8312-4bbe-ba3b-5ea3198f3c5c': Step(
                    '01aeb224-8312-4bbe-ba3b-5ea3198f3c5c',
                    {'type': 'download'},
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
                    {'type': 'script.python'},
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
                ),
                '03bf3df2-e1d3-4c4e-9b99-ad3072bded03': Step(
                    '03bf3df2-e1d3-4c4e-9b99-ad3072bded03',
                    {'type': 'script.python'},
                    {
                        'code': [
                            'print(len(contents))\n',
                        ],
                        'env': [StepInputConnection(
                            '02a716e6-e11c-43c2-b50e-4a80083d0456',
                            'env',
                        )],
                    },
                ),
            },
            {},
        )


class WorkflowWS(WebSocketHandler):
    def open(self):
        logger.info("WebSocket connected")
        self.write_message(to_json(self.application.workflow))

    def on_message(self, message):
        pass

    def on_close(self):
        logger.info("WebSocket disconnected")

    def check_origin(self, origin):
        return True


def make_app():
    return Application(
        [
            URLSpec('/workflow', WorkflowWS),
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
