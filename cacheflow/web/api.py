import json
import logging
from tornado.websocket import WebSocketHandler

from ..storage.controller import WorkflowChangeObserver
from .json import workflow_to_json, json_to_actions, action_to_json


logger = logging.getLogger(__name__)


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

            # Execute the workflow
            if actions_array:
                self.application.execute_workflow()
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
