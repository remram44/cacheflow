import React from 'react';
import './Port.css';
import * as workflow from '../workflow';

interface PortProps {
  type: workflow.PortType;
  position: [number, number];
  onGrab: () => void;
}

export class Port extends React.PureComponent<PortProps> {
  constructor(props: PortProps) {
    super(props);

    this.onMouseDown = this.onMouseDown.bind(this);
  }

  onMouseDown(e: React.MouseEvent) {
    // Left button only
    if (e.button !== 0) {
      return;
    }
    e.preventDefault();

    this.props.onGrab();
  }

  render() {
    return (
      <circle
        className={this.props.type}
        cx={this.props.position[0]}
        cy={this.props.position[1]}
        onMouseDown={this.onMouseDown}
      />
    );
  }
}
