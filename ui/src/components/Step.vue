<template>
  <div class="step" :style=style>
    <h2>{{name}}</h2>
    <table class="outputs">
      <tr v-for="output of step.outputs" :key="output">
        <td>???</td>
        <td>{{output}}</td>
      </tr>
    </table>
    <table class="inputs">
      <tr v-for="input of inputs" :key="input[0]">
        <td>{{input[0]}}</td>
        <td><input type="text" v-if="input[1] !== null" :value="input[1]"/></td>
      </tr>
    </table>
  </div>
</template>

<script>
import { sortByKey } from '../utils.js'

export default {
  name: 'Step',
  props: ['name', 'step'],
  computed: {
    inputs: function() {
      let entries = Object.entries(this.step.inputs);
      sortByKey(entries, function(o) { return o[0]; });
      for(let i = 0; i < entries.length; ++i) {
        if(entries[i][1].length == 0) {
          entries[i][1] = "";
        } else if(typeof entries[i][1][0] != "string") {
          entries[i][1] = null;
        }
      }
      return entries;
    },
    style: function() {
      return `left: ${this.step.position[0]}px; top: ${this.step.position[1]}px;`;
    },
  },
  methods: {
    updatePortPositions: function() {
      let output_rows = this.$el.querySelectorAll(".outputs tr");
      for(let i = 0; i < output_rows.length; ++i) {
        let rect = output_rows[i].getBoundingClientRect();
        this.$emit(
          'portposition',
          {
            port: `${this.name}.out.${this.step.outputs[i]}`,
            position: [rect.right + 6, (rect.top + rect.bottom) / 2],
          },
        );
      }

      let input_rows = this.$el.querySelectorAll(".inputs tr");
      for(let i = 0; i < input_rows.length; ++i) {
        let rect = input_rows[i].getBoundingClientRect();
        this.$emit(
          'portposition',
          {
            port: `${this.name}.in.${this.inputs[i][0]}`,
            position: [rect.left - 6, (rect.top + rect.bottom) / 2],
          },
        );
      }
    },
  },
  mounted: function() {
    this.$nextTick(this.updatePortPositions);
  },
  updated: function() {
    this.$nextTick(this.updatePortPositions);
  },
  beforeDestroy: function() {
    for(let output of this.step.outputs) {
      this.$emit(
        'portposition',
        {
          port: `${this.name}.out.${output}`,
          position: undefined,
        },
      );
    }

    for(let input of this.inputs) {
      this.$emit(
        'portposition',
        {
          port: `${this.name}.in.${input[0]}`,
          position: undefined,
        },
      );
    }
  },
}
</script>

<style scoped>
.step {
  position: absolute;
  width: 200px;
  border: 1px solid black;
  padding: 6px;
  z-index: 15;
}

.step h2 {
  text-align: center;
  margin: 0;
  height: 32px;
}

.step td {
  font-size: 0.85rem;
}

.step input {
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
}

.step table.inputs {
  margin-right: auto;
  padding: 0;
}

.step table.inputs tr, .step table.inputs td {
  padding: 0 2px 0 2px;
}

.step table.outputs {
  margin-left: auto;
  padding: 0;
}

.step table.outputs tr, .step table.outputs td {
  padding: 0 2px 0 2px;
}
</style>
