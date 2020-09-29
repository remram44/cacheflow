import React from 'react';
import './Port.css';
import * as workflow from '../workflow';

interface PortProps {
  type: workflow.PortType;
  position: [number, number];
}

export class Port extends React.PureComponent<PortProps> {
  render() {
    return (
      <circle
        className={this.props.type}
        cx={this.props.position[0]}
        cy={this.props.position[1]}
      />
    );
  }
}
