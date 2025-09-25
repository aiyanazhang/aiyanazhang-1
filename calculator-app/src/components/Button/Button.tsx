import React, { useCallback } from 'react';
import type { ButtonProps } from '../../types/calculator';
import styles from './Button.module.css';

/**
 * Button component for calculator operations and numbers
 */
const Button: React.FC<ButtonProps> = ({ 
  label, 
  type, 
  onClick, 
  className = '', 
  disabled = false,
  ariaLabel
}) => {
  const handleClick = useCallback(() => {
    if (!disabled) {
      onClick(label);
    }
  }, [label, onClick, disabled]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if ((event.key === 'Enter' || event.key === ' ') && !disabled) {
      event.preventDefault();
      onClick(label);
    }
  }, [label, onClick, disabled]);

  const buttonClasses = [
    styles.button,
    styles[type],
    className,
    disabled ? styles.disabled : ''
  ].filter(Boolean).join(' ');

  return (
    <button
      className={buttonClasses}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      type="button"
      aria-label={ariaLabel || `${type} button ${label}`}
      tabIndex={disabled ? -1 : 0}
    >
      <span className={styles.label}>
        {label}
      </span>
    </button>
  );
};

export default Button;