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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
import AIRecommendations from '../components/AIRecommendations';
import OpportunitiesFeed from '../components/OpportunitiesFeed';
import { Flame, Award } from 'lucide-react';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const qc = useQueryClient();
  const { theme, isDark } = useTheme();
  const [timedOut, setTimedOut] = useState(false);

  // Fetch dashboard data
  const { data: careerData, isLoading: careerLoading, isError: careerError, error: careerErrObj } = useQuery({
    queryKey: ['career','dashboard'],
    queryFn: () => careerAPI.getCareerDashboard(),
  });

  const { data: habitsData, isLoading: habitsLoading, isError: habitsError, error: habitsErrObj } = useQuery({
    queryKey: ['habits','dashboard'],
    queryFn: () => habitsAPI.getHabitsDashboard(),
  });

  const { data: financeData, isLoading: financeLoading, isError: financeError, error: financeErrObj } = useQuery({
    queryKey: ['finance','dashboard'],
    queryFn: () => financeAPI.getFinanceDashboard(),
  });

  const { data: moodData, isLoading: moodLoading, isError: moodError, error: moodErrObj } = useQuery({
    queryKey: ['mood','dashboard'],
    queryFn: () => moodAPI.getMoodDashboard(),
  });

  const { data: userStats, isLoading: statsLoading, isError: statsError, error: statsErrObj } = useQuery({
    queryKey: ['gamification','user-stats'],
    queryFn: () => gamificationAPI.getUserStats(),
  });

  // Prepare UI elements; no blocking timeout/error early returns so dashboard always renders
  let dashboardContent = null;

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
    { id: 'wellness', label: 'Wellness', icon: Heart },
    { id: 'finance', label: 'Finance', icon: DollarSign },
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

  // Render main dashboard unconditionally (dashboardContent used for non-blocking states)
  
  // Otherwise, render the main dashboard
  const seedDemo = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/demo/seed', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (!res.ok) throw new Error('Failed to seed demo data');
      return res.json();
    },
    onSuccess: async () => {
      // Refresh key dashboards
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['career','dashboard'] }),
        qc.invalidateQueries({ queryKey: ['habits','dashboard'] }),
        qc.invalidateQueries({ queryKey: ['finance','dashboard'] }),
        qc.invalidateQueries({ queryKey: ['mood','dashboard'] }),
        qc.invalidateQueries({ queryKey: ['gamification','user-stats'] }),
      ]);
    }
  });
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
              
              <div className="flex items-center gap-3">
                <button
                  onClick={() => seedDemo.mutate()}
                  disabled={seedDemo.isPending}
                  className="px-3 py-2 text-sm rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-60"
                  title="Populate demo data"
                >
                  {seedDemo.isPending ? 'Seeding…' : 'Load Demo Data'}
                </button>
              </div>
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
            {/* Overall Progress Card (Overview tab only) */}
            {activeTab === 'overview' && (
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
            )}

            {/* Stats Grid (Overview tab only) */}
            {activeTab === 'overview' && (
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

                    {/* Navigation button for each card */}
                    <div className="mt-4">
                      <button
                        onClick={() => {
                          // navigate to the appropriate page
                          if (stat.title === 'Career Goals') window.location.href = '/career';
                          if (stat.title === 'Daily Habits') window.location.href = '/habits';
                          if (stat.title === 'Financial Goals') window.location.href = '/finance';
                          if (stat.title === 'Mood Score') window.location.href = '/mood';
                        }}
                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                      >
                        View
                      </button>
                    </div>
                  </motion.div>
                </AnimatedCard>
              ))}
            </div>
            )}

            {/* AI Recommendations (Career tab only) */}
            {activeTab === 'career' && (
              <AnimatedCard delay={0} className="p-6">
                <motion.div variants={itemVariants}>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    AI Career Recommendations
                  </h2>
                  <AIRecommendations />
                </motion.div>
              </AnimatedCard>
            )}

            {/* Peer Benchmarking + Opportunities (Career tab) */}
            {activeTab === 'career' && (
              <AnimatedCard delay={1} className="p-6">
                <motion.div variants={itemVariants}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Peer Benchmarking</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Sample cohort estimate based on your profile.</p>
                    </div>
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200">
                      <Award className="w-4 h-4" /> Top 15% in DSA (sample)
                    </div>
                  </div>
                  <div className="mt-2">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Opportunities for you</h3>
                    <OpportunitiesFeed limit={6} />
                  </div>
                </motion.div>
              </AnimatedCard>
            )}

            {/* Recent Activity (Overview tab only) */}
            {activeTab === 'overview' && (
              <AnimatedCard delay={1} className="p-6">
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
            )}

            {/* Career summary (Career tab) */}
            {activeTab === 'career' && (
              <AnimatedCard delay={1} className="p-6">
                <motion.div variants={itemVariants}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Career Summary</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Goals completed: {careerData?.completed_goals || 0} / {careerData?.total_goals || 0}</p>
                    </div>
                    <button className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700" onClick={() => (window.location.href = '/career')}>Go to Career</button>
                  </div>
                </motion.div>
              </AnimatedCard>
            )}

            {/* Wellness summary (Wellness tab - combines Habits + Mood) */}
            {activeTab === 'wellness' && (
              <AnimatedCard delay={0} className="p-6">
                <motion.div variants={itemVariants}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Wellness Summary</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Habits completed today: {habitsData?.completed_habits_today || 0} / {habitsData?.total_habits || 0}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Average mood: {moodData?.average_mood ?? '—'}/10</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Tip: Aim for 2+ key habits daily to boost your mood trend.</p>
                    </div>
                  </div>
                </motion.div>
              </AnimatedCard>
            )}

            {/* Finance summary (Finance tab) */}
            {activeTab === 'finance' && (
              <AnimatedCard delay={0} className="p-6">
                <motion.div variants={itemVariants}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Finance Summary</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Goals completed: {financeData?.completed_goals || 0} / {financeData?.total_goals || 0}</p>
                    </div>
                    <button className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700" onClick={() => (window.location.href = '/finance')}>Go to Finance</button>
                  </div>
                </motion.div>
              </AnimatedCard>
            )}

            {/* (Removed separate Habits/Mood tabs in favor of Wellness) */}

            {/* Achievements summary (Achievements tab) */}
            {activeTab === 'achievements' && (
              <AnimatedCard delay={0} className="p-6">
                <motion.div variants={itemVariants}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Achievements</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Level: {userStats?.level ?? '—'} • XP: {userStats?.xp ?? 0}</p>
                      <div className="mt-3 flex flex-wrap items-center gap-3">
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-200">
                          <Flame className="w-4 h-4" /> Streak: {userStats?.streak_days ?? 0} days
                        </div>
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-200">
                          <Award className="w-4 h-4" /> {userStats?.badges_earned ?? 0} badges
                        </div>
                      </div>
                    </div>
                    <button className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700" onClick={() => (window.location.href = '/achievements')}>View Achievements</button>
                  </div>
                </motion.div>
              </AnimatedCard>
            )}
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Dashboard;
