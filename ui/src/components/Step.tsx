import React from 'react';
import './Step.css';
import { sortByKey } from '../utils';
import * as workflow from '../workflow';

interface StepProps {
  step: workflow.Step;
  setPort: (
    type: workflow.PortType,
    name: string,
    position: [number, number]
  ) => void;
  onMove: () => void;
  onRemove: () => void;
  onSetInputParameter: () => void;
}

export class Step extends React.PureComponent<StepProps> {
  outputsRef: React.RefObject<HTMLTableElement>;
  inputsRef: React.RefObject<HTMLTableElement>;

  constructor(props: StepProps) {
    super(props);

    this.outputsRef = React.createRef();
    this.inputsRef = React.createRef();

    this.onMouseDown = this.onMouseDown.bind(this);
    this.remove = this.remove.bind(this);
  }

  onMouseDown(e: React.MouseEvent) {
    // Left button only
    if (e.button !== 0) {
      return;
    }
    e.preventDefault();

    // TODO: Drag step
  }

  remove() {
    // TODO: Delete step
  }

  changeInput(name: string, e: React.ChangeEvent) {}

  componentDidMount() {
    this.sendPortLocations();
  }

  componentDidUpdate() {
    //this.sendPortLocations();
  }

  sendPortLocations() {
    // Send output port information
    if (this.outputsRef.current) {
      const outputs = this.getOutputs();
      this.outputsRef.current
        .querySelectorAll('.outputs tr')
        .forEach((row, i) => {
          const rect = row.getBoundingClientRect();
          this.props.setPort('output', outputs[i], [
            rect.right + 6,
            (rect.top + rect.bottom) / 2,
          ]);
        });
    }

    // Send input port information
    if (this.inputsRef.current) {
      const inputs = this.getInputs();
      this.inputsRef.current
        .querySelectorAll('.inputs tr')
        .forEach((row, i) => {
          const rect = row.getBoundingClientRect();
          this.props.setPort('input', inputs[i][0], [
            rect.left - 6,
            (rect.top + rect.bottom) / 2,
          ]);
        });
    }
  }

  getOutputs() {
    const outputs = this.props.step.outputs.slice();
    outputs.sort();
    return outputs;
  }

  getInputs() {
    const inputEntries = Array.from(this.props.step.inputs.entries());
    const inputs: Array<[string, string | undefined]> = inputEntries.map(
      ([name, values]) => {
        if (values.length === 0) {
          return [name, ''];
        } else if (values[0].type !== 'constant') {
          return [name, undefined];
        } else {
          return [name, values[0].value];
        }
      }
    );
    sortByKey(inputs, o => o[0]);
    return inputs;
  }

  render() {
    const style = {
      left: this.props.step.position[0] + 'px',
      top: this.props.step.position[1] + 'px',
    };

    return (
      <div className="step" style={style} onMouseDown={this.onMouseDown}>
        <button className="close" onClick={this.remove}>
          [x]
        </button>
        <h2>{this.props.step.component.type}</h2>
        <table className="outputs" ref={this.outputsRef}>
          <tbody>
            {this.getOutputs().map(output => (
              <tr key={output}>
                <td>???</td>
                <td>{output}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <table className="inputs" ref={this.inputsRef}>
          <tbody>
            {this.getInputs().map(([name, value]) => (
              <tr key={name}>
                <td>{name}</td>
                <td>
                  <input
                    type="text"
                    v-if="input[1] !== null"
                    value={value}
                    onChange={event => this.changeInput(name, event)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
}
