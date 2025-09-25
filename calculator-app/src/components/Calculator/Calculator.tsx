import React, { useReducer, useEffect, useCallback } from 'react';
import type { ButtonType } from '../../types/calculator';
import { calculatorReducer, initialState } from '../../utils/calculatorReducer';
import { isValidKey, getButtonFromKey, shouldPreventDefault } from '../../utils/keyboard';
import Display from '../Display/Display';
import ButtonGrid from '../ButtonGrid/ButtonGrid';
import styles from './Calculator.module.css';

/**
 * Main Calculator component with state management
 */
const Calculator: React.FC = () => {
  const [state, dispatch] = useReducer(calculatorReducer, initialState);

  /**
   * Handle button clicks from the button grid
   */
  const handleButtonClick = useCallback((value: string, type: ButtonType) => {
    switch (type) {
      case 'number':
        dispatch({ type: 'INPUT_NUMBER', payload: value });
        break;
      
      case 'operation':
        dispatch({ type: 'PERFORM_OPERATION', payload: value });
        break;
      
      case 'equals':
        dispatch({ type: 'CALCULATE' });
        break;
      
      case 'function':
        handleFunctionButton(value);
        break;
    }
  }, []);

  /**
   * Handle function button operations
   */
  const handleFunctionButton = useCallback((value: string) => {
    switch (value) {
      case '.':
        dispatch({ type: 'INPUT_DECIMAL' });
        break;
      
      case 'AC':
        dispatch({ type: 'CLEAR' });
        break;
      
      case 'CE':
        dispatch({ type: 'CLEAR_ENTRY' });
        break;
      
      case 'M+':
        dispatch({ type: 'MEMORY_STORE' });
        break;
      
      case 'MR':
        dispatch({ type: 'MEMORY_RECALL' });
        break;
      
      case 'MC':
        dispatch({ type: 'MEMORY_CLEAR' });
        break;
      
      default:
        console.warn(`Unknown function button: ${value}`);
    }
  }, []);

  /**
   * Handle keyboard input
   */
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const { key } = event;
    
    if (!isValidKey(key)) return;
    
    if (shouldPreventDefault(key)) {
      event.preventDefault();
    }
    
    const buttonConfig = getButtonFromKey(key);
    if (buttonConfig) {
      handleButtonClick(buttonConfig.value, buttonConfig.type);
    }
  }, [handleButtonClick]);

  /**
   * Set up and clean up keyboard event listeners
   */
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  /**
   * Check if calculator has memory stored
   */
  const hasMemory = state.memory !== 0;

  return (
    <div 
      className={styles.calculator}
      role="application"
      aria-label="Calculator"
      tabIndex={-1}
    >
      <div className={styles.calculatorBody}>
        <Display 
          value={state.currentValue}
          error={state.error || undefined}
          hasMemory={hasMemory}
        />
        
        <ButtonGrid 
          onButtonClick={handleButtonClick}
          disabled={!!state.error}
        />
      </div>
      
      {/* Screen reader announcements */}
      <div 
        className={styles.srOnly}
        aria-live="polite"
        aria-atomic="true"
      >
        {state.error && `Error: ${state.error}`}
        {state.operation && !state.error && `Operation: ${state.operation}`}
      </div>
    </div>
  );
};

export default Calculator;