// Calculator State Interface
export interface CalculatorState {
  currentValue: string;
  previousValue: string | null;
  operation: string | null;
  waitingForOperand: boolean;
  memory: number;
  error: string | null;
}

// Button Types
export type ButtonType = 'number' | 'operation' | 'function' | 'equals';

// Button Configuration Interface
export interface ButtonConfig {
  label: string;
  value: string;
  type: ButtonType;
  className?: string;
  ariaLabel?: string;
}

// Calculator Action Types for Reducer
export type CalculatorActionType =
  | 'INPUT_NUMBER'
  | 'INPUT_DECIMAL'
  | 'PERFORM_OPERATION'
  | 'CALCULATE'
  | 'CLEAR'
  | 'CLEAR_ENTRY'
  | 'MEMORY_STORE'
  | 'MEMORY_RECALL'
  | 'MEMORY_CLEAR'
  | 'SET_ERROR';

// Calculator Action Interface
export interface CalculatorAction {
  type: CalculatorActionType;
  payload?: string | number;
}

// Display Component Props
export interface DisplayProps {
  value: string;
  error?: string;
  hasMemory: boolean;
}

// Button Component Props
export interface ButtonProps {
  label: string;
  type: ButtonType;
  onClick: (value: string) => void;
  className?: string;
  disabled?: boolean;
  ariaLabel?: string;
}

// ButtonGrid Component Props
export interface ButtonGridProps {
  onButtonClick: (value: string, type: ButtonType) => void;
  disabled?: boolean;
}

// Calculator Operations
export type Operation = '+' | '-' | '*' | '/' | '=';

// Keyboard Key Mapping
export interface KeyMapping {
  [key: string]: {
    value: string;
    type: ButtonType;
  };
}

// Error Types
export type CalculatorError = 
  | 'DIVISION_BY_ZERO'
  | 'INVALID_OPERATION'
  | 'OVERFLOW'
  | 'INVALID_INPUT';

// Theme Interface (for future enhancement)
export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
    error: string;
  };
  fonts: {
    display: string;
    button: string;
  };
}