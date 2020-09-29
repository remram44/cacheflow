import React from 'react';
import './Canvas.css';
import { Workflow } from '../workflow';
import { sortByKey } from '../utils';

function Step(props: {}) {
  return <></>;
}

interface CanvasProps {
  workflow: Workflow;

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

type PortType = 'input' | 'output';

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
    type: PortType,
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
            type: PortType,
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
