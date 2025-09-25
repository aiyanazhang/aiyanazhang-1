import { calculatorReducer, initialState } from '../calculatorReducer';
import type { CalculatorState } from '../../types/calculator';

describe('Calculator Reducer', () => {
  it('should return initial state', () => {
    expect(initialState).toEqual({
      currentValue: '0',
      previousValue: null,
      operation: null,
      waitingForOperand: false,
      memory: 0,
      error: null,
    });
  });

  describe('INPUT_NUMBER', () => {
    it('should input number when not waiting for operand', () => {
      const state = calculatorReducer(initialState, {
        type: 'INPUT_NUMBER',
        payload: '5'
      });
      expect(state.currentValue).toBe('5');
      expect(state.error).toBe(null);
    });

    it('should replace current value when waiting for operand', () => {
      const initialStateWaiting: CalculatorState = {
        ...initialState,
        waitingForOperand: true,
        currentValue: '10'
      };
      const state = calculatorReducer(initialStateWaiting, {
        type: 'INPUT_NUMBER',
        payload: '5'
      });
      expect(state.currentValue).toBe('5');
      expect(state.waitingForOperand).toBe(false);
    });

    it('should append digits to existing number', () => {
      const initialStateWithNumber: CalculatorState = {
        ...initialState,
        currentValue: '12'
      };
      const state = calculatorReducer(initialStateWithNumber, {
        type: 'INPUT_NUMBER',
        payload: '3'
      });
      expect(state.currentValue).toBe('123');
    });
  });

  describe('INPUT_DECIMAL', () => {
    it('should add decimal point to current number', () => {
      const initialStateWithNumber: CalculatorState = {
        ...initialState,
        currentValue: '12'
      };
      const state = calculatorReducer(initialStateWithNumber, {
        type: 'INPUT_DECIMAL'
      });
      expect(state.currentValue).toBe('12.');
    });

    it('should start with 0. when waiting for operand', () => {
      const initialStateWaiting: CalculatorState = {
        ...initialState,
        waitingForOperand: true
      };
      const state = calculatorReducer(initialStateWaiting, {
        type: 'INPUT_DECIMAL'
      });
      expect(state.currentValue).toBe('0.');
      expect(state.waitingForOperand).toBe(false);
    });
  });

  describe('PERFORM_OPERATION', () => {
    it('should set operation when no previous value', () => {
      const initialStateWithNumber: CalculatorState = {
        ...initialState,
        currentValue: '10'
      };
      const state = calculatorReducer(initialStateWithNumber, {
        type: 'PERFORM_OPERATION',
        payload: '+'
      });
      expect(state.previousValue).toBe('10');
      expect(state.operation).toBe('+');
      expect(state.waitingForOperand).toBe(true);
    });

    it('should change operation when waiting for operand', () => {
      const initialStateWithOperation: CalculatorState = {
        ...initialState,
        previousValue: '10',
        operation: '+',
        waitingForOperand: true
      };
      const state = calculatorReducer(initialStateWithOperation, {
        type: 'PERFORM_OPERATION',
        payload: '-'
      });
      expect(state.operation).toBe('-');
      expect(state.previousValue).toBe('10');
    });

    it('should calculate and set new operation', () => {
      const initialStateWithOperation: CalculatorState = {
        ...initialState,
        currentValue: '5',
        previousValue: '10',
        operation: '+',
        waitingForOperand: false
      };
      const state = calculatorReducer(initialStateWithOperation, {
        type: 'PERFORM_OPERATION',
        payload: '*'
      });
      expect(state.currentValue).toBe('15');
      expect(state.previousValue).toBe('15');
      expect(state.operation).toBe('*');
      expect(state.waitingForOperand).toBe(true);
    });
  });

  describe('CALCULATE', () => {
    it('should calculate result', () => {
      const initialStateWithOperation: CalculatorState = {
        ...initialState,
        currentValue: '5',
        previousValue: '10',
        operation: '+'
      };
      const state = calculatorReducer(initialStateWithOperation, {
        type: 'CALCULATE'
      });
      expect(state.currentValue).toBe('15');
      expect(state.previousValue).toBe(null);
      expect(state.operation).toBe(null);
      expect(state.waitingForOperand).toBe(true);
    });

    it('should not calculate without previous value', () => {
      const state = calculatorReducer(initialState, {
        type: 'CALCULATE'
      });
      expect(state).toEqual(initialState);
    });

    it('should handle division by zero error', () => {
      const initialStateWithDivision: CalculatorState = {
        ...initialState,
        currentValue: '0',
        previousValue: '10',
        operation: '/'
      };
      const state = calculatorReducer(initialStateWithDivision, {
        type: 'CALCULATE'
      });
      expect(state.error).toBe('Cannot divide by zero');
    });
  });

  describe('CLEAR', () => {
    it('should reset to initial state but preserve memory', () => {
      const stateWithMemory: CalculatorState = {
        currentValue: '123',
        previousValue: '456',
        operation: '+',
        waitingForOperand: true,
        memory: 100,
        error: 'Some error'
      };
      const state = calculatorReducer(stateWithMemory, {
        type: 'CLEAR'
      });
      expect(state).toEqual({
        ...initialState,
        memory: 100
      });
    });
  });

  describe('CLEAR_ENTRY', () => {
    it('should reset current value to 0', () => {
      const stateWithValue: CalculatorState = {
        ...initialState,
        currentValue: '123',
        error: 'Some error'
      };
      const state = calculatorReducer(stateWithValue, {
        type: 'CLEAR_ENTRY'
      });
      expect(state.currentValue).toBe('0');
      expect(state.error).toBe(null);
    });
  });

  describe('Memory Operations', () => {
    describe('MEMORY_STORE', () => {
      it('should store current value in memory', () => {
        const stateWithValue: CalculatorState = {
          ...initialState,
          currentValue: '123'
        };
        const state = calculatorReducer(stateWithValue, {
          type: 'MEMORY_STORE'
        });
        expect(state.memory).toBe(123);
      });

      it('should not store invalid values', () => {
        const stateWithInvalidValue: CalculatorState = {
          ...initialState,
          currentValue: 'abc'
        };
        const state = calculatorReducer(stateWithInvalidValue, {
          type: 'MEMORY_STORE'
        });
        expect(state.memory).toBe(0); // Should preserve existing memory
      });
    });

    describe('MEMORY_RECALL', () => {
      it('should recall memory value', () => {
        const stateWithMemory: CalculatorState = {
          ...initialState,
          memory: 456
        };
        const state = calculatorReducer(stateWithMemory, {
          type: 'MEMORY_RECALL'
        });
        expect(state.currentValue).toBe('456');
        expect(state.waitingForOperand).toBe(false);
      });
    });

    describe('MEMORY_CLEAR', () => {
      it('should clear memory', () => {
        const stateWithMemory: CalculatorState = {
          ...initialState,
          memory: 123
        };
        const state = calculatorReducer(stateWithMemory, {
          type: 'MEMORY_CLEAR'
        });
        expect(state.memory).toBe(0);
      });
    });
  });

  describe('SET_ERROR', () => {
    it('should set error message', () => {
      const state = calculatorReducer(initialState, {
        type: 'SET_ERROR',
        payload: 'Test error'
      });
      expect(state.error).toBe('Test error');
    });
  });
});