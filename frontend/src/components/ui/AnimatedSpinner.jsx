import { motion } from 'framer-motion';

const AnimatedSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const spinnerVariants = {
    rotate: {
      rotate: 360,
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }
    },
    pulse: {
      scale: [1, 1.1, 1],
      opacity: [0.5, 1, 0.5],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <motion.div
        className={`${sizeClasses[size]} relative`}
        variants={spinnerVariants}
        animate="rotate"
      >
        {/* Outer ring */}
        <motion.div
          className="absolute inset-0 border-4 border-blue-200 dark:border-gray-600 rounded-full"
          variants={spinnerVariants}
          animate="pulse"
        />
        
        {/* Spinning ring */}
        <motion.div
          className="absolute inset-0 border-4 border-transparent border-t-blue-500 dark:border-t-blue-400 rounded-full"
          variants={spinnerVariants}
          animate="rotate"
        />
        
        {/* Inner dot */}
        <motion.div
          className="absolute inset-2 bg-blue-500 dark:bg-blue-400 rounded-full"
          variants={spinnerVariants}
          animate="pulse"
        />
      </motion.div>
    </div>
  );
};

export default AnimatedSpinner;
