<template>
  <div
    class="step" :style=style
    v-on:mousedown.left.self.prevent="mousedown"
    >
    <a class="close" v-on:click.self.prevent="remove">[x]</a>
    <h2>{{step.component.type}}</h2>
    <table class="outputs">
      <tr v-for="output of step.outputs" :key="output">
        <td>???</td>
        <td>{{output}}</td>
      </tr>
    </table>
    <table class="inputs">
      <tr v-for="input of inputs" :key="input[0]">
        <td>{{input[0]}}</td>
        <td>
          <input
            type="text" v-if="input[1] !== null"
            :value="input[1]"
            v-on:change="changeInput(input[0], $event)"
            />
        </td>
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
    sendUpdate: function() {
      // Send output port information
      let output_rows = this.$el.querySelectorAll(".outputs tr");
      for(let i = 0; i < output_rows.length; ++i) {
        let rect = output_rows[i].getBoundingClientRect();
        this.$emit(
          'setport',
          {
            name: `${this.name}.out.${this.step.outputs[i]}`,
            type: 'output',
            step: this.name, port_name: this.step.outputs[i],
            position: [rect.right + 6, (rect.top + rect.bottom) / 2],
          },
        );
      }

      // Send input port information
      let input_rows = this.$el.querySelectorAll(".inputs tr");
      for(let i = 0; i < input_rows.length; ++i) {
        let rect = input_rows[i].getBoundingClientRect();
        this.$emit(
          'setport',
          {
            name: `${this.name}.in.${this.inputs[i][0]}`,
            type: 'input',
            step: this.name, port_name: this.inputs[i][0],
            position: [rect.left - 6, (rect.top + rect.bottom) / 2],
          },
        );
      }
    },
    changeInput: function(input_name, event) {
      // TODO: Notify of input change
      console.log("Step ", this.name, " input ", input_name, " changed to ", event.target.value);
    },
    mousedown: function(event) {
      document.addEventListener('mouseup', this.mouseup);
      document.addEventListener('mousemove', this.mousemove);
      this.offset = [
        this.step.position[0] - event.clientX,
        this.step.position[1] - event.clientY,
      ];
    },
    mouseup: function() {
      document.removeEventListener('mouseup', this.mouseup);
      document.removeEventListener('mousemove', this.mousemove);
      this.$emit('stepmove', {name: this.name, position: this.step.position});
    },
    mousemove: function(event) {
      event.preventDefault();
      this.step.position = [
        event.clientX + this.offset[0],
        event.clientY + this.offset[1],
      ];
    },
    remove: function() {
      this.$emit("remove");
    },
  },
  mounted: function() {
    this.$nextTick(this.sendUpdate);
  },
  updated: function() {
    this.$nextTick(this.sendUpdate);
  },
  beforeDestroy: function() {
    // Remove event listeners
    document.removeEventListener('mousemove', this.mousemoved);
    document.removeEventListener('mouseup', this.mouseup);

    // Destroy output ports
    for(let output of this.step.outputs) {
      this.$emit(
        'setport',
        {
          name: `${this.name}.out.${output}`,
          position: undefined,
        },
      );
    }

    // Destroy input ports
    for(let input of this.inputs) {
      this.$emit(
        'setport',
        {
          name: `${this.name}.in.${input[0]}`,
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
  border: 2px solid black;
  border-radius: 15px;
  padding: 6px;
  z-index: 10;
  background-color: white;
}

.step * {
  pointer-events: none;
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
  pointer-events: auto;
}

.step table.inputs {
  margin-right: auto;
  padding: 0;
  border-collapse: collapse;
}

.step table.inputs tr, .step table.inputs td {
  padding: 0 2px 0 2px;
}

.step table.outputs {
  margin-left: auto;
  padding: 0;
  border-collapse: collapse;
}

.step table.outputs tr, .step table.outputs td {
  padding: 0 2px 0 2px;
}

a.close {
  position: absolute;
  right: 6px;
  top: 6px;
  pointer-events: auto;
}
</style>
