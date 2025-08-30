/**
 * Authentication API module
 * Handles user authentication, registration, and profile management
 */

import apiClient from './client';

const authAPI = {
  /**
   * User registration
   * @param {Object} userData - User registration data
   * @param {string} userData.name - User's full name
   * @param {string} userData.email - User's email address
   * @param {string} userData.password - User's password
   * @returns {Promise<Object>} Registration response
   */
  async register(userData) {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  /**
   * User login
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.email - User's email address
   * @param {string} credentials.password - User's password
   * @returns {Promise<Object>} Login response with tokens
   */
  async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New access token
   */
  async refreshToken(refreshToken) {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  /**
   * Get current user profile
   * @returns {Promise<Object>} Current user profile
   */
  async getCurrentUserProfile() {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  /**
   * Update user profile
   * @param {Object} profileData - Profile data to update
   * @returns {Promise<Object>} Updated user profile
   */
  async updateUserProfile(profileData) {
    const response = await apiClient.put('/auth/me', profileData);
    return response.data;
  },

  /**
   * Change user password
   * @param {Object} passwordData - Password change data
   * @param {string} passwordData.current_password - Current password
   * @param {string} passwordData.new_password - New password
   * @returns {Promise<Object>} Password change response
   */
  async changePassword(passwordData) {
    const response = await apiClient.post('/auth/change-password', passwordData);
    return response.data;
  },

  /**
   * Request password reset
   * @param {string} email - User's email address
   * @returns {Promise<Object>} Password reset request response
   */
  async requestPasswordReset(email) {
    const response = await apiClient.post('/auth/forgot-password', { email });
    return response.data;
  },

  /**
   * Reset password with token
   * @param {Object} resetData - Password reset data
   * @param {string} resetData.token - Reset token
   * @param {string} resetData.new_password - New password
   * @returns {Promise<Object>} Password reset response
   */
  async resetPassword(resetData) {
    const response = await apiClient.post('/auth/reset-password', resetData);
    return response.data;
  },

  /**
   * Logout user
   * @returns {Promise<Object>} Logout response
   */
  async logout() {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },

  /**
   * Verify email address
   * @param {string} token - Email verification token
   * @returns {Promise<Object>} Email verification response
   */
  async verifyEmail(token) {
    const response = await apiClient.post('/auth/verify-email', { token });
    return response.data;
  },

  /**
   * Resend email verification
   * @returns {Promise<Object>} Resend verification response
   */
  async resendEmailVerification() {
    const response = await apiClient.post('/auth/resend-verification');
    return response.data;
  },

  /**
   * Get user preferences
   * @returns {Promise<Object>} User preferences
   */
  async getUserPreferences() {
    const response = await apiClient.get('/auth/preferences');
    return response.data;
  },

  /**
   * Update user preferences
   * @param {Object} preferences - User preferences to update
   * @returns {Promise<Object>} Updated user preferences
   */
  async updateUserPreferences(preferences) {
    const response = await apiClient.put('/auth/preferences', preferences);
    return response.data;
  },

  /**
   * Delete user account
   * @param {string} password - User's password for confirmation
   * @returns {Promise<Object>} Account deletion response
   */
  async deleteAccount(password) {
    const response = await apiClient.delete('/auth/account', { data: { password } });
    return response.data;
  },

  /**
   * Get user activity log
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   * @returns {Promise<Object>} User activity log
   */
  async getUserActivity(params = {}) {
    const response = await apiClient.get('/auth/activity', { params });
    return response.data;
  },

  /**
   * Update user avatar
   * @param {FormData} avatarData - Avatar image data
   * @returns {Promise<Object>} Avatar update response
   */
  async updateAvatar(avatarData) {
    const response = await apiClient.put('/auth/avatar', avatarData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get user statistics
   * @returns {Promise<Object>} User statistics
   */
  async getUserStats() {
    const response = await apiClient.get('/auth/stats');
    return response.data;
  },

  /**
   * Check if user is authenticated
   * @returns {Promise<boolean>} Authentication status
   */
  async checkAuth() {
    try {
      await apiClient.get('/auth/me');
      return true;
    } catch (error) {
      return false;
    }
  },
};

export default authAPI;
