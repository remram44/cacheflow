<template>
  <div>
    <div class="canvas">
      <Step
        v-for="step in workflow.steps" :key="step.id"
        :step="step"
        v-on:setport="setPort"
        v-on:stepmove="moveStep"
        v-on:remove="removeStep(step.id)"
        v-on:setinputparameter="setInputParameter"
        />
    </div>
    <svg class="canvas ports">
      <Port
        v-for="port in this.ports" :key="port.key"
        :port="port"
        v-on:startconnection="startConnection"
        v-on:grabconnection="grabConnection"
        />
    </svg>
    <svg class="canvas connections">
      <Connection
        v-for="connection of connections" :key="connection.key"
        :source="connection.source" :dest="connection.dest"
        />
      <Connection
        v-if="newConnection != null"
        :source="newConnection.source" :dest="newConnection.dest"
        />
    </svg>
  </div>
</template>

<script>
import Step from './Step.vue'
import Port from './Port.vue'
import Connection from './Connection.vue'
import { sortByKey } from '../utils.js'

export default {
  name: 'Canvas',
  props: ['workflow'],
  data: function() {
    return {
      ports: {},
      newConnection: null,
    };
  },
  computed: {
    connections: function() {
      // Pre-compute port information
      let step_output_index = {};
      let step_output_count = {};
      let step_input_index = {};
      for(let step_id in this.workflow.steps) {
        let step = this.workflow.steps[step_id];

        // Index outputs
        {
          let count = 0;
          step_output_index[step_id] = {};
          for(let output of step.outputs) {
            step_output_index[step_id][output] = count++;
          }
          step_output_count[step_id] = count;
        }

        // Index inputs
        {
          let count = 0;
          step_input_index[step_id] = {};
          let inputs = Object.entries(step.inputs);
          sortByKey(inputs, function(o) { return o[0]; });
          for(let [input_name,] of inputs) {
            step_input_index[step_id][input_name] = count++;
          }
        }
      }

      // For each step, for each of its input, for each of its connection
      let connections = [];
      for(let step_id in this.workflow.steps) {
        let step = this.workflow.steps[step_id];
        for(let input_name in step.inputs) {
          let input_array = step.inputs[input_name];
          for(let source of input_array) {
            if(!(typeof source == "string")) {
              // Get position of source output port
              let skey = `${source.step_id}.out.${source.output_name}`;
              if(!(skey in this.ports)) {
                continue;
              }
              let spos = this.ports[skey].position;

              // Get position of destination input port
              let dkey = `${step_id}.in.${input_name}`;
              if(!(dkey in this.ports)) {
                continue;
              }
              let dpos = this.ports[dkey].position;

              // Add connection to array
              connections.push({
                key: `${skey}.${dkey}`,
                source_step_id: source.step_id, source_output_name: source.output_name,
                dest_step_id: step_id, dest_input_name: input_name,
                source: spos, dest: dpos,
              });
            }
          }
        }
      }
      return connections;
    },
  },
  methods: {
    setPort: function(port) {
      if(port.position !== undefined) {
        this.$set(this.ports, port.key, port);
      } else {
        this.$delete(this.ports, port.key);
      }
    },
    moveStep: function(e) {
      this.$emit('stepmove', e);
    },
    removeStep: function(step_id) {
      this.$emit('stepremove', step_id);
    },
    setInputParameter: function(e) {
      this.$emit('setinputparameter', e);
    },
    startConnection: function(port_key) {
      let source_port = this.ports[port_key];
      this.newConnection = {
        key: `${port_key}.`,
        source_step_id: source_port.step_id,
        source_output_name: source_port.port_name,
        source: source_port.position,
        dest: [event.clientX, event.clientY],
      };
      document.addEventListener('mouseup', this.connectionMouseUp);
      document.addEventListener('mousemove', this.connectionMouseMove);
    },
    grabConnection: function(port_key) {
      let source_port = null;
      for(let conn of this.connections) {
        if(`${conn.dest_step_id}.in.${conn.dest_input_name}` == port_key) {
          // Delete that connection
          this.$emit(
            'removeconnection',
            {
              step_id: conn.dest_step_id,
              input_name: conn.dest_input_name,
              source_step_id: conn.source_step_id,
              source_output_name: conn.source_output_name,
            },
          );

          // Make new connection from source port
          source_port = `${conn.source_step_id}.out.${conn.source_output_name}`;

          break;
        }
      }
      if(source_port !== null) {
        this.startConnection(source_port);
      }
    },
    connectionMouseUp: function(event) {
      document.removeEventListener('mouseup', this.connectionMouseUp);
      document.removeEventListener('mousemove', this.connectionMouseMove);

      // Find closest port
      let min_port = null;
      let min_sqdist = 150;
      for(let port_key in this.ports) {
        let port = this.ports[port_key];
        if(port.type != 'input') {
          continue;
        }
        let dx = port.position[0] - event.clientX;
        let dy = port.position[1] - event.clientY;
        let sqdist = dx * dx + dy * dy;
        if(sqdist < min_sqdist) {
          min_sqdist = sqdist;
          min_port = port;
        }
      }

      if(min_port !== null) {
        this.$emit(
          'setconnection',
          {
            step_id: min_port.step_id,
            input_name: min_port.port_name,
            source_step_id: this.newConnection.source_step_id,
            source_output_name: this.newConnection.source_output_name,
          },
        );
      }

      this.newConnection = null
    },
    connectionMouseMove: function(event) {
      this.newConnection.dest = [event.clientX, event.clientY];
    },
  },
  beforeDestroy: function() {
    // Remove event listeners
    document.removeEventListener('mouseup', this.connectionMouseUp);
    document.removeEventListener('mousemove', this.connectionMouseMove);
  },
  components: {
    Step,
    Port,
    Connection,
  },
}
</script>

<style scoped>
div.canvas {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #eee;
}

svg.canvas {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
}

svg.ports {
  z-index: 14;
  pointer-events: none;
}

svg.connections {
  z-index: 5;
}
</style>
