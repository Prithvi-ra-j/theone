import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Zap, 
  Heart, 
  Star, 
  Target, 
  TrendingUp,
  RotateCcw,
  Play,
  Pause
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from '../components/ui/ThemeToggle';
import AnimatedCard from '../components/ui/AnimatedCard';
import AnimatedSpinner from '../components/ui/AnimatedSpinner';
import EnhancedTaskCard from '../components/ui/EnhancedTaskCard';
import PageTransition from '../components/ui/PageTransition';

const AnimationDemo = () => {
  const { theme, isDark } = useTheme();
  const [isPlaying, setIsPlaying] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  const sampleTask = {
    id: 1,
    title: "Complete Animation Demo",
    description: "This is a sample task to demonstrate the enhanced task card animations and interactions.",
    priority: "high",
    status: "in_progress",
    progress: 75,
    due_date: new Date(Date.now() + 86400000).toISOString(),
    tags: ["demo", "animation", "frontend"],
    completed: false
  };

  const floatingElements = [
    { icon: Sparkles, delay: 0, color: "text-yellow-400" },
    { icon: Heart, delay: 0.5, color: "text-pink-400" },
    { icon: Star, delay: 1, color: "text-blue-400" },
    { icon: Zap, delay: 1.5, color: "text-purple-400" },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.9 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  const floatingVariants = {
    animate: {
      y: [-10, 10, -10],
      rotate: [0, 5, -5, 0],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  const confettiVariants = {
    initial: { y: -100, opacity: 1 },
    animate: { y: 1000, opacity: 0 }
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        {/* Header */}
        <motion.div 
          className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white py-8"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <motion.div
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <h1 className="text-4xl font-bold mb-2">🎨 Animation Demo</h1>
                <p className="text-blue-100">Experience the power of Framer Motion animations</p>
              </motion.div>
              
              <motion.div
                initial={{ x: 50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                <ThemeToggle />
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Floating Elements */}
        <div className="relative overflow-hidden">
          {floatingElements.map((element, index) => (
            <motion.div
              key={index}
              className={`absolute ${element.color} text-4xl`}
              style={{
                left: `${20 + index * 20}%`,
                top: '20%'
              }}
              variants={floatingVariants}
              animate="animate"
              initial={{ y: 0, rotate: 0 }}
            >
              <element.icon />
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-8"
          >
            {/* Theme Info Card */}
            <AnimatedCard delay={0} className="p-6 text-center">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Current Theme: {theme.toUpperCase()}
                </h2>
                <div className="flex items-center justify-center space-x-4">
                  <div className={`w-8 h-8 rounded-full ${isDark ? 'bg-gray-800' : 'bg-yellow-400'}`} />
                  <span className="text-lg text-gray-600 dark:text-gray-300">
                    {isDark ? '🌙 Dark Mode' : '☀️ Light Mode'}
                  </span>
                </div>
              </motion.div>
            </AnimatedCard>

            {/* Interactive Demo Section */}
            <AnimatedCard delay={1} className="p-6">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Interactive Elements
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Animation Controls */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Animation Controls
                    </h3>
                    
                    <motion.button
                      className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors duration-200"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsPlaying(!isPlaying)}
                    >
                      {isPlaying ? <Pause className="w-5 h-5 inline mr-2" /> : <Play className="w-5 h-5 inline mr-2" />}
                      {isPlaying ? 'Pause' : 'Play'} Animations
                    </motion.button>

                    <motion.button
                      className="w-full py-3 px-4 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors duration-200"
                      whileHover={{ scale: 1.05, rotate: 5 }}
                      whileTap={{ scale: 0.95, rotate: -5 }}
                      onClick={() => setShowConfetti(true)}
                    >
                      🎉 Show Confetti
                    </motion.button>
                  </div>

                  {/* Live Spinner */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Live Spinner
                    </h3>
                    <div className="flex justify-center">
                      <AnimatedSpinner size="lg" />
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatedCard>

            {/* Enhanced Task Card Demo */}
            <AnimatedCard delay={2} className="p-6">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Enhanced Task Card
                </h2>
                <div className="max-w-md mx-auto">
                  <EnhancedTaskCard
                    task={sampleTask}
                    onComplete={(id) => console.log('Completed:', id)}
                    onEdit={(task) => console.log('Edit:', task)}
                    onDelete={(id) => console.log('Delete:', id)}
                  />
                </div>
              </motion.div>
            </AnimatedCard>

            {/* Animation Showcase */}
            <AnimatedCard delay={3} className="p-6">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Animation Showcase
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { icon: Target, label: "Bounce", animation: "animate-bounce-gentle" },
                    { icon: TrendingUp, label: "Float", animation: "animate-float" },
                    { icon: Heart, label: "Pulse", animation: "animate-pulse-slow" },
                    { icon: Star, label: "Shimmer", animation: "animate-shimmer" }
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      className="text-center p-4 bg-gray-100 dark:bg-gray-700 rounded-lg"
                      whileHover={{ scale: 1.1, y: -5 }}
                      whileTap={{ scale: 0.9 }}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                    >
                      <div className={`w-12 h-12 mx-auto mb-2 ${item.animation}`}>
                        <item.icon className="w-full h-full text-blue-500" />
                      </div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {item.label}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </AnimatedCard>

            {/* Glass Morphism Demo */}
            <AnimatedCard delay={4} className="p-6">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Glass Morphism Effect
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[1, 2, 3].map((item) => (
                    <motion.div
                      key={item}
                      className="glass-card p-6 text-center"
                      whileHover={{ scale: 1.05, rotateY: 5 }}
                      initial={{ opacity: 0, rotateY: -15 }}
                      animate={{ opacity: 1, rotateY: 0 }}
                      transition={{ duration: 0.5, delay: 0.6 + item * 0.1 }}
                    >
                      <div className="w-16 h-16 mx-auto mb-4 bg-white/20 rounded-full flex items-center justify-center">
                        <span className="text-2xl">✨</span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                        Glass Card {item}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Beautiful glass morphism effect with backdrop blur
                      </p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </AnimatedCard>
          </motion.div>
        </div>

        {/* Confetti Animation */}
        <AnimatePresence>
          {showConfetti && (
            <motion.div
              className="fixed inset-0 pointer-events-none z-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onAnimationComplete={() => {
                setTimeout(() => setShowConfetti(false), 3000);
              }}
            >
              {[...Array(50)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-gradient-to-r from-yellow-400 to-red-500 rounded-full"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: '-10px'
                  }}
                  variants={confettiVariants}
                  initial="initial"
                  animate="animate"
                  transition={{
                    duration: 3,
                    delay: Math.random() * 2,
                    ease: "easeOut"
                  }}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  );
};

export default AnimationDemo;
