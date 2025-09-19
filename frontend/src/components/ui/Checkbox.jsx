import React from 'react';

const Checkbox = React.forwardRef(({ 
  label, 
  description, 
  checked, 
  onChange, 
  name, 
  disabled = false,
  className = "",
  ...props 
}, ref) => {
  return (
    <div className={`flex items-center ${className}`}>
      <div className="flex items-center h-5">
        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          name={name}
          disabled={disabled}
          ref={ref}
          className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500 focus:ring-2
                    disabled:opacity-50 disabled:cursor-not-allowed"
          {...props}
        />
      </div>
      {(label || description) && (
        <div className="ml-3 text-sm">
          {label && (
            <label 
              htmlFor={name} 
              className={`font-medium text-gray-700 dark:text-gray-300 ${disabled ? 'opacity-50' : ''}`}
            >
              {label}
            </label>
          )}
          {description && (
            <p className={`text-gray-500 dark:text-gray-400 ${disabled ? 'opacity-50' : ''}`}>
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

export default Checkbox;