import React, { useMemo } from 'react';
import type { DisplayProps } from '../../types/calculator';
import { formatDisplayValue } from '../../utils/calculator';
import styles from './Display.module.css';

/**
 * Display component for showing calculator values and status
 */
const Display: React.FC<DisplayProps> = ({ value, error, hasMemory }) => {
  const displayValue = useMemo(() => {
    if (error) return 'Error';
    return formatDisplayValue(value);
  }, [value, error]);

  const displayClasses = useMemo(() => {
    return `${styles.display} ${error ? styles.error : ''}`;
  }, [error]);

  return (
    <div className={styles.displayContainer}>
      {/* Memory indicator */}
      <div className={styles.indicators}>
        {hasMemory && (
          <span className={styles.memoryIndicator} aria-label="Memory has value">
            M
          </span>
        )}
      </div>
      
      {/* Main display */}
      <div 
        className={displayClasses}
        role="textbox"
        aria-readonly="true"
        aria-label={`Calculator display showing ${error ? error : displayValue}`}
        aria-live="polite"
        aria-atomic="true"
      >
        {displayValue}
      </div>
      
      {/* Error message */}
      {error && (
        <div 
          className={styles.errorMessage}
          role="alert"
          aria-live="assertive"
        >
          {error}
        </div>
      )}
    </div>
  );
};

export default Display;