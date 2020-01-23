import json
import logging
import os
import tornado.ioloop
import tornado.web
from tornado.routing import URLSpec
from tornado.websocket import WebSocketHandler

from ..base import Step, StepInputConnection, Workflow
from ..cache import NullCache
from ..executor import Executor
from ..storage import actions


logger = logging.getLogger(__name__)


def workflow_to_json(workflow):
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
        if step.component_def['type'] == 'script.Python':
            steps[step.id]['inputs'].setdefault('env', [])
            steps[step.id]['outputs'].add('env')
        elif step.component_def['type'] == 'Download':
            steps[step.id]['inputs'].setdefault('url', [])
            steps[step.id]['inputs'].setdefault('headers', [])
            steps[step.id]['outputs'].add('file')
    for step in steps.values():
        step['outputs'] = sorted(step['outputs'])

    return {'steps': steps, 'meta': workflow.meta}


def json_to_action(type_, message):
    # TODO: Implement other actions
    if type_ == 'workflow_remove_step':
        return actions.RemoveStep(message['step_id'])
    else:
        logger.error("Got invalid action type %r", type_)
        return


def action_to_json(action):
    # TODO: Implement other actions
    if isinstance(action, actions.RemoveStep):
        return {'type': 'workflow_remove_step', 'step_id': action.step_id}
    else:
        raise TypeError


class Application(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super(Application, self).__init__(handlers, **kwargs)

        self.client_sockets = set()

        self.executor = Executor(NullCache())
        self.executor.add_components_from_entrypoint()

        self.workflow = Workflow(
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

    def add_socket(self, socket):
        self.client_sockets.add(socket)

    def remove_socket(self, socket):
        self.client_sockets.discard(socket)

    def apply_action(self, action):
        self.workflow = action.apply(self.workflow)

        message = action_to_json(action)
        for socket in self.client_sockets:
            socket.write_message(message)


class WorkflowWS(WebSocketHandler):
    def open(self):
        self.application.add_socket(self)
        logger.info("WebSocket connected")

        # Send components library
        components = []
        for loader in self.application.executor.component_loaders:
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
            'workflow': workflow_to_json(self.application.workflow),
        })

    def on_message(self, message):
        message = json.loads(message)
        type_ = message.pop('type')
        if type_.startswith('workflow_'):
            action = json_to_action(type_, message)
            if action:
                self.application.apply_action(action)
        else:
            logger.error("Got invalid message %r", type_)

    def on_close(self):
        self.application.remove_socket(self)
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
