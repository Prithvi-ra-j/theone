/**
 * Habits API Module
 * Handles all habit-related API calls including habits, tasks, and calendar events
 */

import api from './client';

const HABITS_BASE_URL = '/habits';

const habitsAPI = {
  // Habits
  getHabits: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.category) queryParams.append('category', params.category);
    if (params.frequency) queryParams.append('frequency', params.frequency);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}?${queryParams.toString()}`
      : HABITS_BASE_URL;
    
    return api.get(url);
  },

  getHabit: (habitId) => 
    api.get(`${HABITS_BASE_URL}/${habitId}`),

  createHabit: (habitData) => 
    api.post(HABITS_BASE_URL, habitData),

  updateHabit: (habitId, habitData) => 
    api.put(`${HABITS_BASE_URL}/${habitId}`, habitData),

  deleteHabit: (habitId) => 
    api.delete(`${HABITS_BASE_URL}/${habitId}`),

  completeHabit: (habitId, completionData = {}) => 
    api.post(`${HABITS_BASE_URL}/${habitId}/complete`, completionData),

  skipHabit: (habitId, reason = '') => 
    api.post(`${HABITS_BASE_URL}/${habitId}/skip`, { reason }),

  getHabitCompletions: (habitId, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/${habitId}/completions?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/${habitId}/completions`;
    
    return api.get(url);
  },

  // Tasks
  getTasks: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.category) queryParams.append('category', params.category);
    if (params.due_date) queryParams.append('due_date', params.due_date);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/tasks?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/tasks`;
    
    return api.get(url);
  },

  getTask: (taskId) => 
    api.get(`${HABITS_BASE_URL}/tasks/${taskId}`),

  createTask: (taskData) => 
    api.post(`${HABITS_BASE_URL}/tasks`, taskData),

  updateTask: (taskId, taskData) => 
    api.put(`${HABITS_BASE_URL}/tasks/${taskId}`, taskData),

  deleteTask: (taskId) => 
    api.delete(`${HABITS_BASE_URL}/tasks/${taskId}`),

  updateTaskStatus: (taskId, status) => 
    api.patch(`${HABITS_BASE_URL}/tasks/${taskId}/status`, { status }),

  updateTaskPriority: (taskId, priority) => 
    api.patch(`${HABITS_BASE_URL}/tasks/${taskId}/priority`, { priority }),

  // Calendar Events
  getEvents: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.type) queryParams.append('type', params.type);
    if (params.category) queryParams.append('category', params.category);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/events?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/events`;
    
    return api.get(url);
  },

  getEvent: (eventId) => 
    api.get(`${HABITS_BASE_URL}/events/${eventId}`),

  createEvent: (eventData) => 
    api.post(`${HABITS_BASE_URL}/events`, eventData),

  updateEvent: (eventId, eventData) => 
    api.put(`${HABITS_BASE_URL}/events/${eventId}`, eventData),

  deleteEvent: (eventId) => 
    api.delete(`${HABITS_BASE_URL}/events/${eventId}`),

  // Habits Dashboard
  getHabitsDashboard: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date) queryParams.append('date', params.date);
    if (params.period) queryParams.append('period', params.period);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/dashboard?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/dashboard`;
    
    return api.get(url);
  },

  getTodayHabits: (date = null) => {
    const url = date 
      ? `${HABITS_BASE_URL}/today?date=${date}`
      : `${HABITS_BASE_URL}/today`;
    return api.get(url);
  },

  getUpcomingTasks: (days = 7) => 
    api.get(`${HABITS_BASE_URL}/tasks/upcoming?days=${days}`),

  getUpcomingEvents: (days = 7) => 
    api.get(`${HABITS_BASE_URL}/events/upcoming?days=${days}`),

  // Habit Analytics
  getHabitAnalytics: (habitId, timeframe = 'month') => 
    api.get(`${HABITS_BASE_URL}/${habitId}/analytics?timeframe=${timeframe}`),

  getHabitStreak: (habitId) => 
    api.get(`${HABITS_BASE_URL}/${habitId}/streak`),

  getHabitProgress: (habitId, period = 'week') => 
    api.get(`${HABITS_BASE_URL}/${habitId}/progress?period=${period}`),

  getOverallProgress: (timeframe = 'month') => 
    api.get(`${HABITS_BASE_URL}/progress?timeframe=${timeframe}`),

  // Habit Categories
  getHabitCategories: () => 
    api.get(`${HABITS_BASE_URL}/categories`),

  createHabitCategory: (categoryData) => 
    api.post(`${HABITS_BASE_URL}/categories`, categoryData),

  updateHabitCategory: (categoryId, categoryData) => 
    api.put(`${HABITS_BASE_URL}/categories/${categoryId}`, categoryData),

  deleteHabitCategory: (categoryId) => 
    api.delete(`${HABITS_BASE_URL}/categories/${categoryId}`),

  // Habit Templates
  getHabitTemplates: (category = null) => {
    const url = category 
      ? `${HABITS_BASE_URL}/templates?category=${category}`
      : `${HABITS_BASE_URL}/templates`;
    return api.get(url);
  },

  getHabitTemplate: (templateId) => 
    api.get(`${HABITS_BASE_URL}/templates/${templateId}`),

  createHabitFromTemplate: (templateId, customizations = {}) => 
    api.post(`${HABITS_BASE_URL}/templates/${templateId}/create`, customizations),

  // Habit Reminders
  getHabitReminders: (habitId) => 
    api.get(`${HABITS_BASE_URL}/${habitId}/reminders`),

  createHabitReminder: (habitId, reminderData) => 
    api.post(`${HABITS_BASE_URL}/${habitId}/reminders`, reminderData),

  updateHabitReminder: (habitId, reminderId, reminderData) => 
    api.put(`${HABITS_BASE_URL}/${habitId}/reminders/${reminderId}`, reminderData),

  deleteHabitReminder: (habitId, reminderId) => 
    api.delete(`${HABITS_BASE_URL}/${habitId}/reminders/${reminderId}`),

  // Habit Challenges
  getHabitChallenges: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.category) queryParams.append('category', params.category);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/challenges?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/challenges`;
    
    return api.get(url);
  },

  joinHabitChallenge: (challengeId) => 
    api.post(`${HABITS_BASE_URL}/challenges/${challengeId}/join`),

  leaveHabitChallenge: (challengeId) => 
    api.post(`${HABITS_BASE_URL}/challenges/${challengeId}/leave`),

  // Habit Sharing
  shareHabit: (habitId, shareData) => 
    api.post(`${HABITS_BASE_URL}/${habitId}/share`, shareData),

  getSharedHabits: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.user_id) queryParams.append('user_id', params.user_id);
    if (params.category) queryParams.append('category', params.category);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${HABITS_BASE_URL}/shared?${queryParams.toString()}`
      : `${HABITS_BASE_URL}/shared`;
    
    return api.get(url);
  },

  // Export/Import
  exportHabitsData: (format = 'json') => 
    api.download(`${HABITS_BASE_URL}/export?format=${format}`),

  importHabitsData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload(`${HABITS_BASE_URL}/import`, formData);
  },

  // Bulk Operations
  bulkUpdateHabits: (habitIds, updateData) => 
    api.patch(`${HABITS_BASE_URL}/bulk-update`, { habit_ids: habitIds, ...updateData }),

  bulkDeleteHabits: (habitIds) => 
    api.delete(`${HABITS_BASE_URL}/bulk-delete`, { data: { habit_ids: habitIds } }),

  bulkCompleteHabits: (habitIds, completionData = {}) => 
    api.post(`${HABITS_BASE_URL}/bulk-complete`, { habit_ids: habitIds, ...completionData }),
};

export default habitsAPI;
