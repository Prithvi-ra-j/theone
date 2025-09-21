import React from 'react';
import { motion } from 'framer-motion';

const ProgressBar = ({ 
  progress, 
  label, 
  size = 'md', 
  color = 'primary', 
  showPercentage = true, 
  animated = true,
  className = '' 
}) => {
  // Normalize progress: coerce to number and clamp between 0 and 100
  const numericProgress = Number.isFinite(Number(progress)) ? Number(progress) : 0;
  const clampedProgress = Math.min(Math.max(numericProgress, 0), 100);
  // Fraction used for framer-motion numeric animation (0 -> 1)
  const fraction = clampedProgress / 100;
  
  // Size variants
  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
    xl: 'h-6'
  };
  
  // Color variants
  const colorClasses = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    success: 'bg-success-600',
    warning: 'bg-warning-600',
    danger: 'bg-danger-600',
    info: 'bg-blue-600'
  };
  
  // Background color variants
  const bgColorClasses = {
    primary: 'bg-primary-100',
    secondary: 'bg-secondary-100',
    success: 'bg-success-100',
    warning: 'bg-warning-100',
    danger: 'bg-danger-100',
    info: 'bg-blue-100'
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          {showPercentage && (
            <span className="text-sm font-medium text-gray-600">
              {Math.round(clampedProgress)}%
            </span>
          )}
        </div>
      )}
      
      <div className={`w-full ${sizeClasses[size]} bg-gray-200 rounded-full overflow-hidden ${bgColorClasses[color]}`}>
        <motion.div
          className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full transition-all duration-300 ease-out`}
          // Use numeric animation to avoid animating from '0%' to 'NaN%'.
          // Animate the scaleX transform which accepts numeric values.
          initial={animated ? { scaleX: 0 } : false}
          animate={animated ? { scaleX: fraction } : false}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={!animated ? { width: `${clampedProgress}%`, transformOrigin: 'left' } : { transformOrigin: 'left' }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
