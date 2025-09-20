import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Target, 
  Calendar, 
  DollarSign, 
  Heart, 
  Trophy,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { 
  careerAPI, 
  habitsAPI, 
  financeAPI, 
  moodAPI, 
  gamificationAPI 
} from '../api';
import ProgressBar from '../components/ui/ProgressBar';
import TaskCard from '../components/ui/TaskCard';
import { formatCurrency } from '../utils/formatters';
import { useTheme } from '../contexts/ThemeContext';
import AnimatedCard from '../components/ui/AnimatedCard';
import PageTransition from '../components/ui/PageTransition';
import AnimatedSpinner from '../components/ui/AnimatedSpinner';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const { theme, isDark } = useTheme();
  const [timedOut, setTimedOut] = useState(false);

  // Fetch dashboard data
  const { data: careerData, isLoading: careerLoading, isError: careerError, error: careerErrObj } = useQuery({
    queryKey: ['career-dashboard'],
    queryFn: () => careerAPI.getCareerDashboard(),
  });

  const { data: habitsData, isLoading: habitsLoading, isError: habitsError, error: habitsErrObj } = useQuery({
    queryKey: ['habits-dashboard'],
    queryFn: () => habitsAPI.getHabitsDashboard(),
  });

  const { data: financeData, isLoading: financeLoading, isError: financeError, error: financeErrObj } = useQuery({
    queryKey: ['finance-dashboard'],
    queryFn: () => financeAPI.getFinanceDashboard(),
  });

  const { data: moodData, isLoading: moodLoading, isError: moodError, error: moodErrObj } = useQuery({
    queryKey: ['mood-dashboard'],
    queryFn: () => moodAPI.getMoodDashboard(),
  });

  const { data: userStats, isLoading: statsLoading, isError: statsError, error: statsErrObj } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => gamificationAPI.getUserStats(),
  });

  // Timeout logic (after all useQuery hooks)
  useEffect(() => {
    if (!(careerLoading || habitsLoading || financeLoading || moodLoading || statsLoading)) return;
    const timeout = setTimeout(() => setTimedOut(true), 30000);
    return () => clearTimeout(timeout);
  }, [careerLoading, habitsLoading, financeLoading, moodLoading, statsLoading]);

  // Prepare UI elements based on conditions
  let dashboardContent;
  
  if (timedOut) {
    console.error('Dashboard page load timeout: Data did not load within 30 seconds');
    dashboardContent = (
      <div className="flex items-center justify-center min-h-screen bg-yellow-50 dark:bg-yellow-900">
        <div>
          <h2 className="text-xl font-bold text-yellow-700 dark:text-yellow-300">Timeout: Dashboard data did not load within 30 seconds</h2>
          <p className="text-xs text-yellow-600 dark:text-yellow-200">Please check your network or backend server.</p>
        </div>
      </div>
    );
  } else if (careerError || habitsError || financeError || moodError || statsError) {
    console.error('Dashboard load error:', {
      career: careerErrObj,
      habits: habitsErrObj,
      finance: financeErrObj,
      mood: moodErrObj,
      stats: statsErrObj,
    });
    dashboardContent = (
      <div className="flex items-center justify-center min-h-screen bg-red-50 dark:bg-red-900">
        <div>
          <h2 className="text-xl font-bold text-red-700 dark:text-red-300">Error loading dashboard data</h2>
          <pre className="text-xs text-red-600 dark:text-red-200">
            {JSON.stringify({
              career: careerErrObj?.message,
              habits: habitsErrObj?.message,
              finance: financeErrObj?.message,
              mood: moodErrObj?.message,
              stats: statsErrObj?.message,
            }, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  const isLoading = careerLoading || habitsLoading || financeLoading || moodLoading || statsLoading;

  // Calculate overall progress
  const overallProgress = React.useMemo(() => {
    if (!careerData || !habitsData || !financeData || !moodData) return 0;
    
    const careerProgress = careerData.total_goals > 0 
      ? (careerData.completed_goals / careerData.total_goals) * 100 
      : 0;
    
    const habitsProgress = habitsData.total_habits > 0 
      ? (habitsData.completed_habits_today / habitsData.total_habits) * 100 
      : 0;
    
    const financeProgress = financeData.total_goals > 0 
      ? (financeData.completed_goals / financeData.total_goals) * 100 
      : 0;
    
    return Math.round((careerProgress + habitsProgress + financeProgress) / 3);
  }, [careerData, habitsData, financeData, moodData]);

  // Set loading content if still loading
  if (isLoading && !dashboardContent) {
    dashboardContent = (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <AnimatedSpinner size="xl" />
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'career', label: 'Career', icon: Target },
    { id: 'habits', label: 'Habits', icon: Calendar },
    { id: 'finance', label: 'Finance', icon: DollarSign },
    { id: 'mood', label: 'Mood', icon: Heart },
    { id: 'achievements', label: 'Achievements', icon: Trophy },
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
    hidden: { opacity: 0, y: 20, scale: 0.95 },
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

  // If we have dashboardContent (error or loading states), return it
  if (dashboardContent) {
    return dashboardContent;
  }
  
  // Otherwise, render the main dashboard
  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        {/* Header */}
        <motion.div 
          className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-6 flex items-center justify-between">
              <motion.h1 
                className="text-3xl font-bold text-gray-900 dark:text-white"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                Dashboard
              </motion.h1>
              
              {/* Theme toggle moved to the left sidebar for a single global control */}
            </div>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div 
          className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8">
              {tabs.map((tab, index) => (
                <motion.button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                >
                  <div className="flex items-center space-x-2">
                    <tab.icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </div>
                </motion.button>
              ))}
            </nav>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-8"
          >
            {/* Overall Progress Card */}
            <AnimatedCard delay={0} className="p-6">
              <motion.div 
                className="text-center"
                variants={itemVariants}
              >
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Overall Progress
                </h2>
                <div className="relative">
                  <div className="w-32 h-32 mx-auto relative">
                    <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-gray-200 dark:text-gray-700"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <motion.path
                        className="text-blue-500 dark:text-blue-400"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        strokeLinecap="round"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: overallProgress / 100 }}
                        transition={{ duration: 1, delay: 0.5 }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">
                        {overallProgress}%
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatedCard>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  title: 'Career Goals',
                  value: careerData?.total_goals || 0,
                  completed: careerData?.completed_goals || 0,
                  icon: Target,
                  color: 'blue'
                },
                {
                  title: 'Daily Habits',
                  value: habitsData?.total_habits || 0,
                  completed: habitsData?.completed_habits_today || 0,
                  icon: Calendar,
                  color: 'green'
                },
                {
                  title: 'Financial Goals',
                  value: financeData?.total_goals || 0,
                  completed: financeData?.completed_goals || 0,
                  icon: DollarSign,
                  color: 'purple'
                },
                {
                  title: 'Mood Score',
                  value: moodData?.average_mood || 0,
                  completed: moodData?.average_mood || 0,
                  icon: Heart,
                  color: 'pink'
                }
              ].map((stat, index) => (
                <AnimatedCard 
                  key={stat.title} 
                  delay={index + 1}
                  className="p-6 text-center hover-lift"
                >
                  <motion.div
                    className="flex flex-col items-center"
                    variants={itemVariants}
                  >
                    {/* Fixed color classes to use hardcoded values instead of template literals */}
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 ${
                      stat.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900' :
                      stat.color === 'green' ? 'bg-green-100 dark:bg-green-900' :
                      stat.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900' :
                      'bg-pink-100 dark:bg-pink-900'
                    }`}>
                      <stat.icon className={`w-6 h-6 ${
                        stat.color === 'blue' ? 'text-blue-600 dark:text-blue-400' :
                        stat.color === 'green' ? 'text-green-600 dark:text-green-400' :
                        stat.color === 'purple' ? 'text-purple-600 dark:text-purple-400' :
                        'text-pink-600 dark:text-pink-400'
                      }`} />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {stat.title}
                    </h3>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stat.title === 'Mood Score' ? `${stat.value}/10` : stat.completed}
                    </p>
                    {stat.title !== 'Mood Score' && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        of {stat.value} completed
                      </p>
                    )}
                  </motion.div>
                </AnimatedCard>
              ))}
            </div>

            {/* Recent Activity */}
            <AnimatedCard delay={6} className="p-6">
              <motion.div variants={itemVariants}>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Recent Activity
                </h2>
                <div className="space-y-4">
                  {[
                    { text: 'Completed daily meditation habit', time: '2 hours ago', icon: CheckCircle, color: 'green' },
                    { text: 'Updated career goal progress', time: '4 hours ago', icon: Target, color: 'blue' },
                    { text: 'Logged today\'s expenses', time: '6 hours ago', icon: DollarSign, color: 'purple' },
                    { text: 'Recorded mood: Excellent', time: '8 hours ago', icon: Heart, color: 'pink' }
                  ].map((activity, index) => (
                    <motion.div
                      key={index}
                      className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.7 + index * 0.1 }}
                      whileHover={{ scale: 1.02, x: 5 }}
                    >
                      <activity.icon className={`w-5 h-5 ${activity.color === 'green' ? 'text-green-500' : activity.color === 'blue' ? 'text-blue-500' : activity.color === 'purple' ? 'text-purple-500' : 'text-pink-500'}`} />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {activity.text}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {activity.time}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </AnimatedCard>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Dashboard;
