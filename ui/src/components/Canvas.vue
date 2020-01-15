<template>
  <div>
    <div class="canvas">
      <Step v-for="(step, name) in steps" :key="name" :step="step" :name="name"/>
    </div>
    <svg class="canvas">
      <StepSvg
        v-for="(step, name) in steps" :key="name"
        :step="step"
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
import StepSvg from './StepSvg.vue'
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
              let source_step = this.steps[source.step];
              let sx = source_step.position[0] + 212;
              let sy = source_step.position[1] + 55;
              sy += step_output_index[source.step][source.output] * 32;

              // Compute position of destination input port
              let dx = step.position[0];
              let dy = step.position[1] + 55;
              dy += step_output_count[step_id] * 32;
              dy += step_input_index[step_id][input_name] * 32;

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
    outputY: function(step, idx) {
      return step.position[1] + 48 + 25 * idx;
    },
    inputY: function(step, idx) {
      return step.position[1] + 48 + 25 * step.outputs.length + 25 * idx;
    },
  },
  components: {
    Step,
    StepSvg,
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
