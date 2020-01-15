<template>
  <g>
    <!-- Output ports -->
    <circle
      v-for="(output, idx) of step.outputs" :key="output"
      :cx="step.position[0] + 212"
      :cy="outputY(idx)"
      class="output"
      />

    <!-- Input ports -->
    <circle
      v-for="(input, idx) of inputs" :key="input[0]"
      :cx="step.position[0]"
      :cy="inputY(idx)"
      class="input"
      />
  </g>
</template>

<script>
import { sortByKey } from '../utils.js'

export default {
  props: ['step'],
  computed: {
    inputs: function() {
      let entries = Object.entries(this.step.inputs);
      sortByKey(entries, function(o) { return o[0]; });
      return entries;
    },
  },
  methods: {
    outputY: function(idx) {
      return this.step.position[1] + 55 + 32 * idx;
    },
    inputY: function(idx) {
      return this.step.position[1] + 55 + 32 * this.step.outputs.length + 32 * idx;
    },
  },
}
</script>

<style scoped>
circle.output {
  r: 6px;
  stroke: black;
  fill: yellow;
}

circle.input {
  r: 6px;
  stroke: black;
  fill: yellow;
}
</style>
