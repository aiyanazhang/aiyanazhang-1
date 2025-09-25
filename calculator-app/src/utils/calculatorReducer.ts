import type { CalculatorState, CalculatorAction } from '../types/calculator';
import { calculate, handleDecimalInput, handleNumberInput, getErrorMessage } from './calculator';

// Initial state
export const initialState: CalculatorState = {
  currentValue: '0',
  previousValue: null,
  operation: null,
  waitingForOperand: false,
  memory: 0,
  error: null,
};

/**
 * Calculator reducer for state management
 */
export const calculatorReducer = (state: CalculatorState, action: CalculatorAction): CalculatorState => {
  switch (action.type) {
    case 'INPUT_NUMBER': {
      const digit = action.payload as string;
      
      if (state.waitingForOperand) {
        return {
          ...state,
          currentValue: digit,
          waitingForOperand: false,
          error: null,
        };
      }
      
      return {
        ...state,
        currentValue: handleNumberInput(state.currentValue, digit),
        error: null,
      };
    }
    
    case 'INPUT_DECIMAL': {
      if (state.waitingForOperand) {
        return {
          ...state,
          currentValue: '0.',
          waitingForOperand: false,
          error: null,
        };
      }
      
      return {
        ...state,
        currentValue: handleDecimalInput(state.currentValue),
        error: null,
      };
    }
    
    case 'PERFORM_OPERATION': {
      const nextOperation = action.payload as string;
      
      if (state.previousValue === null) {
        return {
          ...state,
          previousValue: state.currentValue,
          operation: nextOperation,
          waitingForOperand: true,
          error: null,
        };
      }
      
      if (state.operation && state.waitingForOperand) {
        return {
          ...state,
          operation: nextOperation,
          error: null,
        };
      }
      
      try {
        const result = calculate(state.previousValue, state.currentValue, state.operation as any);
        return {
          ...state,
          currentValue: result,
          previousValue: result,
          operation: nextOperation,
          waitingForOperand: true,
          error: null,
        };
      } catch (error) {
        return {
          ...state,
          error: getErrorMessage((error as Error).message as any),
        };
      }
    }
    
    case 'CALCULATE': {
      if (state.previousValue === null || state.operation === null) {
        return state;
      }
      
      try {
        const result = calculate(state.previousValue, state.currentValue, state.operation as any);
        return {
          ...state,
          currentValue: result,
          previousValue: null,
          operation: null,
          waitingForOperand: true,
          error: null,
        };
      } catch (error) {
        return {
          ...state,
          error: getErrorMessage((error as Error).message as any),
        };
      }
    }
    
    case 'CLEAR': {
      return {
        ...initialState,
        memory: state.memory, // Preserve memory
      };
    }
    
    case 'CLEAR_ENTRY': {
      return {
        ...state,
        currentValue: '0',
        error: null,
      };
    }
    
    case 'MEMORY_STORE': {
      const value = parseFloat(state.currentValue);
      return {
        ...state,
        memory: isNaN(value) ? state.memory : value,
        error: null,
      };
    }
    
    case 'MEMORY_RECALL': {
      return {
        ...state,
        currentValue: state.memory.toString(),
        waitingForOperand: false,
        error: null,
      };
    }
    
    case 'MEMORY_CLEAR': {
      return {
        ...state,
        memory: 0,
        error: null,
      };
    }
    
    case 'SET_ERROR': {
      return {
        ...state,
        error: action.payload as string,
      };
    }
    
    default:
      return state;
  }
};