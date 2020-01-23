<template>
  <div id="app">
    <Canvas
      :workflow="workflow"
      v-on:stepremove="removeStep" v-on:stepmove="moveStep"
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
import { uuid4 } from './utils.js'

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
    // TODO: Send messages for those actions
    addStep: function(component) {
      let inputs = {};
      for(let input of component.inputs) {
        inputs[input] = [];
      }
      let name = uuid4();
      this.$set(
        this.workflow.steps, name,
        {
          component: component.component_def,
          position: [10, 10],
          inputs: inputs,
          outputs: component.outputs.slice(),
        },
      );
      console.log("Step ", name, " added");
    },
    removeStep: function(name) {
      this.websocket.send(JSON.stringify({
        type: 'workflow_remove_step',
        step_id: name,
      }));
    },
    moveStep: function(e) {
      let {name, position} = e;
      console.log("Step ", name, " moved to ", position);
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
      // TODO: Implement other actions
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
