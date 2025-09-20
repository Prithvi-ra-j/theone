import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Target, 
  Plus, 
  Edit3, 
  Trash2, 
  BookOpen, 
  TrendingUp,
  Calendar,
  CheckCircle,
  Clock,
  Star,
  Filter,
  Search
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { careerAPI } from '../api';
import { mockCareerData } from '../api/mockData';
import { toast } from 'react-hot-toast';
import TaskCard from '../components/ui/TaskCard.jsx';
import ProgressBar from '../components/ui/ProgressBar.jsx';
import Modal from '../components/ui/Modal.jsx';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import Textarea from '../components/ui/Textarea.jsx';
import Select from '../components/ui/Select.jsx';

const Career = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [modalType, setModalType] = useState('goal'); // 'goal', 'skill', 'learning-path'
  
  // Query hooks need to be defined before they're used in the timeout effect
  const { data: initialCareerData = { recent_goals: [], stats: {}, skills: [] }, isLoading: initialLoading, error: initialCareerError } = useQuery({
    queryKey: ['career'],
    queryFn: async () => {
      try {
        const response = await careerAPI.getCareerDashboard();
        return response.data || mockCareerData || { recent_goals: [], stats: {}, skills: [] };
      } catch (error) {
        console.error('Error fetching career dashboard:', error);
        return mockCareerData || { recent_goals: [], stats: {}, skills: [] };
      }
    },
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
  
  const { data: skillsData = { skills: [] }, isLoading: isSkillsLoading, error: skillsQueryError } = useQuery({
    queryKey: ['skills'],
    queryFn: async () => {
      try {
        const response = await careerAPI.getSkills();
        return response.data || { skills: [] };
      } catch (error) {
        console.error('Error fetching skills:', error);
        return { skills: [] };
      }
    },
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
  
  const { data: pathsData = { paths: [] }, isLoading: isPathsLoading, error: pathsQueryError } = useQuery({
    queryKey: ['learning-paths'],
    queryFn: async () => {
      try {
        const response = await careerAPI.getLearningPaths();
        return response.data || { paths: [] };
      } catch (error) {
        console.error('Error fetching learning paths:', error);
        return { paths: [] };
      }
    },
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
  
  // Timeout logic
  const [timedOut, setTimedOut] = React.useState(false);
  React.useEffect(() => {
    if (!(initialLoading || isSkillsLoading || isPathsLoading)) return;
    const timeout = setTimeout(() => setTimedOut(true), 30000);
    return () => clearTimeout(timeout);
  }, [initialLoading, isSkillsLoading, isPathsLoading]);

  if (timedOut) {
    console.error('Career page load timeout: Data did not load within 30 seconds');
    return (
      <div className="flex items-center justify-center min-h-screen bg-yellow-50 dark:bg-yellow-900">
        <div>
          <h2 className="text-xl font-bold text-yellow-700 dark:text-yellow-300">Timeout: Career data did not load within 30 seconds</h2>
          <p className="text-xs text-yellow-600 dark:text-yellow-200">Please check your network or backend server.</p>
        </div>
      </div>
    );
  }
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    search: ''
  });

  const queryClient = useQueryClient();

  // Use the initial queries above as the canonical data sources to avoid duplicate
  // network requests. Map them to the variable names used throughout the file.
  const careerData = initialCareerData;
  const isLoading = initialLoading;
  const isError = initialCareerError;
  const careerErrObj = initialCareerError;

  const skills = (skillsData && skillsData.skills) ? skillsData.skills : [];
  const skillsLoading = isSkillsLoading;
  const skillsError = skillsQueryError;
  const skillsErrObj = skillsQueryError;

  const learningPaths = (pathsData && pathsData.paths) ? pathsData.paths : [];
  const pathsLoading = isPathsLoading;
  const pathsError = pathsQueryError;
  const pathsErrObj = pathsQueryError;

  // Mutations
  const createGoalMutation = useMutation({
    mutationFn: async (formData) => {
      try {
        const response = await careerAPI.createCareerGoal(formData);
        return response;
      } catch (error) {
        // Check if it's a CORS error or network error
        if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
          console.warn('CORS or network error detected, using mock data fallback');
          // Return a mock successful response with the form data
          return { 
            data: { 
              ...formData, 
              id: `mock-${Date.now()}`,
              created_at: new Date().toISOString(),
              status: formData.status || 'in_progress'
            } 
          };
        }
        throw error;
      }
    },
    onSuccess: (response) => {
      // Check if this is mock data (has mock- prefix in ID)
      const isMockData = response.data?.id?.toString().startsWith('mock-');
      
      if (isMockData) {
        // Manually update the query cache with the mock data
        const currentData = queryClient.getQueryData(['career-dashboard']) || { recent_goals: [] };
        queryClient.setQueryData(['career-dashboard'], {
          ...currentData,
          recent_goals: [response.data, ...(currentData.recent_goals || [])]
        });
        toast.success('Goal created in offline mode');
      } else {
        // Normal invalidation for real API responses
        queryClient.invalidateQueries(['career-dashboard']);
        toast.success('Career goal created successfully!');
      }
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create career goal');
      console.error('Error creating goal:', error);
    },
  });

  const updateGoalMutation = useMutation({
    mutationFn: async (formData) => {
      try {
        const response = await careerAPI.updateCareerGoal(formData);
        return response;
      } catch (error) {
        // Check if it's a CORS error or network error
        if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
          console.warn('CORS or network error detected, using mock data fallback');
          // Return a mock successful response with the form data
          return { 
            data: { 
              ...formData,
              updated_at: new Date().toISOString()
            } 
          };
        }
        throw error;
      }
    },
    onSuccess: (response) => {
  // Check if this is mock data (has mock- prefix in ID), keep detection consistent
  const isMockData = response.data?.id?.toString().startsWith('mock-');
      
      if (isMockData) {
        // Manually update the query cache with the mock data
        const currentData = queryClient.getQueryData(['career-dashboard']) || { recent_goals: [] };
        const updatedGoals = currentData.recent_goals?.map(goal => 
          goal.id === response.data.id ? { ...goal, ...response.data } : goal
        ) || [];
        
        queryClient.setQueryData(['career-dashboard'], {
          ...currentData,
          recent_goals: updatedGoals
        });
        toast.success('Goal updated in offline mode');
      } else {
        // Normal invalidation for real API responses
        queryClient.invalidateQueries(['career-dashboard']);
        toast.success('Career goal updated successfully!');
      }
      setIsModalOpen(false);
      setEditingGoal(null);
    },
    onError: (error) => {
      toast.error('Failed to update career goal');
      console.error('Error updating goal:', error);
    },
  });

  const deleteGoalMutation = useMutation({
    mutationFn: careerAPI.deleteCareerGoal,
    onSuccess: () => {
      queryClient.invalidateQueries(['career-dashboard']);
      toast.success('Career goal deleted successfully!');
    },
    onError: (error) => {
      toast.error('Failed to delete career goal');
      console.error('Error deleting goal:', error);
    },
  });

  const createSkillMutation = useMutation({
    mutationFn: careerAPI.createSkill,
    onSuccess: () => {
      queryClient.invalidateQueries(['skills']);
      toast.success('Skill added successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to add skill');
      console.error('Error adding skill:', error);
    },
  });

  const createLearningPathMutation = useMutation({
    mutationFn: careerAPI.createLearningPath,
    onSuccess: () => {
      queryClient.invalidateQueries(['learning-paths']);
      toast.success('Learning path created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create learning path');
      console.error('Error creating learning path:', error);
    },
  });

  const handleCreateNew = (type) => {
    setModalType(type);
    setEditingGoal(null);
    setIsModalOpen(true);
  };

  const handleEdit = (goal) => {
    setEditingGoal(goal);
    setModalType('goal');
    setIsModalOpen(true);
  };

  const handleDelete = (goalId) => {
    if (window.confirm('Are you sure you want to delete this career goal?')) {
      deleteGoalMutation.mutate(goalId);
    }
  };

  const handleSubmit = (formData) => {
    if (modalType === 'goal') {
      if (editingGoal) {
        updateGoalMutation.mutate({ id: editingGoal.id, ...formData });
      } else {
        createGoalMutation.mutate(formData);
      }
    } else if (modalType === 'skill') {
      createSkillMutation.mutate(formData);
    } else if (modalType === 'learning-path') {
      createLearningPathMutation.mutate(formData);
    }
  };

  const filteredGoals = React.useMemo(() => {
    if (!initialCareerData?.recent_goals) return [];
    
    return initialCareerData.recent_goals.filter(goal => {
      const matchesStatus = filters.status === 'all' || goal.status === filters.status;
      const matchesPriority = filters.priority === 'all' || goal.priority === filters.priority;
      const matchesSearch = filters.search === '' || 
        goal.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        goal.description?.toLowerCase().includes(filters.search.toLowerCase());
      
      return matchesStatus && matchesPriority && matchesSearch;
    });
  }, [careerData?.recent_goals, filters]);

  // Error logging and error UI
  if (initialCareerError || skillsQueryError || pathsQueryError) {
    console.error('Career page load error:', {
      career: initialCareerError,
      skills: skillsQueryError,
      learningPaths: pathsQueryError,
    });
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50 dark:bg-red-900">
        <div>
          <h2 className="text-xl font-bold text-red-700 dark:text-red-300">Error loading career data</h2>
          <pre className="text-xs text-red-600 dark:text-red-200">
            {JSON.stringify({
              career: initialCareerError?.message,
              skills: skillsQueryError?.message,
              learningPaths: pathsQueryError?.message,
            }, null, 2)}
          </pre>
        </div>
      </div>
    );
  }
  if (initialLoading || isSkillsLoading || isPathsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Career Development</h1>
                <p className="mt-2 text-gray-600">
                  Set goals, track skills, and plan your learning journey.
                </p>
              </div>
              <div className="flex space-x-3">
                <Button
                  onClick={() => handleCreateNew('goal')}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Goal</span>
                </Button>
                <Button
                  onClick={() => handleCreateNew('skill')}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Skill</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Goals</p>
                <p className="text-2xl font-bold text-gray-900">
                  {careerData?.total_goals || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-green-50 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {careerData?.completed_goals || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-purple-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Overall Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {careerData?.total_goals > 0 
                    ? Math.round((careerData.completed_goals / careerData.total_goals) * 100)
                    : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search goals..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>
            <Select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Status</option>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="on_hold">On Hold</option>
            </Select>
            <Select
              value={filters.priority}
              onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Priority</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </Select>
          </div>
        </div>

        {/* Goals Section */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Career Goals</h2>
          </div>
          <div className="p-6">
            {filteredGoals.length === 0 ? (
              <div className="text-center py-12">
                <Target className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No goals found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {filters.search || filters.status !== 'all' || filters.priority !== 'all'
                    ? 'Try adjusting your filters or search terms.'
                    : 'Get started by creating your first career goal.'}
                </p>
                {!filters.search && filters.status === 'all' && filters.priority === 'all' && (
                  <div className="mt-6">
                    <Button onClick={() => handleCreateNew('goal')}>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Goal
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredGoals.map((goal) => (
                  <TaskCard
                    key={goal.id}
                    id={goal.id}
                    title={goal.title}
                    description={goal.description}
                    status={goal.status}
                    priority={goal.priority}
                    progress={goal.progress}
                    targetDate={goal.target_date}
                    type="goal"
                    onEdit={() => handleEdit(goal)}
                    onDelete={() => handleDelete(goal.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Skills and Learning Paths */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Skills Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Skills</h2>
            </div>
            <div className="p-6">
              {skills?.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No skills added yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {skills?.map((skill) => (
                    <div key={skill.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{skill.name}</h4>
                        <p className="text-sm text-gray-500">Level {skill.current_level}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${
                              i < skill.current_level ? 'text-yellow-400 fill-current' : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Learning Paths Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Learning Paths</h2>
            </div>
            <div className="p-6">
              {learningPaths?.length === 0 ? (
                <div className="text-center py-8">
                  <TrendingUp className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No learning paths created yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {learningPaths?.map((path) => (
                    <div key={path.id} className="p-3 bg-gray-50 rounded-lg">
                      <h4 className="font-medium text-gray-900">{path.title}</h4>
                      <p className="text-sm text-gray-500 mt-1">{path.description}</p>
                      <div className="mt-2">
                        <ProgressBar 
                          progress={path.progress || 0} 
                          size="sm"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingGoal(null);
        }}
        title={
          editingGoal 
            ? 'Edit Career Goal' 
            : modalType === 'goal' 
              ? 'Create Career Goal'
              : modalType === 'skill'
                ? 'Add Skill'
                : 'Create Learning Path'
        }
      >
        <CareerForm
          type={modalType}
          editingGoal={editingGoal}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            setEditingGoal(null);
          }}
        />
      </Modal>
    </div>
  );
};

// Form Component
const CareerForm = ({ type, editingGoal, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: editingGoal?.title || '',
    description: editingGoal?.description || '',
    target_date: editingGoal?.target_date ? editingGoal.target_date.split('T')[0] : '',
    priority: editingGoal?.priority || 'medium',
    status: editingGoal?.status || 'not_started',
    name: editingGoal?.name || '', // for skills
    current_level: editingGoal?.current_level || 1, // for skills
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (type === 'skill') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Skill Name
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., React, Python, Project Management"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Level
          </label>
          <Select
            name="current_level"
            value={formData.current_level}
            onChange={handleChange}
          >
            {[1, 2, 3, 4, 5].map(level => (
              <option key={level} value={level}>
                Level {level} - {level === 1 ? 'Beginner' : level === 2 ? 'Elementary' : level === 3 ? 'Intermediate' : level === 4 ? 'Advanced' : 'Expert'}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Add Skill
          </Button>
        </div>
      </form>
    );
  }

  if (type === 'learning-path') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Path Title
          </label>
          <Input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Full Stack Development"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <Textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe your learning path..."
            rows={3}
            required
          />
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Create Path
          </Button>
        </div>
      </form>
    );
  }

  // Default goal form
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Goal Title
        </label>
        <Input
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="e.g., Become a Senior Developer"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <Textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe your career goal..."
          rows={3}
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Date
          </label>
          <Input
            type="date"
            name="target_date"
            value={formData.target_date}
            onChange={handleChange}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <Select
            name="priority"
            value={formData.priority}
            onChange={handleChange}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </Select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Status
        </label>
        <Select
          name="status"
          value={formData.status}
          onChange={handleChange}
        >
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="on_hold">On Hold</option>
          <option value="completed">Completed</option>
        </Select>
      </div>
      <div className="flex justify-end space-x-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {editingGoal ? 'Update Goal' : 'Create Goal'}
        </Button>
      </div>
    </form>
  );
};

export default Career;
