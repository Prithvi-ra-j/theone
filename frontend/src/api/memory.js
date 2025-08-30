/**
 * Memory API Module
 * Handles all memory-related API calls including user memory, embeddings, and AI personalization
 */

import api from './client';

const MEMORY_BASE_URL = '/memory';

const memoryAPI = {
  // User Memory
  getUserMemories: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.importance) queryParams.append('importance', params.importance);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}?${queryParams.toString()}`
      : MEMORY_BASE_URL;
    
    return api.get(url);
  },

  getUserMemory: (memoryId) => 
    api.get(`${MEMORY_BASE_URL}/${memoryId}`),

  createUserMemory: (memoryData) => 
    api.post(MEMORY_BASE_URL, memoryData),

  updateUserMemory: (memoryId, memoryData) => 
    api.put(`${MEMORY_BASE_URL}/${memoryId}`, memoryData),

  deleteUserMemory: (memoryId) => 
    api.delete(`${MEMORY_BASE_URL}/${memoryId}`),

  // Memory Search
  searchMemories: (query, params = {}) => {
    const queryParams = new URLSearchParams();
    queryParams.append('query', query);
    if (params.category) queryParams.append('category', params.category);
    if (params.importance) queryParams.append('importance', params.importance);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.similarity_threshold) queryParams.append('similarity_threshold', params.similarity_threshold);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = `${MEMORY_BASE_URL}/search?${queryParams.toString()}`;
    return api.get(url);
  },

  searchMemoriesSemantic: (query, params = {}) => {
    const queryParams = new URLSearchParams();
    queryParams.append('query', query);
    if (params.category) queryParams.append('category', params.category);
    if (params.importance) queryParams.append('importance', params.importance);
    if (params.similarity_threshold) queryParams.append('similarity_threshold', params.similarity_threshold);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = `${MEMORY_BASE_URL}/search/semantic?${queryParams.toString()}`;
    return api.get(url);
  },

  // User Context
  getUserContext: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.categories) queryParams.append('categories', params.categories);
    if (params.include_patterns) queryParams.append('include_patterns', params.include_patterns);
    if (params.include_preferences) queryParams.append('include_preferences', params.include_preferences);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/context?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/context`;
    
    return api.get(url);
  },

  getAggregatedContext: (timeframe = 'month') => 
    api.get(`${MEMORY_BASE_URL}/context/aggregated?timeframe=${timeframe}`),

  getUserPatterns: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.pattern_type) queryParams.append('pattern_type', params.pattern_type);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.confidence_threshold) queryParams.append('confidence_threshold', params.confidence_threshold);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/patterns?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/patterns`;
    
    return api.get(url);
  },

  // User Preferences
  getUserPreferences: () => 
    api.get(`${MEMORY_BASE_URL}/preferences`),

  updateUserPreferences: (preferencesData) => 
    api.put(`${MEMORY_BASE_URL}/preferences`, preferencesData),

  updatePreference: (key, value) => 
    api.patch(`${MEMORY_BASE_URL}/preferences/${key}`, { value }),

  resetUserPreferences: () => 
    api.delete(`${MEMORY_BASE_URL}/preferences`),

  // Personalized Suggestions
  getPersonalizedSuggestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.context) queryParams.append('context', params.context);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/suggestions?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/suggestions`;
    
    return api.get(url);
  },

  getHabitSuggestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_habits) queryParams.append('current_habits', params.current_habits);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.lifestyle) queryParams.append('lifestyle', params.lifestyle);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/suggestions/habits?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/suggestions/habits`;
    
    return api.get(url);
  },

  getCareerSuggestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.current_skills) queryParams.append('current_skills', params.current_skills);
    if (params.interests) queryParams.append('interests', params.interests);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.market_trends) queryParams.append('market_trends', params.market_trends);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/suggestions/career?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/suggestions/career`;
    
    return api.get(url);
  },

  getFinancialSuggestions: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.income) queryParams.append('income', params.income);
    if (params.expenses) queryParams.append('expenses', params.expenses);
    if (params.goals) queryParams.append('goals', params.goals);
    if (params.risk_tolerance) queryParams.append('risk_tolerance', params.risk_tolerance);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/suggestions/financial?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/suggestions/financial`;
    
    return api.get(url);
  },

  // Conversation History
  getConversations: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.topic) queryParams.append('topic', params.topic);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/conversations?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/conversations`;
    
    return api.get(url);
  },

  getConversation: (conversationId) => 
    api.get(`${MEMORY_BASE_URL}/conversations/${conversationId}`),

  createConversation: (conversationData) => 
    api.post(`${MEMORY_BASE_URL}/conversations`, conversationData),

  updateConversation: (conversationId, conversationData) => 
    api.put(`${MEMORY_BASE_URL}/conversations/${conversationId}`, conversationData),

  deleteConversation: (conversationId) => 
    api.delete(`${MEMORY_BASE_URL}/conversations/${conversationId}`),

  // Memory Categories
  getMemoryCategories: () => 
    api.get(`${MEMORY_BASE_URL}/categories`),

  createMemoryCategory: (categoryData) => 
    api.post(`${MEMORY_BASE_URL}/categories`, categoryData),

  updateMemoryCategory: (categoryId, categoryData) => 
    api.put(`${MEMORY_BASE_URL}/categories/${categoryId}`, categoryData),

  deleteMemoryCategory: (categoryId) => 
    api.delete(`${MEMORY_BASE_URL}/categories/${categoryId}`),

  // Memory Tags
  getMemoryTags: () => 
    api.get(`${MEMORY_BASE_URL}/tags`),

  createMemoryTag: (tagData) => 
    api.post(`${MEMORY_BASE_URL}/tags`, tagData),

  updateMemoryTag: (tagId, tagData) => 
    api.put(`${MEMORY_BASE_URL}/tags/${tagId}`, tagData),

  deleteMemoryTag: (tagId) => 
    api.delete(`${MEMORY_BASE_URL}/tags/${tagId}`),

  tagMemory: (memoryId, tagIds) => 
    api.post(`${MEMORY_BASE_URL}/${memoryId}/tags`, { tag_ids: tagIds }),

  untagMemory: (memoryId, tagIds) => 
    api.delete(`${MEMORY_BASE_URL}/${memoryId}/tags`, { data: { tag_ids: tagIds } }),

  // Memory Analytics
  getMemoryAnalytics: (timeframe = 'month', params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.group_by) queryParams.append('group_by', params.group_by);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/analytics?timeframe=${timeframe}&${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/analytics?timeframe=${timeframe}`;
    
    return api.get(url);
  },

  getMemoryInsights: (timeframe = 'month') => 
    api.get(`${MEMORY_BASE_URL}/insights?timeframe=${timeframe}`),

  getMemoryTrends: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.trend_type) queryParams.append('trend_type', params.trend_type);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/trends?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/trends`;
    
    return api.get(url);
  },

  // Memory Import/Export
  exportMemories: (format = 'json', params = {}) => {
    const queryParams = new URLSearchParams();
    queryParams.append('format', format);
    if (params.category) queryParams.append('category', params.category);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.include_embeddings) queryParams.append('include_embeddings', params.include_embeddings);
    
    const url = `${MEMORY_BASE_URL}/export?${queryParams.toString()}`;
    return api.download(url);
  },

  importMemories: (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    if (options.overwrite) formData.append('overwrite', options.overwrite);
    if (options.category) formData.append('category', options.category);
    if (options.validate_only) formData.append('validate_only', options.validate_only);
    
    return api.upload(`${MEMORY_BASE_URL}/import`, formData);
  },

  // Memory Service Status
  getMemoryServiceStatus: () => 
    api.get(`${MEMORY_BASE_URL}/status`),

  getEmbeddingStatus: () => 
    api.get(`${MEMORY_BASE_URL}/embeddings/status`),

  reindexMemories: () => 
    api.post(`${MEMORY_BASE_URL}/embeddings/reindex`),

  // Memory Cleanup
  cleanupOldMemories: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.older_than_days) queryParams.append('older_than_days', params.older_than_days);
    if (params.category) queryParams.append('category', params.category);
    if (params.importance_threshold) queryParams.append('importance_threshold', params.importance_threshold);
    if (params.dry_run) queryParams.append('dry_run', params.dry_run);
    
    const url = queryParams.toString() 
      ? `${MEMORY_BASE_URL}/cleanup?${queryParams.toString()}`
      : `${MEMORY_BASE_URL}/cleanup`;
    
    return api.post(url);
  },

  // Bulk Operations
  bulkUpdateMemories: (memoryIds, updateData) => 
    api.patch(`${MEMORY_BASE_URL}/bulk-update`, { memory_ids: memoryIds, ...updateData }),

  bulkDeleteMemories: (memoryIds) => 
    api.delete(`${MEMORY_BASE_URL}/bulk-delete`, { data: { memory_ids: memoryIds } }),

  bulkTagMemories: (memoryIds, tagIds) => 
    api.post(`${MEMORY_BASE_URL}/bulk-tag`, { memory_ids: memoryIds, tag_ids: tagIds }),

  bulkCategorizeMemories: (memoryIds, categoryId) => 
    api.patch(`${MEMORY_BASE_URL}/bulk-categorize`, { memory_ids: memoryIds, category_id: categoryId }),
};

export default memoryAPI;
