<template>
  <div class="library">
    <div>
      <div>
        <h1>Workflow library</h1>
        <p v-for="component in components" :key="component.component.type">
          <button v-on:click="add(component)">{{ component.name }}</button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Library',
  data: function() {
    return {
      components: [
        {
          name: "download",
          component: {type: "download"},
          inputs: ["url", "headers"],
          outputs: ["file"],
        },
        {
          name: "python",
          component: {type: "script.python"},
          inputs: ["env"],
          outputs: ["env", "streams"],
        },
      ],
    };
  },
  methods: {
    add: function(component) {
      this.$emit('add', component);
    },
  },
}
</script>

<style scoped>
.library {
  position: absolute;
  display: table;
  height: 100%;
  right: 10px;
  top: 0;
  bottom: 0;
  z-index: 15;
}

.library>div {
  display: table-cell;
  vertical-align: middle;
}

.library>div>div {
  border: 1px solid #aaa;
  padding: 5px;
  background-color: white;
}

.library h1 {
  font-size: 1.8rem;
}

.library p {
  text-align: center;
}
</style>
