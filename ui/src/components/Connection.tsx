import React from 'react';
import './Connection.css';

interface ConnectionProps {
  source: [number, number];
  dest: [number, number];
}

export class Connection extends React.PureComponent<ConnectionProps> {
  render() {
    const [sx, sy] = this.props.source;
    const [dx, dy] = this.props.dest;
    const path = `M ${sx} ${sy} C ${sx + 40} ${sy} ${dx - 40} ${dy} ${dx} ${dy}`;
    return (
      <path d={path} className="connection" />
    );
  }
}
