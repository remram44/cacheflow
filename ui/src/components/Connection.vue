<template>
  <path :d="path" class="connection"/>
</template>

<script>
export default {
  props: ['connection'],
  computed: {
    path: function() {
      return this.connection; // TODO: Build path from data
    },
  },
}
</script>

<style scoped>
path.connection {
  stroke: black;
  fill: none;
  z-index: 10;
}
</style>
