import React from 'react';

export default function Input({ 
  label, 
  type = "text", 
  value, 
  onChange, 
  placeholder,
  name,
  disabled = false,
  required = false,
  className = "",
  ...props 
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        name={name}
        disabled={disabled}
        required={required}
        className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                   focus:outline-none focus:ring-2 focus:ring-primary-500 
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 
                   placeholder-gray-400 dark:placeholder-gray-500
                   ${disabled ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-800' : ''}
                   ${className}`}
        {...props}
      />
    </div>
  );
}
