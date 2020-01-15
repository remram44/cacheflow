<template>
  <circle
    :cx="position[0]"
    :cy="position[1]"
    class="input"
    />
</template>

<script>
export default {
  props: ['position'],
}
</script>

<style scoped>
circle.output {
  r: 6px;
  stroke: black;
  fill: grey;
}

circle.input {
  r: 6px;
  stroke: black;
  fill: yellow;
}
</style>
