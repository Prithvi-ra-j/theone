import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Home, 
  Target, 
  Calendar, 
  DollarSign, 
  Heart, 
  User,
  LogOut,
  Menu,
  X,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Activity,
  MessageSquare,
  BookOpen
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from './ui/ThemeToggle';

import { Outlet } from 'react-router-dom';
import statusAPI from '../api/status';

const Layout = () => {
  const { user, logout } = useAuth();
  const { theme, isDark } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const [isLarge, setIsLarge] = React.useState(false);
  const [collapsed, setCollapsed] = React.useState(false);
  const { data: health } = useQuery({
    queryKey: ['healthz'],
    queryFn: () => statusAPI.getHealth(),
    refetchInterval: 30_000,
  });

  // Track large screens so the sidebar stays open on desktop
  React.useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mq = window.matchMedia('(min-width: 1024px)');
    const handler = (e) => setIsLarge(e.matches);
    // Set initial
    setIsLarge(mq.matches);
    // Add listener (support modern and legacy APIs)
    if (mq.addEventListener) mq.addEventListener('change', handler);
    else mq.addListener(handler);
    return () => {
      if (mq.removeEventListener) mq.removeEventListener('change', handler);
      else mq.removeListener(handler);
    };
  }, []);

  const navigation = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/career', label: 'Career', icon: Target },
    { path: '/reality-check', label: 'Reality Check', icon: Activity },
    { path: '/habits', label: 'Habits', icon: Calendar },
    { path: '/finance', label: 'Finance', icon: DollarSign },
    { path: '/journal', label: 'Journal', icon: BookOpen },
    { path: '/assistant', label: 'Assistant', icon: MessageSquare },
    { path: '/profile', label: 'Profile', icon: User },
  // Animation Demo removed
  ];

  // Mini assistant floating widget removed for now

  const handleLogout = () => {
    logout();
  };

  const sidebarVariants = {
    closed: {
      x: '-100%',
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
    open: {
      x: 0,
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    }
  };

  const overlayVariants = {
    closed: { opacity: 0, pointerEvents: 'none' },
    open: { opacity: 1, pointerEvents: 'auto' }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Dev-only debug badge to verify state and hot reloads */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed top-4 right-4 z-60 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 rounded-md shadow-md px-3 py-2 opacity-90">
          <div className="font-semibold">Layout debug</div>
          <div className="text-xs">isLarge: {isLarge ? 'true' : 'false'}</div>
          <div className="text-xs">collapsed: {collapsed ? 'true' : 'false'}</div>
          <div className="text-xs">sidebarOpen: {sidebarOpen ? 'true' : 'false'}</div>
        </div>
      )}
      {/* Mobile sidebar overlay */}
      <motion.div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
        variants={overlayVariants}
        initial="closed"
        animate={sidebarOpen ? "open" : "closed"}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      {
        /* Keep sidebar visible on large screens by combining the media query state with sidebarOpen */
      }
      <motion.aside
          // Sidebar is fixed on large screens so it stays pinned to the left
          className={`z-50 ${collapsed ? 'w-20' : 'w-64'} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform lg:fixed lg:top-0 lg:left-0 lg:h-full lg:inset-y-0`}
          role="navigation"
          aria-label="Main navigation"
        variants={sidebarVariants}
        initial={sidebarOpen || isLarge ? 'open' : 'closed'}
        animate={sidebarOpen || isLarge ? 'open' : 'closed'}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <motion.div
            className="flex items-center space-x-2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">D</span>
            </div>
            {/* Show title only when not collapsed */}
            {!collapsed && <span className="text-xl font-bold text-gray-900 dark:text-white">Dristhi</span>}
            {!collapsed && (
              <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${health?.db && health?.ai?.available ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`} title="System health">
                {health?.ai?.model || 'no-ai'} · {health?.db ? 'db' : 'no-db'}
              </span>
            )}
          </motion.div>
          
          <div className="flex items-center space-x-2">
            {/* Collapse toggle visible on large screens */}
            <button
              onClick={() => setCollapsed((s) => !s)}
              className="hidden lg:inline-flex p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
            </button>

            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <nav className={`mt-8 ${collapsed ? 'px-2' : 'px-6'}`} aria-label="Primary">
          <ul className={collapsed ? 'space-y-2 text-sm' : 'space-y-2'}>
            {navigation.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center space-x-3 w-full p-2 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 ${location.pathname === item.path ? 'bg-gray-100 dark:bg-gray-700 font-semibold' : ''}`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  {!collapsed && <span className="text-sm">{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
          {/* Assistant setup CTA removed for now */}
        </nav>

    <div className="absolute bottom-6 left-6 right-6">
          <div className="flex items-center justify-between mb-4">
            <ThemeToggle />
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
          
          {user && (
            <motion.div
              className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user.name || user.email}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user.email}
              </p>
            </motion.div>
          )}
        </div>
      </motion.aside>

  {/* Main content */}
  <div className={`${collapsed ? 'lg:pl-20' : 'lg:pl-64'}`}>
        {/* Top bar */}
        <motion.header
          className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 lg:hidden"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">D</span>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Page content */}
        <main className="min-h-screen p-4 md:p-6 max-w-7xl mx-auto">
          <Outlet />
        </main>
      </div>
      
  {/* Floating mini assistant removed for now */}
    </div>
  );
};

export default Layout;
