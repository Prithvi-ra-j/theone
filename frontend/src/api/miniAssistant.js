/**
 * Mini Assistant API Client
 * Handles all API calls related to the Mini Assistant feature
 */

import api from './client';

const miniAssistantAPI = {
  // Get the current user's mini assistant
  getMiniAssistant: () => api.get('/mini-assistant'),

  // Create a new mini assistant
  createMiniAssistant: (data) => api.post('/mini-assistant', data),

  // Update an existing mini assistant
  updateMiniAssistant: (data) => api.put('/mini-assistant', data),

  // Get all interactions for the mini assistant
  getInteractions: () => api.get('/mini-assistant/interactions'),

  // Create a new interaction
  createInteraction: (data) => api.post('/mini-assistant/interactions', data),

  // Mark interactions as read
  markInteractionsAsRead: () => api.post('/mini-assistant/interactions/read'),

  // Bulk delete interactions
  bulkDeleteInteractions: (ids) => api.post('/mini-assistant/interactions/bulk-delete', { ids }),

  // Delete all interactions
  deleteAllInteractions: () => api.post('/mini-assistant/interactions/delete-all'),

  // Tools
  listTools: () => api.get('/mini-assistant/tools'),
  executeTool: (tool, params) => api.post('/mini-assistant/tools/execute', { tool, params }),
};

export default miniAssistantAPI;