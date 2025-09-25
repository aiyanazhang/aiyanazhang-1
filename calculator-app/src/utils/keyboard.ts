import type { KeyMapping, ButtonType } from '../types/calculator';

/**
 * Keyboard to calculator button mapping
 */
export const keyMapping: KeyMapping = {
  // Numbers
  '0': { value: '0', type: 'number' },
  '1': { value: '1', type: 'number' },
  '2': { value: '2', type: 'number' },
  '3': { value: '3', type: 'number' },
  '4': { value: '4', type: 'number' },
  '5': { value: '5', type: 'number' },
  '6': { value: '6', type: 'number' },
  '7': { value: '7', type: 'number' },
  '8': { value: '8', type: 'number' },
  '9': { value: '9', type: 'number' },
  
  // Operations
  '+': { value: '+', type: 'operation' },
  '-': { value: '-', type: 'operation' },
  '*': { value: '*', type: 'operation' },
  '/': { value: '/', type: 'operation' },
  
  // Decimal point
  '.': { value: '.', type: 'function' },
  
  // Equals
  '=': { value: '=', type: 'equals' },
  'Enter': { value: '=', type: 'equals' },
  
  // Clear functions
  'Escape': { value: 'AC', type: 'function' },
  'Delete': { value: 'CE', type: 'function' },
  'Backspace': { value: 'CE', type: 'function' },
  
  // Memory functions
  'm': { value: 'M+', type: 'function' },
  'M': { value: 'M+', type: 'function' },
  'r': { value: 'MR', type: 'function' },
  'R': { value: 'MR', type: 'function' },
  'c': { value: 'MC', type: 'function' },
  'C': { value: 'MC', type: 'function' },
};

/**
 * Checks if a key is valid for calculator input
 */
export const isValidKey = (key: string): boolean => {
  return key in keyMapping;
};

/**
 * Gets button configuration for a keyboard key
 */
export const getButtonFromKey = (key: string): { value: string; type: ButtonType } | null => {
  return keyMapping[key] || null;
};

/**
 * Prevents default behavior for calculator keys
 */
export const shouldPreventDefault = (key: string): boolean => {
  const preventKeys = ['/', '*', '+', '-', '=', 'Enter', 'Escape', 'Delete', 'Backspace'];
  return preventKeys.includes(key);
};