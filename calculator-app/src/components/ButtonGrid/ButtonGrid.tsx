import React, { memo } from 'react';
import type { ButtonGridProps, ButtonConfig } from '../../types/calculator';
import Button from '../Button/Button';
import styles from './ButtonGrid.module.css';

/**
 * Button configuration for the calculator layout
 */
const buttonConfigs: ButtonConfig[] = [
  // Row 1: Memory and Clear functions
  { label: 'MC', value: 'MC', type: 'function', ariaLabel: 'Memory Clear' },
  { label: 'MR', value: 'MR', type: 'function', ariaLabel: 'Memory Recall' },
  { label: 'M+', value: 'M+', type: 'function', ariaLabel: 'Memory Store' },
  { label: 'AC', value: 'AC', type: 'function', ariaLabel: 'All Clear' },
  
  // Row 2: Functions and operations
  { label: 'CE', value: 'CE', type: 'function', ariaLabel: 'Clear Entry' },
  { label: '/', value: '/', type: 'operation', ariaLabel: 'Divide' },
  { label: '*', value: '*', type: 'operation', ariaLabel: 'Multiply' },
  { label: '-', value: '-', type: 'operation', ariaLabel: 'Subtract' },
  
  // Row 3: Numbers 7-9 and operations
  { label: '7', value: '7', type: 'number', ariaLabel: 'Seven' },
  { label: '8', value: '8', type: 'number', ariaLabel: 'Eight' },
  { label: '9', value: '9', type: 'number', ariaLabel: 'Nine' },
  { label: '+', value: '+', type: 'operation', ariaLabel: 'Add', className: styles.tallButton },
  
  // Row 4: Numbers 4-6
  { label: '4', value: '4', type: 'number', ariaLabel: 'Four' },
  { label: '5', value: '5', type: 'number', ariaLabel: 'Five' },
  { label: '6', value: '6', type: 'number', ariaLabel: 'Six' },
  
  // Row 5: Numbers 1-3
  { label: '1', value: '1', type: 'number', ariaLabel: 'One' },
  { label: '2', value: '2', type: 'number', ariaLabel: 'Two' },
  { label: '3', value: '3', type: 'number', ariaLabel: 'Three' },
  { label: '=', value: '=', type: 'equals', ariaLabel: 'Equals', className: styles.tallButton },
  
  // Row 6: Zero and decimal
  { label: '0', value: '0', type: 'number', ariaLabel: 'Zero', className: styles.wideButton },
  { label: '.', value: '.', type: 'function', ariaLabel: 'Decimal point' },
];

/**
 * ButtonGrid component for calculator button layout
 */
const ButtonGrid: React.FC<ButtonGridProps> = memo(({ onButtonClick, disabled = false }) => {
  const handleButtonClick = (value: string) => {
    const config = buttonConfigs.find(btn => btn.value === value);
    if (config) {
      onButtonClick(value, config.type);
    }
  };

  return (
    <div className={styles.buttonGrid} role="grid" aria-label="Calculator buttons">
      {buttonConfigs.map((config, index) => {
        // Special layout handling for buttons that span multiple cells
        const isAddButton = config.value === '+';
        const isEqualsButton = config.value === '=';
        const isZeroButton = config.value === '0';
        
        // Skip rendering equals button in its first position since it spans two rows
        if (isEqualsButton && index === 11) {
          return null;
        }
        
        return (
          <div
            key={config.value}
            className={`${styles.buttonCell} ${config.className || ''}`}
            style={{
              gridColumn: isZeroButton ? '1 / 3' : undefined,
              gridRow: isAddButton ? 'span 2' : isEqualsButton ? 'span 2' : undefined
            }}
          >
            <Button
              label={config.label}
              type={config.type}
              onClick={handleButtonClick}
              disabled={disabled}
              ariaLabel={config.ariaLabel}
              className={config.className}
            />
          </div>
        );
      })}
      
      {/* Render equals button separately to position it correctly */}
      <div 
        className={`${styles.buttonCell} ${styles.tallButton}`}
        style={{ gridColumn: '4', gridRow: '5 / 7' }}
      >
        <Button
          label="="
          type="equals"
          onClick={handleButtonClick}
          disabled={disabled}
          ariaLabel="Equals"
        />
      </div>
    </div>
  );
});

ButtonGrid.displayName = 'ButtonGrid';

export default ButtonGrid;