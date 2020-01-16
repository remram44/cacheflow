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
  data: function() {
    return {
      components: [
        {
          name: "dataset",
          component: {type: "dataset"},
          inputs: ["name"],
          outputs: ["table"],
        },
        {
          name: "plot",
          component: {type: "plot"},
          inputs: ["style", "table", "x", "y"],
          outputs: ["plot"],
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
  border: 1px solid #ccc;
  padding: 5px;
}

.library p {
  text-align: center;
}
</style>
