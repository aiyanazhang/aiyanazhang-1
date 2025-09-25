import { calculate, formatDisplayValue, isValidNumber, handleDecimalInput, handleNumberInput, getErrorMessage } from '../calculator';

describe('Calculator Utilities', () => {
  describe('calculate', () => {
    it('should perform addition correctly', () => {
      expect(calculate('2', '3', '+')).toBe('5');
      expect(calculate('10.5', '2.5', '+')).toBe('13');
    });

    it('should perform subtraction correctly', () => {
      expect(calculate('5', '3', '-')).toBe('2');
      expect(calculate('10.5', '2.5', '-')).toBe('8');
    });

    it('should perform multiplication correctly', () => {
      expect(calculate('4', '3', '*')).toBe('12');
      expect(calculate('2.5', '4', '*')).toBe('10');
    });

    it('should perform division correctly', () => {
      expect(calculate('12', '3', '/')).toBe('4');
      expect(calculate('10', '4', '/')).toBe('2.5');
    });

    it('should throw error for division by zero', () => {
      expect(() => calculate('5', '0', '/')).toThrow('DIVISION_BY_ZERO');
    });

    it('should throw error for invalid input', () => {
      expect(() => calculate('abc', '5', '+')).toThrow('INVALID_INPUT');
      expect(() => calculate('5', 'xyz', '+')).toThrow('INVALID_INPUT');
    });

    it('should throw error for invalid operation', () => {
      expect(() => calculate('5', '3', '%' as any)).toThrow('INVALID_OPERATION');
    });
  });

  describe('formatDisplayValue', () => {
    it('should format regular numbers correctly', () => {
      expect(formatDisplayValue('123')).toBe('123');
      expect(formatDisplayValue('1234')).toBe('1,234');
      expect(formatDisplayValue('1234567')).toBe('1,234,567');
    });

    it('should handle decimal numbers', () => {
      expect(formatDisplayValue('123.456')).toBe('123.456');
      expect(formatDisplayValue('1234.56')).toBe('1,234.56');
    });

    it('should handle zero and empty values', () => {
      expect(formatDisplayValue('0')).toBe('0');
      expect(formatDisplayValue('')).toBe('0');
    });

    it('should use scientific notation for very large numbers', () => {
      const result = formatDisplayValue('1000000000000000');
      expect(result).toMatch(/e\+/);
    });

    it('should use scientific notation for very small numbers', () => {
      const result = formatDisplayValue('0.0000001');
      expect(result).toMatch(/e-/);
    });
  });

  describe('isValidNumber', () => {
    it('should validate correct numbers', () => {
      expect(isValidNumber('123')).toBe(true);
      expect(isValidNumber('123.456')).toBe(true);
      expect(isValidNumber('-123')).toBe(true);
      expect(isValidNumber('0')).toBe(true);
    });

    it('should reject invalid numbers', () => {
      expect(isValidNumber('abc')).toBe(false);
      expect(isValidNumber('')).toBe(false);
      expect(isValidNumber('12.34.56')).toBe(false);
    });

    it('should reject infinite values', () => {
      expect(isValidNumber('Infinity')).toBe(false);
      expect(isValidNumber('-Infinity')).toBe(false);
    });
  });

  describe('handleDecimalInput', () => {
    it('should add decimal point to integer', () => {
      expect(handleDecimalInput('123')).toBe('123.');
    });

    it('should not add decimal point if already present', () => {
      expect(handleDecimalInput('123.45')).toBe('123.45');
    });

    it('should handle zero correctly', () => {
      expect(handleDecimalInput('0')).toBe('0.');
    });
  });

  describe('handleNumberInput', () => {
    it('should append digits to existing number', () => {
      expect(handleNumberInput('12', '3')).toBe('123');
      expect(handleNumberInput('12.3', '4')).toBe('12.34');
    });

    it('should replace zero with new digit', () => {
      expect(handleNumberInput('0', '5')).toBe('5');
    });

    it('should not replace zero with decimal point', () => {
      expect(handleNumberInput('0', '.')).toBe('0.');
    });
  });

  describe('getErrorMessage', () => {
    it('should return correct error messages', () => {
      expect(getErrorMessage('DIVISION_BY_ZERO')).toBe('Cannot divide by zero');
      expect(getErrorMessage('INVALID_OPERATION')).toBe('Invalid operation');
      expect(getErrorMessage('OVERFLOW')).toBe('Number too large');
      expect(getErrorMessage('INVALID_INPUT')).toBe('Invalid input');
    });

    it('should return default message for unknown error', () => {
      expect(getErrorMessage('UNKNOWN_ERROR' as any)).toBe('Unknown error');
    });
  });
});