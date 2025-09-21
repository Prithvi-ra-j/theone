/**
 * Mood API Module
 * Handles all mood-related API calls including mood logging and wellness tracking
 */

import api from './client';

const MOOD_BASE_URL = '/mood';

const moodAPI = {
  // Mood Logs
  getMoodLogs: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.mood_score_min) queryParams.append('mood_score_min', params.mood_score_min);
    if (params.mood_score_max) queryParams.append('mood_score_max', params.mood_score_max);
    if (params.energy_level) queryParams.append('energy_level', params.energy_level);
    if (params.stress_level) queryParams.append('stress_level', params.stress_level);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/logs?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/logs`;
    
    return api.get(url);
  },

  getMoodLog: (logId) => 
    api.get(`${MOOD_BASE_URL}/logs/${logId}`),

  // Backend exposes POST /mood/log (singular) for creating a mood entry
  createMoodLog: (moodData) => 
    api.post(`${MOOD_BASE_URL}/log`, moodData),

  updateMoodLog: (logId, moodData) => 
    api.put(`${MOOD_BASE_URL}/logs/${logId}`, moodData),

  deleteMoodLog: (logId) => 
    api.delete(`${MOOD_BASE_URL}/logs/${logId}`),

  // Mood Dashboard
  getMoodDashboard: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date) queryParams.append('date', params.date);
    if (params.period) queryParams.append('period', params.period);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/dashboard?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/dashboard`;
    
    return api.get(url);
  },

  getCurrentMood: () => 
    api.get(`${MOOD_BASE_URL}/current`),

  getMoodTrend: (timeframe = 'week') => 
    api.get(`${MOOD_BASE_URL}/trend?timeframe=${timeframe}`),

  // Mood Analytics
  getMoodAnalytics: (timeframe = 'month', params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.group_by) queryParams.append('group_by', params.group_by);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/analytics?timeframe=${timeframe}&${queryParams.toString()}`
      : `${MOOD_BASE_URL}/analytics?timeframe=${timeframe}`;
    
    return api.get(url);
  },

  getMoodCorrelations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.factor) queryParams.append('factor', params.factor);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.min_correlation) queryParams.append('min_correlation', params.min_correlation);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/correlations?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/correlations`;
    
    return api.get(url);
  },

  getMoodPatterns: (timeframe = 'month') => 
    api.get(`${MOOD_BASE_URL}/patterns?timeframe=${timeframe}`),

  getMoodInsights: (timeframe = 'month') => 
    api.get(`${MOOD_BASE_URL}/insights?timeframe=${timeframe}`),

  // Wellness Tracking
  getWellnessMetrics: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.metric) queryParams.append('metric', params.metric);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/wellness?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/wellness`;
    
    return api.get(url);
  },

  logWellnessMetric: (metricData) => 
    api.post(`${MOOD_BASE_URL}/wellness`, metricData),

  updateWellnessMetric: (metricId, metricData) => 
    api.put(`${MOOD_BASE_URL}/wellness/${metricId}`, metricData),

  deleteWellnessMetric: (metricId) => 
    api.delete(`${MOOD_BASE_URL}/wellness/${metricId}`),

  // Sleep Tracking
  getSleepLogs: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.quality) queryParams.append('quality', params.quality);
    if (params.duration_min) queryParams.append('duration_min', params.duration_min);
    if (params.duration_max) queryParams.append('duration_max', params.duration_max);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/sleep?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/sleep`;
    
    return api.get(url);
  },

  getSleepLog: (logId) => 
    api.get(`${MOOD_BASE_URL}/sleep/${logId}`),

  createSleepLog: (sleepData) => 
    api.post(`${MOOD_BASE_URL}/sleep`, sleepData),

  updateSleepLog: (logId, sleepData) => 
    api.put(`${MOOD_BASE_URL}/sleep/${logId}`, sleepData),

  deleteSleepLog: (logId) => 
    api.delete(`${MOOD_BASE_URL}/sleep/${logId}`),

  getSleepAnalytics: (timeframe = 'month') => 
    api.get(`${MOOD_BASE_URL}/sleep/analytics?timeframe=${timeframe}`),

  // Exercise Tracking
  getExerciseLogs: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.type) queryParams.append('type', params.type);
    if (params.duration_min) queryParams.append('duration_min', params.duration_min);
    if (params.duration_max) queryParams.append('duration_max', params.duration_max);
    if (params.intensity) queryParams.append('intensity', params.intensity);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/exercise?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/exercise`;
    
    return api.get(url);
  },

  getExerciseLog: (logId) => 
    api.get(`${MOOD_BASE_URL}/exercise/${logId}`),

  createExerciseLog: (exerciseData) => 
    api.post(`${MOOD_BASE_URL}/exercise`, exerciseData),

  updateExerciseLog: (logId, exerciseData) => 
    api.put(`${MOOD_BASE_URL}/exercise/${logId}`, exerciseData),

  deleteExerciseLog: (logId) => 
    api.delete(`${MOOD_BASE_URL}/exercise/${logId}`),

  getExerciseAnalytics: (timeframe = 'month') => 
    api.get(`${MOOD_BASE_URL}/exercise/analytics?timeframe=${timeframe}`),

  // Stress Tracking
  getStressLogs: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.level_min) queryParams.append('level_min', params.level_min);
    if (params.level_max) queryParams.append('level_max', params.level_max);
    if (params.trigger) queryParams.append('trigger', params.trigger);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/stress?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/stress`;
    
    return api.get(url);
  },

  getStressLog: (logId) => 
    api.get(`${MOOD_BASE_URL}/stress/${logId}`),

  createStressLog: (stressData) => 
    api.post(`${MOOD_BASE_URL}/stress`, stressData),

  updateStressLog: (logId, stressData) => 
    api.put(`${MOOD_BASE_URL}/stress/${logId}`, stressData),

  deleteStressLog: (logId) => 
    api.delete(`${MOOD_BASE_URL}/stress/${logId}`),

  getStressAnalytics: (timeframe = 'month') => 
    api.get(`${MOOD_BASE_URL}/stress/analytics?timeframe=${timeframe}`),

  // Mood Triggers
  getMoodTriggers: () => 
    api.get(`${MOOD_BASE_URL}/triggers`),

  createMoodTrigger: (triggerData) => 
    api.post(`${MOOD_BASE_URL}/triggers`, triggerData),

  updateMoodTrigger: (triggerId, triggerData) => 
    api.put(`${MOOD_BASE_URL}/triggers/${triggerId}`, triggerData),

  deleteMoodTrigger: (triggerId) => 
    api.delete(`${MOOD_BASE_URL}/triggers/${triggerId}`),

  // Mood Goals
  getMoodGoals: () => 
    api.get(`${MOOD_BASE_URL}/goals`),

  getMoodGoal: (goalId) => 
    api.get(`${MOOD_BASE_URL}/goals/${goalId}`),

  createMoodGoal: (goalData) => 
    api.post(`${MOOD_BASE_URL}/goals`, goalData),

  updateMoodGoal: (goalId, goalData) => 
    api.put(`${MOOD_BASE_URL}/goals/${goalId}`, goalData),

  deleteMoodGoal: (goalId) => 
    api.delete(`${MOOD_BASE_URL}/goals/${goalId}`),

  updateGoalProgress: (goalId, progress) => 
    api.patch(`${MOOD_BASE_URL}/goals/${goalId}/progress`, { progress }),

  // Wellness Tips
  getWellnessTips: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.mood_score) queryParams.append('mood_score', params.mood_score);
    if (params.energy_level) queryParams.append('energy_level', params.energy_level);
    if (params.stress_level) queryParams.append('stress_level', params.stress_level);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/tips?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/tips`;
    
    return api.get(url);
  },

  getWellnessTip: (tipId) => 
    api.get(`${MOOD_BASE_URL}/tips/${tipId}`),

  markTipAsHelpful: (tipId) => 
    api.post(`${MOOD_BASE_URL}/tips/${tipId}/helpful`),

  markTipAsNotHelpful: (tipId) => 
    api.post(`${MOOD_BASE_URL}/tips/${tipId}/not-helpful`),

  // AI Mood Insights
  getMoodInsights: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.focus) queryParams.append('focus', params.focus);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/ai-insights?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/ai-insights`;
    
    return api.get(url);
  },

  getPersonalizedAdvice: (context = {}) => 
    api.post(`${MOOD_BASE_URL}/ai-advice`, context),

  getMoodPrediction: (data = {}) => 
    api.post(`${MOOD_BASE_URL}/prediction`, data),

  // Mood Journal
  getMoodJournal: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MOOD_BASE_URL}/journal?${queryParams.toString()}`
      : `${MOOD_BASE_URL}/journal`;
    
    return api.get(url);
  },

  getMoodJournalEntry: (entryId) => 
    api.get(`${MOOD_BASE_URL}/journal/${entryId}`),

  createMoodJournalEntry: (entryData) => 
    api.post(`${MOOD_BASE_URL}/journal`, entryData),

  updateMoodJournalEntry: (entryId, entryData) => 
    api.put(`${MOOD_BASE_URL}/journal/${entryId}`, entryData),

  deleteMoodJournalEntry: (entryId) => 
    api.delete(`${MOOD_BASE_URL}/journal/${entryId}`),

  // Export/Import
  exportMoodData: (format = 'json') => 
    api.download(`${MOOD_BASE_URL}/export?format=${format}`),

  importMoodData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload(`${MOOD_BASE_URL}/import`, formData);
  },

  // Bulk Operations
  bulkUpdateMoodLogs: (logIds, updateData) => 
    api.patch(`${MOOD_BASE_URL}/logs/bulk-update`, { log_ids: logIds, ...updateData }),

  bulkDeleteMoodLogs: (logIds) => 
    api.delete(`${MOOD_BASE_URL}/logs/bulk-delete`, { data: { log_ids: logIds } }),

  bulkLogMood: (moodEntries) => 
    api.post(`${MOOD_BASE_URL}/logs/bulk-create`, { entries: moodEntries }),
};

export default moodAPI;
