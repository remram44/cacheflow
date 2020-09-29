import React from 'react';
import * as workflow from './workflow';
import { Canvas } from './components/Canvas';

interface AppState {
  workflow: workflow.Workflow;
}

export class App extends React.PureComponent<{}, AppState> {
  constructor(props: {}) {
    super(props);
    const param: workflow.StepInputConstant = {
      type: 'constant',
      value: 'fast',
    };
    const conn: workflow.StepInputConnection = {
      type: 'connection',
      step_id: 'step1',
      output_name: 'data',
    };
    const wf: workflow.Workflow = {
      meta: {},
      steps: new Map([
        [
          'step1',
          {
            id: 'step1',
            component: { type: 'data' },
            inputs: new Map([['function', [param]]]),
            outputs: ['data'],
            position: [20, 50],
          },
        ],
        [
          'step2',
          {
            id: 'step2',
            component: { type: 'optimize' },
            inputs: new Map([['data', [conn]]]),
            outputs: [],
            position: [400, 50],
          },
        ],
      ]),
    };
    this.state = { workflow: wf };

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
