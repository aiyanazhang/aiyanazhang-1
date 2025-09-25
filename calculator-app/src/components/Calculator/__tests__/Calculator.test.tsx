import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Calculator from '../Calculator';

// Mock CSS modules
jest.mock('../Calculator.module.css', () => ({
  calculator: 'calculator',
  calculatorBody: 'calculatorBody',
  srOnly: 'srOnly'
}));

jest.mock('../../Display/Display.module.css', () => ({
  displayContainer: 'displayContainer',
  indicators: 'indicators',
  memoryIndicator: 'memoryIndicator',
  display: 'display',
  error: 'error',
  errorMessage: 'errorMessage'
}));

jest.mock('../../Button/Button.module.css', () => ({
  button: 'button',
  label: 'label',
  number: 'number',
  operation: 'operation',
  equals: 'equals',
  function: 'function',
  disabled: 'disabled'
}));

jest.mock('../../ButtonGrid/ButtonGrid.module.css', () => ({
  buttonGrid: 'buttonGrid',
  buttonCell: 'buttonCell',
  wideButton: 'wideButton',
  tallButton: 'tallButton'
}));

describe('Calculator Integration Tests', () => {
  beforeEach(() => {
    render(<Calculator />);
  });

  describe('Basic Arithmetic Operations', () => {
    it('should perform addition correctly', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /two/i }));
      await user.click(screen.getByRole('button', { name: /add/i }));
      await user.click(screen.getByRole('button', { name: /three/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/5/)).toBeInTheDocument();
    });

    it('should perform subtraction correctly', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /subtract/i }));
      await user.click(screen.getByRole('button', { name: /three/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/2/)).toBeInTheDocument();
    });

    it('should perform multiplication correctly', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /four/i }));
      await user.click(screen.getByRole('button', { name: /multiply/i }));
      await user.click(screen.getByRole('button', { name: /three/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/12/)).toBeInTheDocument();
    });

    it('should perform division correctly', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /eight/i }));
      await user.click(screen.getByRole('button', { name: /divide/i }));
      await user.click(screen.getByRole('button', { name: /four/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/2/)).toBeInTheDocument();
    });
  });

  describe('Decimal Operations', () => {
    it('should handle decimal numbers', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /one/i }));
      await user.click(screen.getByRole('button', { name: /decimal point/i }));
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /add/i }));
      await user.click(screen.getByRole('button', { name: /two/i }));
      await user.click(screen.getByRole('button', { name: /decimal point/i }));
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/4/)).toBeInTheDocument();
    });

    it('should not add multiple decimal points', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /one/i }));
      await user.click(screen.getByRole('button', { name: /decimal point/i }));
      await user.click(screen.getByRole('button', { name: /decimal point/i }));
      await user.click(screen.getByRole('button', { name: /five/i }));
      
      expect(screen.getByDisplayValue(/1\\.5/)).toBeInTheDocument();
    });
  });

  describe('Clear Functions', () => {
    it('should clear all with AC button', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /add/i }));
      await user.click(screen.getByRole('button', { name: /three/i }));
      await user.click(screen.getByRole('button', { name: /all clear/i }));
      
      expect(screen.getByDisplayValue(/0/)).toBeInTheDocument();
    });

    it('should clear entry with CE button', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /six/i }));
      await user.click(screen.getByRole('button', { name: /clear entry/i }));
      
      expect(screen.getByDisplayValue(/0/)).toBeInTheDocument();
    });
  });

  describe('Memory Functions', () => {
    it('should store and recall memory', async () => {
      const user = userEvent.setup();
      
      // Enter a number and store in memory
      await user.click(screen.getByRole('button', { name: /seven/i }));
      await user.click(screen.getByRole('button', { name: /memory store/i }));
      
      // Clear display and perform different calculation
      await user.click(screen.getByRole('button', { name: /all clear/i }));
      await user.click(screen.getByRole('button', { name: /five/i }));
      
      // Recall memory
      await user.click(screen.getByRole('button', { name: /memory recall/i }));
      
      expect(screen.getByDisplayValue(/7/)).toBeInTheDocument();
    });

    it('should clear memory', async () => {
      const user = userEvent.setup();
      
      // Store a number in memory
      await user.click(screen.getByRole('button', { name: /nine/i }));
      await user.click(screen.getByRole('button', { name: /memory store/i }));
      
      // Clear memory
      await user.click(screen.getByRole('button', { name: /memory clear/i }));
      
      // Clear display and try to recall
      await user.click(screen.getByRole('button', { name: /all clear/i }));
      await user.click(screen.getByRole('button', { name: /memory recall/i }));
      
      expect(screen.getByDisplayValue(/0/)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle division by zero', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /five/i }));
      await user.click(screen.getByRole('button', { name: /divide/i }));
      await user.click(screen.getByRole('button', { name: /zero/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByText(/cannot divide by zero/i)).toBeInTheDocument();
    });
  });

  describe('Keyboard Input', () => {
    it('should respond to keyboard number input', async () => {
      const user = userEvent.setup();
      
      await user.keyboard('123');
      
      expect(screen.getByDisplayValue(/123/)).toBeInTheDocument();
    });

    it('should respond to keyboard operations', async () => {
      const user = userEvent.setup();
      
      await user.keyboard('5+3=');
      
      expect(screen.getByDisplayValue(/8/)).toBeInTheDocument();
    });

    it('should clear with Escape key', async () => {
      const user = userEvent.setup();
      
      await user.keyboard('123');
      await user.keyboard('{Escape}');
      
      expect(screen.getByDisplayValue(/0/)).toBeInTheDocument();
    });
  });

  describe('Chain Operations', () => {
    it('should handle chained operations', async () => {
      const user = userEvent.setup();
      
      await user.click(screen.getByRole('button', { name: /two/i }));
      await user.click(screen.getByRole('button', { name: /add/i }));
      await user.click(screen.getByRole('button', { name: /three/i }));
      await user.click(screen.getByRole('button', { name: /multiply/i }));
      await user.click(screen.getByRole('button', { name: /four/i }));
      await user.click(screen.getByRole('button', { name: /equals/i }));
      
      expect(screen.getByDisplayValue(/20/)).toBeInTheDocument();
    });
  });
});