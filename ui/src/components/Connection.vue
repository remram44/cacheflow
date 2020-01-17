<template>
  <path :d="path" class="connection"/>
</template>

<script>
export default {
  name: 'Connection',
  props: ['source', 'dest'],
  computed: {
    path: function() {
      let [sx, sy] = this.source;
      let [dx, dy] = this.dest;
      return `M ${sx} ${sy} C ${sx + 40} ${sy} ${dx - 40} ${dy} ${dx} ${dy}`;
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
