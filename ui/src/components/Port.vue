<template>
  <circle
    :cx="port.position[0]" :cy="port.position[1]"
    :class="port.type"
    />
</template>

<script>
export default {
  props: ['port'],
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
