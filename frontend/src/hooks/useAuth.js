// /**
//  * Authentication Hook
//  * Manages user authentication state using React Query
//  */

// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// import { useNavigate } from 'react-router-dom';
// import { toast } from 'react-hot-toast';
// import { authAPI } from '../api';
// import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '../api/config';

// export const useAuth = () => {
//   const queryClient = useQueryClient();
//   const navigate = useNavigate();

//   // Get current user profile
//   const {
//     data: user,
//     isLoading: isLoadingUser,
//     error: userError,
//     refetch: refetchUser,
//   } = useQuery({
//     queryKey: ['auth', 'user'],
//     queryFn: authAPI.getProfile,
//     retry: false,
//     staleTime: 5 * 60 * 1000, // 5 minutes
//     gcTime: 10 * 60 * 1000, // 10 minutes
//   });

//   // Check if user is authenticated
//   const isAuthenticated = !!user && !userError;

//   // Login mutation
//   const loginMutation = useMutation({
//     mutationFn: authAPI.login,
//     onSuccess: (data) => {
//       // Store tokens
//       localStorage.setItem('access_token', data.access_token);
//       if (data.refresh_token) {
//         localStorage.setItem('refresh_token', data.refresh_token);
//       }
      
//       // Update user data in cache
//       queryClient.setQueryData(['auth', 'user'], data.user);
      
//       // Invalidate and refetch user data
//       queryClient.invalidateQueries({ queryKey: ['auth', 'user'] });
      
//       toast.success(SUCCESS_MESSAGES.LOGGED_IN);
//       navigate('/dashboard');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Register mutation
//   const registerMutation = useMutation({
//     mutationFn: authAPI.register,
//     onSuccess: (data) => {
//       toast.success('Registration successful! Please check your email to verify your account.');
//       navigate('/login');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Logout mutation
//   const logoutMutation = useMutation({
//     mutationFn: authAPI.logout,
//     onSuccess: () => {
//       // Clear tokens
//       localStorage.removeItem('access_token');
//       localStorage.removeItem('refresh_token');
      
//       // Clear user data from cache
//       queryClient.removeQueries({ queryKey: ['auth', 'user'] });
//       queryClient.clear();
      
//       toast.success('Successfully logged out');
//       navigate('/login');
//     },
//     onError: (error) => {
//       // Even if logout fails, clear local data
//       localStorage.removeItem('access_token');
//       localStorage.removeItem('refresh_token');
//       queryClient.removeQueries({ queryKey: ['auth', 'user'] });
//       queryClient.clear();
      
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//       navigate('/login');
//     },
//   });

//   // Update profile mutation
//   const updateProfileMutation = useMutation({
//     mutationFn: ({ userId, profileData }) => authAPI.updateProfile(userId, profileData),
//     onSuccess: (data) => {
//       // Update user data in cache
//       queryClient.setQueryData(['auth', 'user'], data);
      
//       toast.success(SUCCESS_MESSAGES.PROFILE_UPDATED);
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Change password mutation
//   const changePasswordMutation = useMutation({
//     mutationFn: ({ currentPassword, newPassword }) => 
//       authAPI.changePassword(currentPassword, newPassword),
//     onSuccess: () => {
//       toast.success(SUCCESS_MESSAGES.PASSWORD_CHANGED);
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Forgot password mutation
//   const forgotPasswordMutation = useMutation({
//     mutationFn: authAPI.forgotPassword,
//     onSuccess: () => {
//       toast.success('Password reset email sent. Please check your inbox.');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Reset password mutation
//   const resetPasswordMutation = useMutation({
//     mutationFn: ({ token, newPassword }) => 
//       authAPI.resetPassword(token, newPassword),
//     onSuccess: () => {
//       toast.success('Password successfully reset. Please log in with your new password.');
//       navigate('/login');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Verify email mutation
//   const verifyEmailMutation = useMutation({
//     mutationFn: ({ token }) => authAPI.verifyEmail(token),
//     onSuccess: () => {
//       toast.success('Email verified successfully! You can now log in.');
//       navigate('/login');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Update preferences mutation
//   const updatePreferencesMutation = useMutation({
//     mutationFn: (preferences) => authAPI.updatePreferences(preferences),
//     onSuccess: (data) => {
//       // Update user data in cache
//       queryClient.setQueryData(['auth', 'user'], (oldData) => ({
//         ...oldData,
//         preferences: data.preferences,
//       }));
      
//       toast.success('Preferences updated successfully');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Delete account mutation
//   const deleteAccountMutation = useMutation({
//     mutationFn: ({ password, reason }) => authAPI.deleteAccount(password, reason),
//     onSuccess: () => {
//       // Clear all data
//       localStorage.removeItem('access_token');
//       localStorage.removeItem('refresh_token');
//       queryClient.removeQueries({ queryKey: ['auth', 'user'] });
//       queryClient.clear();
      
//       toast.success('Account deleted successfully');
//       navigate('/login');
//     },
//     onError: (error) => {
//       const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
//       toast.error(message);
//     },
//   });

//   // Get activity logs
//   const {
//     data: activityLogs,
//     isLoading: isLoadingActivityLogs,
//     error: activityLogsError,
//   } = useQuery({
//     queryKey: ['auth', 'activity-logs'],
//     queryFn: authAPI.getActivityLogs,
//     enabled: isAuthenticated,
//     staleTime: 2 * 60 * 1000, // 2 minutes
//   });

//   // Get user stats
//   const {
//     data: userStats,
//     isLoading: isLoadingUserStats,
//     error: userStatsError,
//   } = useQuery({
//     queryKey: ['auth', 'user-stats'],
//     queryFn: authAPI.getUserStats,
//     enabled: isAuthenticated,
//     staleTime: 5 * 60 * 1000, // 5 minutes
//   });

//   return {
//     // User data
//     user,
//     isLoadingUser,
//     userError,
//     isAuthenticated,
    
//     // Activity logs
//     activityLogs,
//     isLoadingActivityLogs,
//     activityLogsError,
    
//     // User stats
//     userStats,
//     isLoadingUserStats,
//     userStatsError,
    
//     // Mutations
//     login: loginMutation.mutate,
//     loginAsync: loginMutation.mutateAsync,
//     isLoggingIn: loginMutation.isPending,
    
//     register: registerMutation.mutate,
//     registerAsync: registerMutation.mutateAsync,
//     isRegistering: registerMutation.isPending,
    
//     logout: logoutMutation.mutate,
//     logoutAsync: logoutMutation.mutateAsync,
//     isLoggingOut: logoutMutation.isPending,
    
//     updateProfile: updateProfileMutation.mutate,
//     updateProfileAsync: updateProfileMutation.mutateAsync,
//     isUpdatingProfile: updateProfileMutation.isPending,
    
//     changePassword: changePasswordMutation.mutate,
//     changePasswordAsync: changePasswordMutation.mutateAsync,
//     isChangingPassword: changePasswordMutation.isPending,
    
//     forgotPassword: forgotPasswordMutation.mutate,
//     forgotPasswordAsync: forgotPasswordMutation.mutateAsync,
//     isForgotPasswordPending: forgotPasswordMutation.isPending,
    
//     resetPassword: resetPasswordMutation.mutate,
//     resetPasswordAsync: resetPasswordMutation.mutateAsync,
//     isResettingPassword: resetPasswordMutation.isPending,
    
//     verifyEmail: verifyEmailMutation.mutate,
//     verifyEmailAsync: verifyEmailMutation.mutateAsync,
//     isVerifyingEmail: verifyEmailMutation.isPending,
    
//     updatePreferences: updatePreferencesMutation.mutate,
//     updatePreferencesAsync: updatePreferencesMutation.mutateAsync,
//     isUpdatingPreferences: updatePreferencesMutation.isPending,
    
//     deleteAccount: deleteAccountMutation.mutate,
//     deleteAccountAsync: deleteAccountMutation.mutateAsync,
//     isDeletingAccount: deleteAccountMutation.isPending,
    
//     // Utilities
//     refetchUser,
//   };
// };
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const isAuthenticated = !!user;

  // Login removed for prototype — app shows dashboard without auth

  const logout = () => {
    setUser(null);
    navigate('/login');
  };

  return {
    user,
    isAuthenticated,
    logout,
  };
};
