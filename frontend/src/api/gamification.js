/**
 * Gamification API Module
 * Handles all gamification-related API calls including badges, achievements, user stats, and leaderboards
 */

import api from './client';

const GAMIFICATION_BASE_URL = '/gamification';

const gamificationAPI = {
  // Badges
  getBadges: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.rarity) queryParams.append('rarity', params.rarity);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/badges?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/badges`;
    
    return api.get(url);
  },

  getBadge: (badgeId) => 
    api.get(`${GAMIFICATION_BASE_URL}/badges/${badgeId}`),

  getUserBadges: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/badges`
      : `${GAMIFICATION_BASE_URL}/badges/earned`;
    return api.get(url);
  },

  awardBadge: (userId, badgeId, reason = '') => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/badges`, { badge_id: badgeId, reason }),

  revokeBadge: (userId, badgeId, reason = '') => 
    api.delete(`${GAMIFICATION_BASE_URL}/users/${userId}/badges/${badgeId}`, { data: { reason } }),

  // User Stats
  getUserStats: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/stats`
      : `${GAMIFICATION_BASE_URL}/stats`;
    return api.get(url);
  },

  updateUserStats: (userId, statsData) => 
    api.patch(`${GAMIFICATION_BASE_URL}/users/${userId}/stats`, statsData),

  awardXP: (userId, amount, reason = '') => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/xp`, { amount, reason }),

  getXPHistory: (userId = null, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.reason) queryParams.append('reason', params.reason);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const baseUrl = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/xp/history`
      : `${GAMIFICATION_BASE_URL}/xp/history`;
    
    const url = queryParams.toString() 
      ? `${baseUrl}?${queryParams.toString()}`
      : baseUrl;
    
    return api.get(url);
  },

  // Achievements
  getAchievements: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.append('category', params.category);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.status) queryParams.append('status', params.status);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/achievements?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/achievements`;
    
    return api.get(url);
  },

  getAchievement: (achievementId) => 
    api.get(`${GAMIFICATION_BASE_URL}/achievements/${achievementId}`),

  getUserAchievements: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/achievements`
      : `${GAMIFICATION_BASE_URL}/achievements/earned`;
    return api.get(url);
  },

  unlockAchievement: (userId, achievementId) => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/achievements`, { achievement_id: achievementId }),

  // Levels and Progression
  getUserLevel: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/level`
      : `${GAMIFICATION_BASE_URL}/level`;
    return api.get(url);
  },

  getLevelProgress: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/level/progress`
      : `${GAMIFICATION_BASE_URL}/level/progress`;
    return api.get(url);
  },

  getLevelRewards: (level) => 
    api.get(`${GAMIFICATION_BASE_URL}/levels/${level}/rewards`),

  claimLevelReward: (userId, level, rewardId) => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/levels/${level}/rewards/${rewardId}/claim`),

  // Streaks
  getUserStreaks: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/streaks`
      : `${GAMIFICATION_BASE_URL}/streaks`;
    return api.get(url);
  },

  getStreakHistory: (userId = null, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.type) queryParams.append('type', params.type);
    if (params.date_from) queryParams.append('date_from', params.date_from);
    if (params.date_to) queryParams.append('date_to', params.date_to);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const baseUrl = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/streaks/history`
      : `${GAMIFICATION_BASE_URL}/streaks/history`;
    
    const url = queryParams.toString() 
      ? `${baseUrl}?${queryParams.toString()}`
      : baseUrl;
    
    return api.get(url);
  },

  // Challenges
  getChallenges: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.category) queryParams.append('category', params.category);
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/challenges?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/challenges`;
    
    return api.get(url);
  },

  getChallenge: (challengeId) => 
    api.get(`${GAMIFICATION_BASE_URL}/challenges/${challengeId}`),

  joinChallenge: (challengeId) => 
    api.post(`${GAMIFICATION_BASE_URL}/challenges/${challengeId}/join`),

  leaveChallenge: (challengeId) => 
    api.post(`${GAMIFICATION_BASE_URL}/challenges/${challengeId}/leave`),

  getChallengeProgress: (challengeId) => 
    api.get(`${GAMIFICATION_BASE_URL}/challenges/${challengeId}/progress`),

  updateChallengeProgress: (challengeId, progressData) => 
    api.patch(`${GAMIFICATION_BASE_URL}/challenges/${challengeId}/progress`, progressData),

  // Leaderboards
  getLeaderboard: (type, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.timeframe) queryParams.append('timeframe', params.timeframe);
    if (params.category) queryParams.append('category', params.category);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/leaderboards/${type}?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/leaderboards/${type}`;
    
    return api.get(url);
  },

  getUserLeaderboardPosition: (type, userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/leaderboards/${type}/users/${userId}/position`
      : `${GAMIFICATION_BASE_URL}/leaderboards/${type}/position`;
    return api.get(url);
  },

  // Quests
  getQuests: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.type) queryParams.append('type', params.type);
    if (params.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params.category) queryParams.append('category', params.category);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/quests?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/quests`;
    
    return api.get(url);
  },

  getQuest: (questId) => 
    api.get(`${GAMIFICATION_BASE_URL}/quests/${questId}`),

  acceptQuest: (questId) => 
    api.post(`${GAMIFICATION_BASE_URL}/quests/${questId}/accept`),

  abandonQuest: (questId) => 
    api.post(`${GAMIFICATION_BASE_URL}/quests/${questId}/abandon`),

  completeQuest: (questId, completionData = {}) => 
    api.post(`${GAMIFICATION_BASE_URL}/quests/${questId}/complete`, completionData),

  getQuestProgress: (questId) => 
    api.get(`${GAMIFICATION_BASE_URL}/quests/${questId}/progress`),

  updateQuestProgress: (questId, progressData) => 
    api.patch(`${GAMIFICATION_BASE_URL}/quests/${questId}/progress`, progressData),

  // Rewards
  getRewards: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.type) queryParams.append('type', params.type);
    if (params.category) queryParams.append('category', params.category);
    if (params.rarity) queryParams.append('rarity', params.rarity);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/rewards?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/rewards`;
    
    return api.get(url);
  },

  getReward: (rewardId) => 
    api.get(`${GAMIFICATION_BASE_URL}/rewards/${rewardId}`),

  getUserRewards: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/rewards`
      : `${GAMIFICATION_BASE_URL}/rewards/earned`;
    return api.get(url);
  },

  claimReward: (userId, rewardId) => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/rewards/${rewardId}/claim`),

  // Gamification Dashboard
  getGamificationDashboard: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/dashboard`
      : `${GAMIFICATION_BASE_URL}/dashboard`;
    return api.get(url);
  },

  // Analytics
  getGamificationAnalytics: (timeframe = 'month', params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.user_id) queryParams.append('user_id', params.user_id);
    if (params.metric) queryParams.append('metric', params.metric);
    if (params.group_by) queryParams.append('group_by', params.group_by);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/analytics?timeframe=${timeframe}&${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/analytics?timeframe=${timeframe}`;
    
    return api.get(url);
  },

  // Events and Milestones
  getMilestones: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.type) queryParams.append('type', params.type);
    if (params.status) queryParams.append('status', params.status);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = queryParams.toString() 
      ? `${GAMIFICATION_BASE_URL}/milestones?${queryParams.toString()}`
      : `${GAMIFICATION_BASE_URL}/milestones`;
    
    return api.get(url);
  },

  getMilestone: (milestoneId) => 
    api.get(`${GAMIFICATION_BASE_URL}/milestones/${milestoneId}`),

  getUserMilestones: (userId = null) => {
    const url = userId 
      ? `${GAMIFICATION_BASE_URL}/users/${userId}/milestones`
      : `${GAMIFICATION_BASE_URL}/milestones/achieved`;
    return api.get(url);
  },

  // Export/Import
  exportGamificationData: (format = 'json') => 
    api.download(`${GAMIFICATION_BASE_URL}/export?format=${format}`),

  importGamificationData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload(`${GAMIFICATION_BASE_URL}/import`, formData);
  },

  // Bulk Operations
  bulkAwardBadges: (userIds, badgeId, reason = '') => 
    api.post(`${GAMIFICATION_BASE_URL}/badges/bulk-award`, { user_ids: userIds, badge_id: badgeId, reason }),

  bulkAwardXP: (userIds, amount, reason = '') => 
    api.post(`${GAMIFICATION_BASE_URL}/xp/bulk-award`, { user_ids: userIds, amount, reason }),

  resetUserProgress: (userId, confirm = false) => 
    api.post(`${GAMIFICATION_BASE_URL}/users/${userId}/reset`, { confirm }),
};

export default gamificationAPI;
