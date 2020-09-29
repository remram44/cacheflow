import React from 'react';
import './Step.css';
import * as workflow from '../workflow';

interface StepProps {
  step: workflow.Step;
  onSetPort: (
    type: workflow.PortType,
    name: string,
    position: [number, number]
  ) => void;
  onMove: () => void;
  onRemove: () => void;
  onSetInputParameter: () => void;
}

export class Step extends React.PureComponent<StepProps> {
  render() {
    // TODO: Step box
    return <></>;
  }
}
