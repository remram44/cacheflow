import React from 'react';
import { Workflow } from './workflow';
import { Canvas } from './components/Canvas';

interface AppState {
  workflow: Workflow;
}

export class App extends React.PureComponent<{}, AppState> {
  constructor(props: {}) {
    super(props);
    const workflow = {
      meta: {},
      steps: new Map(),
    };
    this.state = { workflow };

    this.addStep = this.addStep.bind(this);
    this.removeStep = this.removeStep.bind(this);
    this.moveStep = this.moveStep.bind(this);
    this.setInputParameter = this.setInputParameter.bind(this);
    this.setConnection = this.setConnection.bind(this);
    this.removeConnection = this.removeConnection.bind(this);
  }

  addStep() {}

  removeStep() {}

  moveStep() {}

  setInputParameter() {}

  setConnection() {}

  removeConnection() {}

  render() {
    return (
      <div id="app">
        <Canvas
          workflow={this.state.workflow}
          onStepAdd={this.addStep}
          onStepRemove={this.removeStep}
          onStepMove={this.moveStep}
          onSetInputParameter={this.setInputParameter}
          onSetConnection={this.setConnection}
          onRemoveConnection={this.removeConnection}
        />
      </div>
    );
  }
}
