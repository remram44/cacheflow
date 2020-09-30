import React from 'react';
import './Canvas.css';
import * as workflow from '../workflow';
import { sortByKey } from '../utils';
import { Step } from './Step';
import { Port } from './Port';
import { Connection } from './Connection';

interface CanvasProps {
  workflow: workflow.Workflow;

  onStepRemove: (stepId: string) => void;
  onStepMove: (stepId: string, position: [number, number]) => void;
  onSetInputParameter: (
    stepId: string,
    inputName: string,
    value: string
  ) => void;
  onSetConnection: (
    fromStepId: string,
    fromOutputName: string,
    toStepId: string,
    toInputName: string
  ) => void;
  onRemoveConnection: (
    fromStepId: string,
    fromOutputName: string,
    toStepId: string,
    toInputName: string
  ) => void;
}

interface CanvasState {
  // Port positions reported from Step, used to position Port and Connection
  ports: Map<string, PortSpec>;
}

interface PortSpec {
  stepId: string;
  name: string;
  type: workflow.PortType;
  position: [number, number];
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
    this.grabPort = this.grabPort.bind(this);
  }

  setPort(portSpec: PortSpec) {
    const key = `${portSpec.stepId}.${portSpec.type}.${portSpec.name}`;
    const prevPort = this.state.ports.get(key);
    if (!portSpec && !prevPort) {
      return;
    }
    if (
      portSpec &&
      prevPort &&
      (portSpec.position[0] === prevPort.position[0] ||
        portSpec.position[1] === prevPort.position[1])
    ) {
      return;
    }
    this.setState(prevState => {
      const ports = new Map(prevState.ports);
      ports.set(key, portSpec);
      return { ports };
    });
  }

  unsetPort(stepId: string, type: workflow.PortType, name: string) {
    const key = `${stepId}.${type}.${name}`;
    this.setState(prevState => {
      const ports = new Map(prevState.ports);
      ports.delete(key);
      return { ports };
    });
  }

  grabPort(portSpec: PortSpec) {
    // TODO: Create or replace connection
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
    const connections: ConnectionSpec[] = [];
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
              sourceStepId: input.step_id,
              sourceOutputName: input.output_name,
              destStepId: step.id,
              destInputName: inputName,
              source: spos.position,
              dest: dpos.position,
            });
          }
        });
      });
    });
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
          ) => this.setPort({ stepId: step.id, type, name, position })}
          unsetPort={(type: workflow.PortType, name: string) =>
            this.unsetPort(step.id, type, name)
          }
          onMove={(position: [number, number]) =>
            this.props.onStepMove(step.id, position)
          }
          onRemove={() => this.props.onStepRemove(step.id)}
          onSetInputParameter={(name: string, value: string) =>
            this.props.onSetInputParameter(step.id, name, value)
          }
        />
      );
    });
    return steps;
  }

  renderPorts() {
    const ports: JSX.Element[] = [];
    this.state.ports.forEach((portSpec, key) => {
      ports.push(
        <Port
          key={key}
          type={portSpec.type}
          position={portSpec.position}
          onGrab={() => this.grabPort(portSpec)}
        />
      );
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
