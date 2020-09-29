import React from 'react';
import './Canvas.css';
import * as workflow from '../workflow';
import { sortByKey } from '../utils';
import { Step } from './Step';

interface CanvasProps {
  workflow: workflow.Workflow;

  onStepAdd: () => void;
  onStepRemove: () => void;
  onStepMove: () => void;
  onSetInputParameter: () => void;
  onSetConnection: () => void;
  onRemoveConnection: () => void;
}

interface CanvasState {
  // Port positions reported from Step, used to position Port and Connection
  ports: Map<string, [number, number]>;
}

export class Canvas extends React.PureComponent<CanvasProps, CanvasState> {
  constructor(props: CanvasProps) {
    super(props);

    this.setPort = this.setPort.bind(this);
    this.moveStep = this.moveStep.bind(this);
    this.removeStep = this.removeStep.bind(this);
    this.setInputParameter = this.setInputParameter.bind(this);
  }

  setPort(
    stepId: string,
    type: workflow.PortType,
    name: string,
    position: [number, number]
  ) {
    this.setState(prevState => {
      const ports = new Map(prevState.ports);
      ports.set(`${stepId}.${type}.${name}`, position);
      return { ports, ...prevState };
    });
  }

  moveStep() {}

  removeStep() {}

  setInputParameter() {}

  renderSteps() {
    const steps: JSX.Element[] = [];
    this.props.workflow.steps.forEach(step => {
      steps.push(
        <Step
          key={step.id}
          step={step}
          onSetPort={(
            type: workflow.PortType,
            name: string,
            position: [number, number]
          ) => this.setPort(step.id, type, name, position)}
          onMove={this.moveStep}
          onRemove={this.removeStep}
          onSetInputParameter={this.setInputParameter}
        />
      );
    });
    return steps;
  }

  renderPorts() {
    const ports: JSX.Element[] = [];
    /*this.getPorts().forEach((port) => {
      ports.push(
        <Port
          key={port.key}
        />
      );
    });*/
    return ports;
  }

  renderConnections() {
    const connections: JSX.Element[] = [];
    /*this.getConnections().forEach((connection) => {
      connections.push(<></>);
    });*/
    return connections;
  }

  computeConnections() {
    // Pre-compute port information
    const stepOutputIndex: Map<string, Map<string, number>> = new Map();
    const stepInputIndex: Map<string, Map<string, number>> = new Map();
    this.props.workflow.steps.forEach(step => {
      // Index outputs
      {
        let count = 0;
        const outputIndexes = new Map();
        for (const output of step.outputs) {
          outputIndexes.set(output, count++);
        }
        stepOutputIndex.set(step.id, outputIndexes);
      }

      // Index inputs
      {
        let count = 0;
        const inputs = Object.entries(step.inputs);
        sortByKey(inputs, o => o[0]);
        const inputIndexes = new Map();
        for (const [inputName] of inputs) {
          inputIndexes.set(inputName, count++);
        }
        stepInputIndex.set(step.id, inputIndexes);
      }
    });

    // For each step, for each of its input, for each of its connection
    const connections: Array<{}> = [];
    this.props.workflow.steps.forEach(step => {
      step.inputs.forEach((inputArray, inputName) => {
        inputArray.forEach(input => {
          if (input.type === 'connection') {
            // Get position of source output port
            const skey = `${input.step_id}.output.${input.output_name}`;
            const spos = this.state.ports.get(skey);
            if (!spos) {
              return;
            }

            // Get position of destination input port
            const dkey = `${step.id}.input.${inputName}`;
            const dpos = this.state.ports.get(dkey);
            if (!dpos) {
              return;
            }

            // Add connection to array
            connections.push({
              key: `${skey}.${dkey}`,
              source_step_id: input.step_id,
              source_output_name: input.output_name,
              dest_step_id: step.id,
              dest_input_name: inputName,
              source: spos,
              dest: dpos,
            });
          }
        });
      });
    });
    return connections;
  }

  render() {
    const connections = this.computeConnections();
    return (
      <>
        <div className="canvas">{this.renderSteps()}</div>
        <svg className="canvas ports">{this.renderPorts()}</svg>
        <svg className="canvas connections">{this.renderConnections()}</svg>
      </>
    );
  }
}
