/**
 * API Configuration
 * Common configuration settings for API calls
 */

// API Configuration Constants
export const API_CONFIG = {
  // Base URLs
  // In production prefer a relative base ('/') so deployed assets call the host's
  // /api/* route (Vercel -> proxy to Render). Only fall back to localhost for
  // local development when no env var is provided.
  BASE_URL: (() => {
    const envBase = import.meta.env.VITE_API_BASE_URL;
    
    if (envBase) return envBase;
    return import.meta.env.MODE === 'production' ? '/' : devDefault;
  })(),
  API_VERSION: 'v1',
  FULL_BASE_URL: (() => {
    const base = import.meta.env.VITE_API_BASE_URL || (import.meta.env.MODE === 'production' ? '/' : 'http://localhost:8000');
    // Ensure no trailing slash
    return `${base.replace(/\/+$/, '')}/api/v1`;
  })(),
  
  // Timeouts
  REQUEST_TIMEOUT: 30000, // 30 seconds
  UPLOAD_TIMEOUT: 120000, // 2 minutes
  DOWNLOAD_TIMEOUT: 60000, // 1 minute
  
  // Retry Configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  
  // Rate Limiting
  RATE_LIMIT_WINDOW: 60000, // 1 minute
  MAX_REQUESTS_PER_WINDOW: 100,
  
  // Cache Configuration
  CACHE_TTL: 5 * 60 * 1000, // 5 minutes
  CACHE_MAX_SIZE: 100,
  
  // File Upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'text/csv',
    'application/json',
    'text/plain'
  ],
  
  // Authentication
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes before expiry
  SESSION_TIMEOUT: 24 * 60 * 60 * 1000, // 24 hours
  
  // Error Handling
  SHOW_ERROR_NOTIFICATIONS: true,
  LOG_ERRORS_TO_CONSOLE: true,
  RETRY_ON_NETWORK_ERROR: true,
  
  // Development
  MOCK_API: import.meta.env.VITE_MOCK_API === 'true',
  DEBUG_MODE: import.meta.env.VITE_DEBUG_MODE === 'true',
  LOG_API_CALLS: import.meta.env.VITE_LOG_API_CALLS === 'true',
};

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    VERIFY_EMAIL: '/auth/verify-email',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    CHANGE_PASSWORD: '/auth/change-password',
    PROFILE: '/auth/me',
    UPDATE_PROFILE: '/auth/me',
    PREFERENCES: '/auth/preferences',
  },
  
  // Career
  CAREER: {
    GOALS: '/career/goals',
    SKILLS: '/career/skills',
    LEARNING_PATHS: '/career/learning-paths',
    DASHBOARD: '/career/dashboard',
    RECOMMENDATIONS: '/career/recommendations',
    ADVICE: '/career/advice',
    ANALYTICS: '/career/analytics',
    RESOURCES: '/career/resources',
    CONNECTIONS: '/career/connections',
    EVENTS: '/career/events',
    ASSESSMENT: '/career/assessment',
    PLAN: '/career/plan',
  },
  
  // Habits
  HABITS: {
    BASE: '/habits',
    TASKS: '/habits/tasks',
    EVENTS: '/habits/events',
    DASHBOARD: '/habits/dashboard',
    TODAY: '/habits/today',
    UPCOMING: '/habits/upcoming',
    ANALYTICS: '/habits/analytics',
    CATEGORIES: '/habits/categories',
    TEMPLATES: '/habits/templates',
    REMINDERS: '/habits/reminders',
    CHALLENGES: '/habits/challenges',
    SHARED: '/habits/shared',
  },
  
  // Finance
  FINANCE: {
    EXPENSES: '/finance/expenses',
    INCOME: '/finance/income',
    BUDGETS: '/finance/budgets',
    GOALS: '/finance/goals',
    DASHBOARD: '/finance/dashboard',
    ANALYTICS: '/finance/analytics',
    CATEGORIES: '/finance/categories',
    RECURRING: '/finance/recurring',
    PLAN: '/finance/plan',
    INVESTMENTS: '/finance/investments',
    DEBTS: '/finance/debts',
    REPORTS: '/finance/reports',
    ADVICE: '/finance/advice',
    RECOMMENDATIONS: '/finance/recommendations',
  },
  
  // Mood
  MOOD: {
    LOGS: '/mood/logs',
    DASHBOARD: '/mood/dashboard',
    CURRENT: '/mood/current',
    TREND: '/mood/trend',
    ANALYTICS: '/mood/analytics',
    WELLNESS: '/mood/wellness',
    SLEEP: '/mood/sleep',
    EXERCISE: '/mood/exercise',
    STRESS: '/mood/stress',
    TRIGGERS: '/mood/triggers',
    GOALS: '/mood/goals',
    TIPS: '/mood/tips',
    AI_INSIGHTS: '/mood/ai-insights',
    JOURNAL: '/mood/journal',
  },
  
  // Gamification
  GAMIFICATION: {
    BADGES: '/gamification/badges',
    ACHIEVEMENTS: '/gamification/achievements',
    STATS: '/gamification/stats',
    XP: '/gamification/xp',
    LEVELS: '/gamification/levels',
    STREAKS: '/gamification/streaks',
    CHALLENGES: '/gamification/challenges',
    LEADERBOARDS: '/gamification/leaderboards',
    QUESTS: '/gamification/quests',
    REWARDS: '/gamification/rewards',
    DASHBOARD: '/gamification/dashboard',
    ANALYTICS: '/gamification/analytics',
    MILESTONES: '/gamification/milestones',
  },
  
  // Memory
  MEMORY: {
    BASE: '/memory',
    SEARCH: '/memory/search',
    CONTEXT: '/memory/context',
    PREFERENCES: '/memory/preferences',
    SUGGESTIONS: '/memory/suggestions',
    CONVERSATIONS: '/memory/conversations',
    CATEGORIES: '/memory/categories',
    TAGS: '/memory/tags',
    ANALYTICS: '/memory/analytics',
    INSIGHTS: '/memory/insights',
    TRENDS: '/memory/trends',
    EXPORT: '/memory/export',
    IMPORT: '/memory/import',
    STATUS: '/memory/status',
    EMBEDDINGS: '/memory/embeddings',
    CLEANUP: '/memory/cleanup',
  },
  
  // AI Services
  AI: {
    CAREER: '/ai/career',
    FINANCE: '/ai/finance',
    HABITS: '/ai/habits',
    MOOD: '/ai/mood',
    WELLNESS: '/ai/wellness',
    PERSONALIZED: '/ai/personalized',
    CONVERSATION: '/ai/conversation',
    LEARNING: '/ai/learning',
    ANALYTICS: '/ai/analytics',
    INSIGHTS: '/ai/insights',
    STATUS: '/ai/status',
    MODELS: '/ai/models',
    PREFERENCES: '/ai/preferences',
    TEST: '/ai/test',
    VALIDATION: '/ai/validation',
    QUALITY: '/ai/quality',
  },
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied. You don\'t have permission for this resource.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  CREATED: 'Successfully created.',
  UPDATED: 'Successfully updated.',
  DELETED: 'Successfully deleted.',
  SAVED: 'Successfully saved.',
  UPLOADED: 'Successfully uploaded.',
  DOWNLOADED: 'Successfully downloaded.',
  LOGGED_IN: 'Successfully logged in.',
  LOGGED_OUT: 'Successfully logged out.',
  PASSWORD_CHANGED: 'Password successfully changed.',
  PROFILE_UPDATED: 'Profile successfully updated.',
};

// Validation Rules
export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 128,
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 100,
  PHONE_REGEX: /^[\+]?[1-9][\d]{0,15}$/,
  URL_REGEX: /^https?:\/\/.+/,
};

// Default Values
export const DEFAULT_VALUES = {
  USER: {
    AVATAR: '/images/default-avatar.png',
    THEME: 'light',
    LANGUAGE: 'en',
    TIMEZONE: 'UTC',
  },
  PAGINATION: {
    PAGE: 1,
    LIMIT: 20,
    SORT_BY: 'created_at',
    SORT_ORDER: 'desc',
  },
  NOTIFICATIONS: {
    EMAIL: true,
    PUSH: true,
    SMS: false,
    IN_APP: true,
  },
};

// Export default configuration
export default API_CONFIG;
