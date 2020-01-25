<template>
  <div id="app">
    <Canvas
      :workflow="workflow"
      v-on:stepremove="removeStep" v-on:stepmove="moveStep"
      v-on:setinputparameter="setInputParameter"
      v-on:setconnection="setConnection"
      v-on:removeconnection="removeConnection"
      />

    <Library
      :components="components"
      v-on:add="addStep"
      />
  </div>
</template>

<script>
import Canvas from './components/Canvas.vue'
import Library from './components/Library.vue'

export default {
  name: 'App',
  data: function() {
    return {
      websocket: null,
      workflow: {
        steps: {},
      },
      components: [],
    };
  },
  methods: {
    addStep: function(component) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_add_step',
        component_def: component.component_def,
        position: [10, 10],
      }));
    },
    removeStep: function(step_id) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_remove_step',
        step_id,
      }));
    },
    moveStep: function(e) {
      let {step_id, position} = e;
      this.websocket.send(JSON.stringify({
        type: 'workflow_move_step',
        step_id,
        position: position,
      }));
    },
    setInputParameter: function(e) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_set_input_parameter',
        step_id: e.step_id,
        input_name: e.input_name,
        value: e.value,
      }));
    },
    setConnection: function(e) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_set_input_connection',
        step_id: e.step_id,
        input_name: e.input_name,
        source_step_id: e.source_step_id,
        source_output_name: e.source_output_name,
      }));
    },
    removeConnection: function(e) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_remove_inputs',
        step_id: e.step_id,
        input_name: e.input_name,
      }));
    },
  },
  created: function() {
    let url = window.API_WS_URL;
    if(url.substring(url.length - 1) != '/') {
      url += '/';
    }
    url += 'workflow';
    let self = this;
    this.websocket = new WebSocket(url);
    this.websocket.addEventListener('open', function() {
      console.log("Connected");
    });
    this.websocket.addEventListener('close', function() {
      console.error("Connection closed");
    });
    this.websocket.addEventListener('message', function(event) {
      let data = JSON.parse(event.data);
      if(data.type == 'workflow') {
        self.workflow = data.workflow;
      } else if(data.type == 'components_add') {
        for(let component of data.components) {
          self.components.push(component);
        }
      // TODO: Implement other incremental actions
      } else if(data.type == 'workflow_remove_step') {
        self.$delete(self.workflow.steps, data.step_id);
      } else {
        console.error("Unrecognized message from server: ", data);
      }
    });
  },
  components: {
    Canvas,
    Library,
  },
}
</script>

<style>
body {
  margin: 0;
}
</style>
