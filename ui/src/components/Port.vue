<template>
  <circle
    :cx="port.position[0]" :cy="port.position[1]"
    :class="port.type"
    v-on:mousedown.left.self.prevent="mousedown"
    />
</template>

<script>
export default {
  name: 'Port',
  props: ['port'],
  methods: {
    mousedown: function() {
      if(this.port.type == 'output') {
        this.$emit('startconnection', this.port.name);
      } else {
        this.$emit('grabconnection', this.port.name);
      }
    },
  },
}
</script>

<style scoped>
circle.output {
  r: 6px;
  stroke: black;
  fill: grey;
  pointer-events: auto;
}

circle.input {
  r: 6px;
  stroke: black;
  fill: yellow;
  pointer-events: auto;
}
</style>
