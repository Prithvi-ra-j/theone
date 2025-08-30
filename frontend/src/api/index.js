/**
 * Main API index file
 * Exports all API modules for different features
 */

export { default as authAPI } from './auth';
export { default as careerAPI } from './career';
export { default as habitsAPI } from './habits';
export { default as financeAPI } from './finance';
export { default as moodAPI } from './mood';
export { default as gamificationAPI } from './gamification';
export { default as memoryAPI } from './memory';
export { default as aiAPI } from './ai';

// Re-export common utilities
export { default as apiClient } from './client';
export { default as apiConfig } from './config';
