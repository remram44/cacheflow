import React from 'react';
import * as workflow from './workflow';
import { Canvas } from './components/Canvas';
import { randomString } from './utils';

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

  addStep(component: workflow.ComponentDef) {
    const id = randomString(8);
    const step: workflow.Step = {
      id,
      component,
      inputs: new Map(),
      outputs: [],
      position: [100, 100],
    };
    this.setState(({ workflow: wf }) => {
      const steps = new Map(wf.steps);
      steps.set(step.id, step);
      return { workflow: { ...wf, steps } };
    });
  }

  removeStep(stepId: string) {
    this.setState(({ workflow: wf }) => {
      const steps = new Map(wf.steps);
      steps.delete(stepId);
      return { workflow: { ...wf, steps } };
    });
  }

  moveStep(stepId: string, position: [number, number]) {
    this.setState(({ workflow: wf }) => {
      const step = wf.steps.get(stepId);
      if (step) {
        const steps = new Map(wf.steps);
        steps.set(stepId, {
          ...step,
          position,
        });
        wf = { ...wf, steps };
      }
      return { workflow: wf };
    });
  }

  setInputParameter(stepId: string, inputName: string, value: string) {
    this.setState(({ workflow: wf }) => {
      const step = wf.steps.get(stepId);
      if (step) {
        const inputs = new Map(step.inputs);
        inputs.set(inputName, [{ type: 'constant', value }]);
        const steps = new Map(wf.steps);
        steps.set(stepId, {
          ...step,
          inputs,
        });
        wf = { ...wf, steps };
      }
      return { workflow: wf };
    });
  }

  setConnection(
    fromStepId: string,
    fromOutputName: string,
    toStepId: string,
    toInputName: string
  ) {
    this.setState(({ workflow: wf }) => {
      const step = wf.steps.get(toStepId);
      if (step) {
        const inputs = new Map(step.inputs);
        const connection: workflow.StepInputConnection = {
          type: 'connection',
          step_id: fromStepId,
          output_name: fromOutputName,
        };
        const prevInputs = inputs.get(toInputName) || [];
        inputs.set(toInputName, [...prevInputs, connection]);
        const steps = new Map(wf.steps);
        steps.set(toStepId, {
          ...step,
          inputs,
        });
        wf = { ...wf, steps };
      }
      return { workflow: wf };
    });
  }

  removeConnection(
    fromStepId: string,
    fromOutputName: string,
    toStepId: string,
    toInputName: string
  ) {
    this.setState(({ workflow: wf }) => {
      const step = wf.steps.get(toStepId);
      if (step) {
        const inputs = new Map(step.inputs);
        const portInputs = step.inputs.get(toInputName) || [];
        inputs.set(
          toInputName,
          portInputs.filter(input => {
            if (input.type === 'connection') {
              const { step_id, output_name } = input;
              if (step_id === fromStepId && output_name === fromOutputName) {
                return false;
              }
            }
            return true;
          })
        );
      }
    });
  }

  render() {
    return (
      <div id="app">
        <Canvas
          workflow={this.state.workflow}
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
