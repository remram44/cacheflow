export interface Workflow {
  meta: Meta;
  steps: Map<string, Step>;
}

export interface Meta {}

export interface Step {
  id: string;
  component: ComponentDef;
  inputs: Map<string, StepInput[]>;
  outputs: string[];
  position: [number, number];
}

export type PortType = 'input' | 'output';

export interface ComponentDef {
  type?: string;
}

export interface StepInputConnection {
  type: 'connection';
  step_id: string;
  output_name: string;
}

export interface StepInputConstant {
  type: 'constant';
  value: string;
}

export type StepInput = StepInputConnection | StepInputConstant;
