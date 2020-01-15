<template>
  <div>
    <div class="canvas">
      <Step
        v-for="(step, name) in steps" :key="name"
        :step="step" :name="name"
        v-on:portposition="setPortPosition"
        />
    </div>
    <svg class="canvas">
      <Port
        v-for="(port, name) in this.portPositions" :key="name"
        :position="port"
        />
      <Connection
        v-for="connection of connections" :key="connection.key"
        :connection="connection.data"
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
  data: function() {
    return {
      steps: {
        dataset: {
          component: {
            type: "dataset"
          },
          position: [100, 100],
          inputs: {
            name: ["age.csv"],
          },
          outputs: ["table"],
        },
        plot: {
          component: {
            type: "plot"
          },
          position: [350, 150],
          inputs: {
            table: [{step: "dataset", output: "table"}],
            x: ["name"],
            y: ["age"],
            style: [],
          },
          outputs: ["plot"],
        },
      },
      portPositions: {},
    };
  },
  computed: {
    connections: function() {
      // Pre-compute port information
      let step_output_index = {};
      let step_output_count = {};
      let step_input_index = {};
      for(let step_id in this.steps) {
        let step = this.steps[step_id];

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
      for(let step_id in this.steps) {
        let step = this.steps[step_id];
        for(let input_name in step.inputs) {
          let input_array = step.inputs[input_name];
          for(let source of input_array) {
            if(!(typeof source == "string")) {
              // Compute position of source output port
              let sx = 0, sy = 0;
              let skey = `${source.step}.out.${source.output}`;
              if(skey in this.portPositions) {
                [sx, sy] = this.portPositions[skey];
              }

              // Compute position of destination input port
              let dx = 0, dy = 0;
              let dkey = `${step_id}.in.${input_name}`;
              if(dkey in this.portPositions) {
                [dx, dy] = this.portPositions[dkey];
              }

              // Add connection to array
              connections.push({
                key: `${step_id}.${input_name}.${source.step}.${source.output}`,
                data: `M ${sx} ${sy} C ${sx + 40} ${sy} ${dx - 40} ${dy} ${dx} ${dy}`,
              });
            }
          }
        }
      }
      return connections;
    },
  },
  methods: {
    setPortPosition: function(evt) {
      let {port, position} = evt;
      if(position !== undefined) {
        this.$set(this.portPositions, port, position);
      } else {
        this.$delete(this.portPositions, port);
      }
    },
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
}

svg.canvas {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
}

svg.canvas g {
  pointer-events: auto;
}
</style>
