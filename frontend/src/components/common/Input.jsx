import React, { forwardRef } from 'react';
import clsx from 'clsx';

const Input = forwardRef(({
  label,
  error,
  help,
  required = false,
  className = '',
  ...props
}, ref) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="text-danger-500 ml-1">*</span>}
        </label>
      )}
      
      <input
        ref={ref}
        className={clsx(
          'form-input',
          error && 'border-danger-300 focus:border-danger-500 focus:ring-danger-500',
          className
        )}
        {...props}
      />
      
      {error && (
        <p className="form-error">{error}</p>
      )}
      
      {help && !error && (
        <p className="form-help">{help}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;