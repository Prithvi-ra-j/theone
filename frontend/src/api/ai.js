/**
 * AI API Module
 * Handles all AI-related API calls including career advice, financial tips, and personalized insights
 */

import api from './client';

const AI_BASE_URL = '/ai';

const aiAPI = {
  // Career AI Services
  getCareerAdvice: (query, context = {}) => 
    api.post(`${AI_BASE_URL}/career/advice`, { query, context }),

  getSkillRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_skills) queryParams.append('current_skills', params.current_skills);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.industry) queryParams.append('industry', params.industry);
    if (params.experience_level) queryParams.append('experience_level', params.experience_level);
    if (params.market_demand) queryParams.append('market_demand', params.market_demand);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/career/skills?${queryParams.toString()}`
      : `${AI_BASE_URL}/career/skills`;
    
    return api.get(url);
  },

  getCareerPathRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_role) queryParams.append('current_role', params.current_role);
    if (params.interests) queryParams.append('interests', params.interests);
    if (params.skills) queryParams.append('skills', params.skills);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.industry) queryParams.append('industry', params.industry);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/career/paths?${queryParams.toString()}`
      : `${AI_BASE_URL}/career/paths`;
    
    return api.get(url);
  },

  getInterviewPreparation: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.role) queryParams.append('role', params.role);
    if (params.company) queryParams.append('company', params.company);
    if (params.interview_type) queryParams.append('interview_type', params.interview_type);
    if (params.experience_level) queryParams.append('experience_level', params.experience_level);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/career/interview-prep?${queryParams.toString()}`
      : `${AI_BASE_URL}/career/interview-prep`;
    
    return api.get(url);
  },

  getResumeFeedback: (resumeText, jobDescription = '') => 
    api.post(`${AI_BASE_URL}/career/resume-feedback`, { resume_text: resumeText, job_description: jobDescription }),

  getCoverLetterHelp: (params = {}) => 
    api.post(`${AI_BASE_URL}/career/cover-letter`, params),

  // Financial AI Services
  getFinancialAdvice: (query, context = {}) => 
    api.post(`${AI_BASE_URL}/finance/advice`, { query, context }),

  getBudgetRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.income) queryParams.append('income', params.income);
    if (params.expenses) queryParams.append('expenses', params.expenses);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.lifestyle) queryParams.append('lifestyle', params.lifestyle);
    if (params.risk_tolerance) queryParams.append('risk_tolerance', params.risk_tolerance);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/finance/budget?${queryParams.toString()}`
      : `${AI_BASE_URL}/finance/budget`;
    
    return api.get(url);
  },

  getInvestmentAdvice: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.time_horizon) queryParams.append('time_horizon', params.time_horizon);
    if (params.risk_tolerance) queryParams.append('risk_tolerance', params.risk_tolerance);
    if (params.current_portfolio) queryParams.append('current_portfolio', params.current_portfolio);
    if (params.amount) queryParams.append('amount', params.amount);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/finance/investment?${queryParams.toString()}`
      : `${AI_BASE_URL}/finance/investment`;
    
    return api.get(url);
  },

  getDebtManagementAdvice: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.debts) queryParams.append('debts', params.debts);
    if (params.income) queryParams.append('income', params.income);
    if (params.expenses) queryParams.append('expenses', params.expenses);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/finance/debt-management?${queryParams.toString()}`
      : `${AI_BASE_URL}/finance/debt-management`;
    
    return api.get(url);
  },

  getTaxOptimizationTips: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.income_sources) queryParams.append('income_sources', params.income_sources);
    if (params.deductions) queryParams.append('deductions', params.deductions);
    if (params.investments) queryParams.append('investments', params.investments);
    if (params.filing_status) queryParams.append('filing_status', params.filing_status);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/finance/tax-optimization?${queryParams.toString()}`
      : `${AI_BASE_URL}/finance/tax-optimization`;
    
    return api.get(url);
  },

  // Habit AI Services
  getHabitSuggestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_habits) queryParams.append('current_habits', params.current_habits);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.lifestyle) queryParams.append('lifestyle', params.lifestyle);
    if (params.time_availability) queryParams.append('time_availability', params.time_availability);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/habits/suggestions?${queryParams.toString()}`
      : `${AI_BASE_URL}/habits/suggestions`;
    
    return api.get(url);
  },

  getHabitOptimization: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.habits) queryParams.append('habits', params.habits);
    if (params.success_rate) queryParams.append('success_rate', params.success_rate);
    if (params.challenges) queryParams.append('challenges', params.challenges);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/habits/optimization?${queryParams.toString()}`
      : `${AI_BASE_URL}/habits/optimization`;
    
    return api.get(url);
  },

  getMotivationTips: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.mood) queryParams.append('mood', params.mood);
    if (params.energy_level) queryParams.append('energy_level', params.energy_level);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.challenges) queryParams.append('challenges', params.challenges);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/habits/motivation?${queryParams.toString()}`
      : `${AI_BASE_URL}/habits/motivation`;
    
    return api.get(url);
  },

  // Mood and Wellness AI Services
  getMoodInsights: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.mood_data) queryParams.append('mood_data', params.mood_data);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.factors) queryParams.append('factors', params.factors);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/mood/insights?${queryParams.toString()}`
      : `${AI_BASE_URL}/mood/insights`;
    
    return api.get(url);
  },

  getWellnessRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_state) queryParams.append('current_state', params.current_state);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.constraints) queryParams.append('constraints', params.constraints);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/wellness/recommendations?${queryParams.toString()}`
      : `${AI_BASE_URL}/wellness/recommendations`;
    
    return api.get(url);
  },

  getStressManagementTips: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.stress_level) queryParams.append('stress_level', params.stress_level);
    if (params.triggers) queryParams.append('triggers', params.triggers);
    if (params.coping_mechanisms) queryParams.append('coping_mechanisms', params.coping_mechanisms);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/wellness/stress-management?${queryParams.toString()}`
      : `${AI_BASE_URL}/wellness/stress-management`;
    
    return api.get(url);
  },

  // Personalized AI Services
  getPersonalizedInsights: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.user_context) queryParams.append('user_context', params.user_context);
    if (params.focus_area) queryParams.append('focus_area', params.focus_area);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/personalized/insights?${queryParams.toString()}`
      : `${AI_BASE_URL}/personalized/insights`;
    
    return api.get(url);
  },

  getGoalOptimization: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.progress) queryParams.append('progress', params.progress);
    if (params.constraints) queryParams.append('constraints', params.constraints);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/personalized/goal-optimization?${queryParams.toString()}`
      : `${AI_BASE_URL}/personalized/goal-optimization`;
    
    return api.get(url);
  },

  getLifeBalanceAnalysis: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.life_areas) queryParams.append('life_areas', params.life_areas);
    if (params.scores) queryParams.append('scores', params.scores);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/personalized/life-balance?${queryParams.toString()}`
      : `${AI_BASE_URL}/personalized/life-balance`;
    
    return api.get(url);
  },

  // AI Chat and Conversations
  startAIConversation: (context = {}) => 
    api.post(`${AI_BASE_URL}/conversation/start`, context),

  continueAIConversation: (conversationId, message, context = {}) => 
    api.post(`${AI_BASE_URL}/conversation/${conversationId}/continue`, { message, context }),

  getConversationHistory: (conversationId) => 
    api.get(`${AI_BASE_URL}/conversation/${conversationId}/history`),

  endAIConversation: (conversationId) => 
    api.post(`${AI_BASE_URL}/conversation/${conversationId}/end`),

  // AI Learning and Training
  getLearningRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_knowledge) queryParams.append('current_knowledge', params.current_knowledge);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.learning_style) queryParams.append('learning_style', params.learning_style);
    if (params.time_available) queryParams.append('time_available', params.time_available);
    if (params.preferences) queryParams.append('preferences', params.preferences);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/learning/recommendations?${queryParams.toString()}`
      : `${AI_BASE_URL}/learning/recommendations`;
    
    return api.get(url);
  },

  getStudyPlan: (params = {}) => 
    api.post(`${AI_BASE_URL}/learning/study-plan`, params),

  getPracticeQuestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.topic) queryParams.append('topic', params.topic);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.count) queryParams.append('count', params.count);
    if (params.format) queryParams.append('format', params.format);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/learning/practice-questions?${queryParams.toString()}`
      : `${AI_BASE_URL}/learning/practice-questions`;
    
    return api.get(url);
  },

  // AI Analytics and Insights
  getAIAnalytics: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.metrics) queryParams.append('metrics', params.metrics);
    if (params.group_by) queryParams.append('group_by', params.group_by);
    if (params.filters) queryParams.append('filters', params.filters);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/analytics?${queryParams.toString()}`
      : `${AI_BASE_URL}/analytics`;
    
    return api.get(url);
  },

  getAIInsights: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.data) queryParams.append('data', params.data);
    if (params.insight_type) queryParams.append('insight_type', params.insight_type);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${AI_BASE_URL}/insights?${queryParams.toString()}`
      : `${AI_BASE_URL}/insights`;
    
    return api.get(url);
  },

  // AI Service Status
  getAIServiceStatus: () => 
    api.get(`${AI_BASE_URL}/status`),

  getModelStatus: (modelName = null) => {
    const url = modelName 
      ? `${AI_BASE_URL}/models/${modelName}/status`
      : `${AI_BASE_URL}/models/status`;
    return api.get(url);
  },

  getAvailableModels: () => 
    api.get(`${AI_BASE_URL}/models`),

  // AI Configuration
  updateAIPreferences: (preferences) => 
    api.put(`${AI_BASE_URL}/preferences`, preferences),

  getAIPreferences: () => 
    api.get(`${AI_BASE_URL}/preferences`),

  resetAIPreferences: () => 
    api.delete(`${AI_BASE_URL}/preferences`),

  // AI Testing and Validation
  testAIResponse: (params = {}) => 
    api.post(`${AI_BASE_URL}/test`, params),

  validateAIResponse: (responseId, feedback) => 
    api.post(`${AI_BASE_URL}/validation/${responseId}`, { feedback }),

  getAIResponseQuality: (responseId) => 
    api.get(`${AI_BASE_URL}/quality/${responseId}`),
};

export default aiAPI;
