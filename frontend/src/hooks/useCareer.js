/**
 * Career Hooks
 * React Query hooks for career-related operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { careerAPI } from '../api';
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from '../api/config';

// Hook for career goals
export const useCareerGoals = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'goals', params],
    queryFn: () => careerAPI.getCareerGoals(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for a single career goal
export const useCareerGoal = (goalId) => {
  return useQuery({
    queryKey: ['career', 'goals', goalId],
    queryFn: () => careerAPI.getCareerGoal(goalId),
    enabled: !!goalId,
    staleTime: 2 * 60 * 1000,
    gcTime: 5 * 60 * 1000,
  });
};

// Hook for creating career goals
export const useCreateCareerGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.createCareerGoal,
    onSuccess: (data) => {
      // Invalidate and refetch career goals
      queryClient.invalidateQueries({ queryKey: ['career', 'goals'] });
      
      // Add new goal to cache
      queryClient.setQueryData(['career', 'goals', data.id], data);
      
      toast.success(SUCCESS_MESSAGES.CREATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating career goals
export const useUpdateCareerGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, goalData }) => careerAPI.updateCareerGoal(goalId, goalData),
    onSuccess: (data, variables) => {
      // Update goal in cache
      queryClient.setQueryData(['career', 'goals', variables.goalId], data);
      
      // Invalidate goals list to refresh any filtered views
      queryClient.invalidateQueries({ queryKey: ['career', 'goals'] });
      
      toast.success(SUCCESS_MESSAGES.UPDATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for deleting career goals
export const useDeleteCareerGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.deleteCareerGoal,
    onSuccess: (data, goalId) => {
      // Remove goal from cache
      queryClient.removeQueries({ queryKey: ['career', 'goals', goalId] });
      
      // Invalidate goals list
      queryClient.invalidateQueries({ queryKey: ['career', 'goals'] });
      
      toast.success(SUCCESS_MESSAGES.DELETED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating goal progress
export const useUpdateGoalProgress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ goalId, progress }) => careerAPI.updateGoalProgress(goalId, progress),
    onSuccess: (data, variables) => {
      // Update goal in cache
      queryClient.setQueryData(['career', 'goals', variables.goalId], data);
      
      // Invalidate goals list
      queryClient.invalidateQueries({ queryKey: ['career', 'goals'] });
      
      toast.success('Progress updated successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for skills
export const useSkills = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'skills', params],
    queryFn: () => careerAPI.getSkills(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Hook for a single skill
export const useSkill = (skillId) => {
  return useQuery({
    queryKey: ['career', 'skills', skillId],
    queryFn: () => careerAPI.getSkill(skillId),
    enabled: !!skillId,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Hook for creating skills
export const useCreateSkill = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.createSkill,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['career', 'skills'] });
      queryClient.setQueryData(['career', 'skills', data.id], data);
      toast.success(SUCCESS_MESSAGES.CREATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating skills
export const useUpdateSkill = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ skillId, skillData }) => careerAPI.updateSkill(skillId, skillData),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['career', 'skills', variables.skillId], data);
      queryClient.invalidateQueries({ queryKey: ['career', 'skills'] });
      toast.success(SUCCESS_MESSAGES.UPDATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for deleting skills
export const useDeleteSkill = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.deleteSkill,
    onSuccess: (data, skillId) => {
      queryClient.removeQueries({ queryKey: ['career', 'skills', skillId] });
      queryClient.invalidateQueries({ queryKey: ['career', 'skills'] });
      toast.success(SUCCESS_MESSAGES.DELETED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating skill level
export const useUpdateSkillLevel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ skillId, level }) => careerAPI.updateSkillLevel(skillId, level),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['career', 'skills', variables.skillId], data);
      queryClient.invalidateQueries({ queryKey: ['career', 'skills'] });
      toast.success('Skill level updated successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for learning paths
export const useLearningPaths = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'learning-paths', params],
    queryFn: () => careerAPI.getLearningPaths(params),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Hook for a single learning path
export const useLearningPath = (pathId) => {
  return useQuery({
    queryKey: ['career', 'learning-paths', pathId],
    queryFn: () => careerAPI.getLearningPath(pathId),
    enabled: !!pathId,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Hook for creating learning paths
export const useCreateLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.createLearningPath,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['career', 'learning-paths'] });
      queryClient.setQueryData(['career', 'learning-paths', data.id], data);
      toast.success(SUCCESS_MESSAGES.CREATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating learning paths
export const useUpdateLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, pathData }) => careerAPI.updateLearningPath(pathId, pathData),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['career', 'learning-paths', variables.pathId], data);
      queryClient.invalidateQueries({ queryKey: ['career', 'learning-paths'] });
      toast.success(SUCCESS_MESSAGES.UPDATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for deleting learning paths
export const useDeleteLearningPath = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.deleteLearningPath,
    onSuccess: (data, pathId) => {
      queryClient.removeQueries({ queryKey: ['career', 'learning-paths', pathId] });
      queryClient.invalidateQueries({ queryKey: ['career', 'learning-paths'] });
      toast.success(SUCCESS_MESSAGES.DELETED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating learning path progress
export const useUpdatePathProgress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, progress }) => careerAPI.updatePathProgress(pathId, progress),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['career', 'learning-paths', variables.pathId], data);
      queryClient.invalidateQueries({ queryKey: ['career', 'learning-paths'] });
      toast.success('Progress updated successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for career dashboard
export const useCareerDashboard = () => {
  return useQuery({
    queryKey: ['career', 'dashboard'],
    queryFn: () => careerAPI.getCareerDashboard(),
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000,
  });
};

// Hook for skill recommendations
export const useSkillRecommendations = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'skill-recommendations', params],
    queryFn: () => careerAPI.getSkillRecommendations(params),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

// Hook for career advice
export const useCareerAdvice = () => {
  return useMutation({
    mutationFn: ({ query, context }) => careerAPI.getCareerAdvice(query, context),
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for career analytics
export const useCareerAnalytics = (timeframe = 'month') => {
  return useQuery({
    queryKey: ['career', 'analytics', timeframe],
    queryFn: () => careerAPI.getCareerAnalytics(timeframe),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for goal progress history
export const useGoalProgressHistory = (goalId, timeframe = 'month') => {
  return useQuery({
    queryKey: ['career', 'goals', goalId, 'progress-history', timeframe],
    queryFn: () => careerAPI.getGoalProgressHistory(goalId, timeframe),
    enabled: !!goalId,
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Hook for skill growth trend
export const useSkillGrowthTrend = (skillId, timeframe = 'month') => {
  return useQuery({
    queryKey: ['career', 'skills', skillId, 'growth-trend', timeframe],
    queryFn: () => careerAPI.getSkillGrowthTrend(skillId, timeframe),
    enabled: !!skillId,
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for career resources
export const useCareerResources = (category = null) => {
  return useQuery({
    queryKey: ['career', 'resources', category],
    queryFn: () => careerAPI.getCareerResources(category),
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
};

// Hook for career connections
export const useCareerConnections = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'connections', params],
    queryFn: () => careerAPI.getCareerConnections(params),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for connecting with users
export const useConnectWithUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, message }) => careerAPI.connectWithUser(userId, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['career', 'connections'] });
      toast.success('Connection request sent successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for career events
export const useCareerEvents = (params = {}) => {
  return useQuery({
    queryKey: ['career', 'events', params],
    queryFn: () => careerAPI.getCareerEvents(params),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for registering for events
export const useRegisterForEvent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.registerForEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['career', 'events'] });
      toast.success('Successfully registered for event');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for career assessment
export const useCareerAssessment = () => {
  return useMutation({
    mutationFn: careerAPI.takeCareerAssessment,
    onSuccess: () => {
      toast.success('Assessment completed successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for assessment results
export const useAssessmentResults = (assessmentId) => {
  return useQuery({
    queryKey: ['career', 'assessment', assessmentId, 'results'],
    queryFn: () => careerAPI.getAssessmentResults(assessmentId),
    enabled: !!assessmentId,
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for career planning
export const useCareerPlan = () => {
  return useQuery({
    queryKey: ['career', 'plan'],
    queryFn: () => careerAPI.getCareerPlan(),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
};

// Hook for creating career plans
export const useCreateCareerPlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.createCareerPlan,
    onSuccess: (data) => {
      queryClient.setQueryData(['career', 'plan'], data);
      toast.success(SUCCESS_MESSAGES.CREATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for updating career plans
export const useUpdateCareerPlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ planId, planData }) => careerAPI.updateCareerPlan(planId, planData),
    onSuccess: (data) => {
      queryClient.setQueryData(['career', 'plan'], data);
      toast.success(SUCCESS_MESSAGES.UPDATED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for deleting career plans
export const useDeleteCareerPlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.deleteCareerPlan,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ['career', 'plan'] });
      toast.success(SUCCESS_MESSAGES.DELETED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for exporting career data
export const useExportCareerData = () => {
  return useMutation({
    mutationFn: ({ format = 'json' }) => careerAPI.exportCareerData(format),
    onSuccess: () => {
      toast.success(SUCCESS_MESSAGES.DOWNLOADED);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};

// Hook for importing career data
export const useImportCareerData = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerAPI.importCareerData,
    onSuccess: () => {
      // Invalidate all career-related queries
      queryClient.invalidateQueries({ queryKey: ['career'] });
      toast.success('Career data imported successfully');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || ERROR_MESSAGES.UNKNOWN_ERROR;
      toast.error(message);
    },
  });
};
