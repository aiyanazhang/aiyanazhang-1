import type { CalculatorError, Operation } from '../types/calculator';

/**
 * Performs arithmetic calculations
 */
export const calculate = (firstOperand: string, secondOperand: string, operation: Operation): string => {
  const first = parseFloat(firstOperand);
  const second = parseFloat(secondOperand);
  
  if (isNaN(first) || isNaN(second)) {
    throw new Error('INVALID_INPUT');
  }

  let result: number;
  
  switch (operation) {
    case '+':
      result = first + second;
      break;
    case '-':
      result = first - second;
      break;
    case '*':
      result = first * second;
      break;
    case '/':
      if (second === 0) {
        throw new Error('DIVISION_BY_ZERO');
      }
      result = first / second;
      break;
    default:
      throw new Error('INVALID_OPERATION');
  }

  // Check for overflow
  if (!isFinite(result)) {
    throw new Error('OVERFLOW');
  }

  return result.toString();
};

/**
 * Formats display number with proper decimal places and commas
 */
export const formatDisplayValue = (value: string): string => {
  if (!value || value === '0') return '0';
  
  const num = parseFloat(value);
  if (isNaN(num)) return value;

  // Handle very large or very small numbers with scientific notation
  if (Math.abs(num) >= 1e15 || (Math.abs(num) < 1e-6 && num !== 0)) {
    return num.toExponential(6);
  }

  // Format with appropriate decimal places
  const formatted = num.toLocaleString('en-US', {
    maximumFractionDigits: 10,
    useGrouping: true
  });

  return formatted;
};

/**
 * Validates if input is a valid number
 */
export const isValidNumber = (input: string): boolean => {
  if (!input || input.trim() === '') return false;
  
  // Check for multiple decimal points
  const decimalCount = (input.match(/\./g) || []).length;
  if (decimalCount > 1) return false;
  
  const num = parseFloat(input);
  return !isNaN(num) && isFinite(num);
};

/**
 * Handles decimal point input
 */
export const handleDecimalInput = (currentValue: string): string => {
  if (currentValue.includes('.')) {
    return currentValue;
  }
  return currentValue === '0' ? '0.' : `${currentValue}.`;
};

/**
 * Handles number input
 */
export const handleNumberInput = (currentValue: string, digit: string): string => {
  if (currentValue === '0' && digit !== '.') {
    return digit;
  }
  return currentValue + digit;
};

/**
 * Gets error message for calculator errors
 */
export const getErrorMessage = (error: CalculatorError): string => {
  switch (error) {
    case 'DIVISION_BY_ZERO':
      return 'Cannot divide by zero';
    case 'INVALID_OPERATION':
      return 'Invalid operation';
    case 'OVERFLOW':
      return 'Number too large';
    case 'INVALID_INPUT':
      return 'Invalid input';
    default:
      return 'Unknown error';
  }
};

/**
 * Clamps a number to prevent display overflow
 */
export const clampDisplayValue = (value: number): number => {
  const MAX_SAFE_DISPLAY = 1e15;
  const MIN_SAFE_DISPLAY = -1e15;
  
  if (value > MAX_SAFE_DISPLAY) return MAX_SAFE_DISPLAY;
  if (value < MIN_SAFE_DISPLAY) return MIN_SAFE_DISPLAY;
  
  return value;
};