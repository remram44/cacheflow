import React from 'react';
import './Canvas.css';
import * as workflow from '../workflow';
import { sortByKey } from '../utils';
import { Step } from './Step';
import { Port } from './Port';
import { Connection } from './Connection';

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
  ports: Map<string, [workflow.PortType, [number, number]]>;
}

interface ConnectionSpec {
  key: string;
  sourceStepId: string;
  sourceOutputName: string;
  destStepId: string;
  destInputName: string;
  source: [number, number];
  dest: [number, number];
}

export class Canvas extends React.PureComponent<CanvasProps, CanvasState> {
  constructor(props: CanvasProps) {
    super(props);

    this.state = { ports: new Map() };

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
    console.log(`setPort(${stepId}, ${type}, ${name})`);
    const key = `${stepId}.${type}.${name}`;
    const prevEntry = this.state.ports.get(key);
    const prevPosition = prevEntry && prevEntry[1];
    if (!position && !prevPosition) {
      return;
    }
    if (
      position &&
      prevPosition &&
      (position[0] === prevPosition[0] || position[1] === prevPosition[1])
    ) {
      return;
    }
    this.setState(prevState => {
      const ports = new Map(prevState.ports);
      ports.set(key, [type, position]);
      return { ports };
    });
  }

  moveStep() {}

  removeStep() {}

  setInputParameter() {}

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
    const connections: Array<ConnectionSpec> = [];
    this.props.workflow.steps.forEach(step => {
      step.inputs.forEach((inputArray, inputName) => {
        inputArray.forEach(input => {
          if (input.type === 'connection') {
            console.log('CONNECTION!');
            // Get position of source output port
            const skey = `${input.step_id}.output.${input.output_name}`;
            const spos = this.state.ports.get(skey);
            if (!spos) {
              console.log('missing ', skey);
              return;
            }

            // Get position of destination input port
            const dkey = `${step.id}.input.${inputName}`;
            const dpos = this.state.ports.get(dkey);
            if (!dpos) {
              console.log('missing ', dkey);
              return;
            }

            // Add connection to array
            connections.push({
              key: `${skey}.${dkey}`,
              sourceStepId: input.step_id,
              sourceOutputName: input.output_name,
              destStepId: step.id,
              destInputName: inputName,
              source: spos[1],
              dest: dpos[1],
            });
          }
        });
      });
    });
    console.log('Connections: ', connections);
    return connections;
  }

  renderSteps() {
    const steps: JSX.Element[] = [];
    this.props.workflow.steps.forEach(step => {
      steps.push(
        <Step
          key={step.id}
          step={step}
          setPort={(
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
    this.state.ports.forEach(([type, position], key) => {
      ports.push(<Port key={key} type={type} position={position} />);
    });
    return ports;
  }

  renderConnections() {
    const connectionsList = this.computeConnections();
    const connections: JSX.Element[] = [];
    connectionsList.forEach(connection => {
      connections.push(
        <Connection
          key={connection.key}
          source={connection.source}
          dest={connection.dest}
        />
      );
    });
    return connections;
  }

  render() {
    return (
      <>
        <div className="canvas">{this.renderSteps()}</div>
        <svg className="canvas ports">{this.renderPorts()}</svg>
        <svg className="canvas connections">{this.renderConnections()}</svg>
      </>
    );
  }
}
