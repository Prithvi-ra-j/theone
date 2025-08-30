/**
 * Career API Module
 * Handles all career-related API calls including goals, skills, and learning paths
 */

import api from './client';

const CAREER_BASE_URL = '/career';

const careerAPI = {
  // Career Goals
  getCareerGoals: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/goals?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/goals`;
    
    return api.get(url);
  },

  getCareerGoal: (goalId) => 
    api.get(`${CAREER_BASE_URL}/goals/${goalId}`),

  createCareerGoal: (goalData) => 
    api.post(`${CAREER_BASE_URL}/goals`, goalData),

  updateCareerGoal: (goalId, goalData) => 
    api.put(`${CAREER_BASE_URL}/goals/${goalId}`, goalData),

  deleteCareerGoal: (goalId) => 
    api.delete(`${CAREER_BASE_URL}/goals/${goalId}`),

  updateGoalProgress: (goalId, progress) => 
    api.patch(`${CAREER_BASE_URL}/goals/${goalId}/progress`, { progress }),

  // Skills
  getSkills: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.level) queryParams.append('level', params.level);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/skills?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/skills`;
    
    return api.get(url);
  },

  getSkill: (skillId) => 
    api.get(`${CAREER_BASE_URL}/skills/${skillId}`),

  createSkill: (skillData) => 
    api.post(`${CAREER_BASE_URL}/skills`, skillData),

  updateSkill: (skillId, skillData) => 
    api.put(`${CAREER_BASE_URL}/skills/${skillId}`, skillData),

  deleteSkill: (skillId) => 
    api.delete(`${CAREER_BASE_URL}/skills/${skillId}`),

  updateSkillLevel: (skillId, level) => 
    api.patch(`${CAREER_BASE_URL}/skills/${skillId}/level`, { level }),

  // Learning Paths
  getLearningPaths: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.category) queryParams.append('category', params.category);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/learning-paths?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/learning-paths`;
    
    return api.get(url);
  },

  getLearningPath: (pathId) => 
    api.get(`${CAREER_BASE_URL}/learning-paths/${pathId}`),

  createLearningPath: (pathData) => 
    api.post(`${CAREER_BASE_URL}/learning-paths`, pathData),

  updateLearningPath: (pathId, pathData) => 
    api.put(`${CAREER_BASE_URL}/learning-paths/${pathId}`, pathData),

  deleteLearningPath: (pathId) => 
    api.delete(`${CAREER_BASE_URL}/learning-paths/${pathId}`),

  updatePathProgress: (pathId, progress) => 
    api.patch(`${CAREER_BASE_URL}/learning-paths/${pathId}/progress`, { progress }),

  // Career Dashboard
  getCareerDashboard: () => 
    api.get(`${CAREER_BASE_URL}/dashboard`),

  // AI Recommendations
  getSkillRecommendations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.current_skills) queryParams.append('current_skills', params.current_skills);
    if (params.industry) queryParams.append('industry', params.industry);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/recommendations/skills?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/recommendations/skills`;
    
    return api.get(url);
  },

  getCareerAdvice: (query, context = {}) => 
    api.post(`${CAREER_BASE_URL}/advice`, { query, context }),

  // Career Analytics
  getCareerAnalytics: (timeframe = 'month') => 
    api.get(`${CAREER_BASE_URL}/analytics?timeframe=${timeframe}`),

  getGoalProgressHistory: (goalId, timeframe = 'month') => 
    api.get(`${CAREER_BASE_URL}/goals/${goalId}/progress-history?timeframe=${timeframe}`),

  getSkillGrowthTrend: (skillId, timeframe = 'month') => 
    api.get(`${CAREER_BASE_URL}/skills/${skillId}/growth-trend?timeframe=${timeframe}`),

  // Career Resources
  getCareerResources: (category = null) => {
    const url = category 
      ? `${CAREER_BASE_URL}/resources?category=${category}`
      : `${CAREER_BASE_URL}/resources`;
    return api.get(url);
  },

  getResource: (resourceId) => 
    api.get(`${CAREER_BASE_URL}/resources/${resourceId}`),

  // Career Networking
  getCareerConnections: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.industry) queryParams.append('industry', params.industry);
    if (params.location) queryParams.append('location', params.location);
    if (params.expertise) queryParams.append('expertise', params.expertise);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/connections?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/connections`;
    
    return api.get(url);
  },

  connectWithUser: (userId, message = '') => 
    api.post(`${CAREER_BASE_URL}/connections`, { user_id: userId, message }),

  // Career Events
  getCareerEvents: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.type) queryParams.append('type', params.type);
    if (params.location) queryParams.append('location', params.location);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${CAREER_BASE_URL}/events?${queryParams.toString()}`
      : `${CAREER_BASE_URL}/events`;
    
    return api.get(url);
  },

  registerForEvent: (eventId) => 
    api.post(`${CAREER_BASE_URL}/events/${eventId}/register`),

  // Career Assessment
  takeCareerAssessment: (assessmentData) => 
    api.post(`${CAREER_BASE_URL}/assessment`, assessmentData),

  getAssessmentResults: (assessmentId) => 
    api.get(`${CAREER_BASE_URL}/assessment/${assessmentId}/results`),

  // Career Planning
  createCareerPlan: (planData) => 
    api.post(`${CAREER_BASE_URL}/plan`, planData),

  getCareerPlan: (planId) => 
    api.get(`${CAREER_BASE_URL}/plan/${planId}`),

  updateCareerPlan: (planId, planData) => 
    api.put(`${CAREER_BASE_URL}/plan/${planId}`, planData),

  deleteCareerPlan: (planId) => 
    api.delete(`${CAREER_BASE_URL}/plan/${planId}`),

  // Export/Import
  exportCareerData: (format = 'json') => 
    api.download(`${CAREER_BASE_URL}/export?format=${format}`),

  importCareerData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload(`${CAREER_BASE_URL}/import`, formData);
  },
};

export default careerAPI;
