import { motion } from 'framer-motion';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const iconVariants = {
    initial: { scale: 0, rotate: -180 },
    animate: { scale: 1, rotate: 0 },
    exit: { scale: 0, rotate: 180 }
  };

  const containerVariants = {
    hover: { scale: 1.05 },
    tap: { scale: 0.95 }
  };

  const getIcon = () => {
    if (theme === 'dark') {
      return <Moon className="w-5 h-5" />;
    } else if (theme === 'light') {
      return <Sun className="w-5 h-5" />;
    }
    return <Monitor className="w-5 h-5" />;
  };

  return (
    <motion.button
      onClick={toggleTheme}
      className={`relative p-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 ${className}`}
      variants={containerVariants}
      whileHover="hover"
      whileTap="tap"
      title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      <motion.div
        key={theme}
        initial="initial"
        animate="animate"
        exit="exit"
        variants={iconVariants}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="flex items-center justify-center"
      >
        {getIcon()}
      </motion.div>
      
      {/* Animated background ring */}
      <motion.div
        className="absolute inset-0 rounded-full border-2 border-white/20"
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      
      {/* Pulse effect on hover */}
      <motion.div
        className="absolute inset-0 rounded-full bg-white/10"
        initial={{ scale: 0, opacity: 0 }}
        whileHover={{ scale: 1.2, opacity: 0 }}
        transition={{ duration: 0.6 }}
      />
    </motion.button>
  );
};

export default ThemeToggle;
