import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
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
  Search,
  AlertCircle
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { careerAPI } from '../api';
// Removed mock data import to rely on real backend data
import { toast } from 'react-hot-toast';
import TaskCard from '../components/ui/TaskCard.jsx';
import ProgressBar from '../components/ui/ProgressBar.jsx';
import AIRecommendations from '../components/AIRecommendations.jsx';
import Modal from '../components/ui/Modal.jsx';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import Textarea from '../components/ui/Textarea.jsx';
import Select from '../components/ui/Select.jsx';

const Career = () => {
  // AI Feedback state
  const [aiFeedbackLoading, setAiFeedbackLoading] = useState(false);
  const [aiFeedback, setAiFeedback] = useState(null);

  const handleGetAIFeedback = async () => {
    setAiFeedbackLoading(true);
    setAiFeedback(null);
    try {
      const res = await careerAPI.getAIFeedback(); // Should call GET /career/feedback
      setAiFeedback(res);
    } catch (err) {
      toast.error('Failed to fetch AI feedback');
      setAiFeedback(null);
    } finally {
      setAiFeedbackLoading(false);
    }
  };
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [modalType, setModalType] = useState('goal'); // 'goal', 'skill', 'learning-path'
  
  // Query hooks need to be defined before they're used in the timeout effect
  const { data: initialCareerData = { recent_goals: [], stats: {}, skills: [] }, isLoading: initialLoading, error: initialCareerError } = useQuery({
    queryKey: ['career', 'dashboard'],
    queryFn: async () => {
      try {
        const data = await careerAPI.getCareerDashboard();
        return data || { recent_goals: [], stats: {}, skills: [] };
      } catch (error) {
        console.error('Error fetching career dashboard:', error);
        throw error; // Let React Query handle the error state
      }
    },
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
  
  const { data: skillsData = { skills: [] }, isLoading: isSkillsLoading, error: skillsQueryError } = useQuery({
    queryKey: ['career', 'skills'],
    queryFn: async () => {
      try {
        const data = await careerAPI.getSkills();
        return data || { skills: [] };
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
    queryKey: ['career', 'learning-paths'],
    queryFn: async () => {
      try {
        const data = await careerAPI.getLearningPaths();
        return data || { paths: [] };
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
  // AI advice modal state
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [aiTargetGoalId, setAiTargetGoalId] = useState(null);
  // Reality Check hint banner
  const [showRealityTip, setShowRealityTip] = useState(true);

  // Learning Path modal state
  const [pathModalOpen, setPathModalOpen] = useState(false);
  const [selectedPath, setSelectedPath] = useState(null);
  const [pathStartDate, setPathStartDate] = useState(() => new Date().toISOString().slice(0,10));

  const openPathModal = (path) => {
    setSelectedPath(path);
    // default start date: today or existing started_at
    const start = path?.started_at ? String(path.started_at).slice(0,10) : new Date().toISOString().slice(0,10);
    setPathStartDate(start);
    setPathModalOpen(true);
  };

  const queryClient = useQueryClient();

  // Use the initial queries above as the canonical data sources to avoid duplicate
  // network requests. Map them to the variable names used throughout the file.
  const careerData = initialCareerData;
  const isLoading = initialLoading;
  const isError = initialCareerError;
  const careerErrObj = initialCareerError;

  const skills = Array.isArray(skillsData)
    ? skillsData
    : (skillsData && skillsData.skills)
      ? skillsData.skills
      : [];
  const skillsLoading = isSkillsLoading;
  const skillsError = skillsQueryError;
  const skillsErrObj = skillsQueryError;

  const learningPaths = Array.isArray(pathsData)
    ? pathsData
    : (pathsData && pathsData.paths)
      ? pathsData.paths
      : [];
  const pathsLoading = isPathsLoading;
  const pathsError = pathsQueryError;
  const pathsErrObj = pathsQueryError;

  // Mutations
  const createGoalMutation = useMutation({
    mutationFn: async (formData) => {
      const data = await careerAPI.createCareerGoal(formData);
      return data;
    },
    onSuccess: (data) => {
      // Invalidate the career dashboard and goals list so UI updates
      queryClient.invalidateQueries(['career', 'dashboard']);
      queryClient.invalidateQueries(['career', 'goals']);
      toast.success('Career goal created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create career goal');
      console.error('Error creating goal:', error);
    },
  });

  const updateGoalMutation = useMutation({
    mutationFn: async (formData) => {
      // Expect formData to include id when updating
      const { id, ...payload } = formData;
      const data = await careerAPI.updateCareerGoal(id, payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['career', 'dashboard']);
      queryClient.invalidateQueries(['career', 'goals']);
      toast.success('Career goal updated successfully!');
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
      queryClient.invalidateQueries(['career', 'dashboard']);
      toast.success('Career goal deleted successfully!');
    },
    onError: (error) => {
      toast.error('Failed to delete career goal');
      console.error('Error deleting goal:', error);
    },
  });

  const createSkillMutation = useMutation({
    mutationFn: careerAPI.createSkill,
    onSuccess: (data) => {
      // data should be the created skill shaped by the API
      const created = data;

      if (created) {
        // Seed individual skill cache
        queryClient.setQueryData(['career', 'skills', created.id], created);

        // Prepend to the skills list if present (handle array or { skills: [] } shapes)
        queryClient.setQueryData(['career', 'skills'], (old) => {
          if (!old) return [created];
          if (Array.isArray(old)) return [created, ...old];
          if (old && Array.isArray(old.skills)) return { ...old, skills: [created, ...old.skills] };
          return old;
        });

        // Also update career dashboard top_skills cache if present
        queryClient.setQueryData(['career', 'dashboard'], (old) => {
          if (!old) return old;
          const top = old.top_skills && Array.isArray(old.top_skills) ? old.top_skills : [];
          return { ...old, top_skills: [created, ...top].slice(0, 5) };
        });
      }

      // Trigger refetch as a safety net
      queryClient.invalidateQueries(['career', 'skills']);
      queryClient.invalidateQueries(['career', 'dashboard']);

      toast.success('Skill added successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to add skill');
      console.error('Error adding skill:', error);
    },
  });

  // Delete Skill
  const deleteSkillMutation = useMutation({
    mutationFn: careerAPI.deleteSkill,
    onSuccess: (data, skillId) => {
      // Remove from skills cache if present (handle array or { skills: [] })
      queryClient.setQueryData(['career', 'skills'], (old) => {
        if (!old) return old;
        if (Array.isArray(old)) return old.filter((s) => s.id !== skillId);
        if (old && Array.isArray(old.skills)) {
          return { ...old, skills: old.skills.filter((s) => s.id !== skillId) };
        }
        return old;
      });

      // Remove individual skill cache entry
      queryClient.removeQueries({ queryKey: ['career', 'skills', skillId] });

      // Update dashboard top_skills if present
      queryClient.setQueryData(['career', 'dashboard'], (old) => {
        if (!old) return old;
        const top = Array.isArray(old.top_skills) ? old.top_skills.filter((s) => s.id !== skillId) : old.top_skills;
        return { ...old, top_skills: top };
      });

      // Safety net: invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['career', 'skills'] });
      queryClient.invalidateQueries({ queryKey: ['career', 'dashboard'] });

      toast.success('Skill deleted successfully!');
    },
    onError: (error) => {
      toast.error('Failed to delete skill');
      console.error('Error deleting skill:', error);
    },
  });

  const createLearningPathMutation = useMutation({
    mutationFn: careerAPI.createLearningPath,
    onSuccess: () => {
      queryClient.invalidateQueries(['career', 'learning-paths']);
      toast.success('Learning path created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create learning path');
      console.error('Error creating learning path:', error);
    },
  });

  // AI mutations (paste after other useMutation blocks)
  const getAIFeedbackMutation = useMutation({
    mutationFn: () => careerAPI.getAIFeedback(),
    onSuccess: (data) => setAiFeedback(data),
    onError: (err) => {
      console.error('Failed to fetch AI feedback', err);
      toast.error('Failed to fetch AI feedback');
      setAiFeedback(null);
    }
  });

  const postGoalAdviceMutation = useMutation({
    mutationFn: ({ goalId, question }) => careerAPI.postGoalAdvice(goalId, { question }),
    onSuccess: (data) => {
      setAiResponse(data);
      queryClient.invalidateQueries(['career', 'dashboard']); // optional
    },
    onError: (err) => {
      console.error('AI advice error:', err);
      toast.error('Failed to fetch AI advice');
      setAiResponse(null);
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

  const handleAIAdvice = (goalId) => {
    setAiTargetGoalId(goalId);
    setAiQuestion('');
    setAiResponse(null);
    setAiModalOpen(true);
  };

  const handleDelete = (goalId) => {
    if (window.confirm('Are you sure you want to delete this career goal?')) {
      deleteGoalMutation.mutate(goalId);
    }
  };

  const handleDeleteSkill = (skillId) => {
    if (window.confirm('Are you sure you want to delete this skill?')) {
      deleteSkillMutation.mutate(skillId);
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

  // AI advice submit handler
  const handleSubmitAI = () => {
    if (!aiQuestion || !aiTargetGoalId) return;
    setAiResponse(null);
    postGoalAdviceMutation.mutate({ goalId: aiTargetGoalId, question: aiQuestion });
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* AI Feedback Button */}
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <Button
          onClick={() => getAIFeedbackMutation.mutate()}
          disabled={getAIFeedbackMutation.isLoading}
          className="mb-4"
        >
          {getAIFeedbackMutation.isLoading ? 'Getting AI Feedback...' : 'Get AI Feedback on My Progress'}
        </Button>

        {aiFeedback && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900 rounded p-4 mt-2">
            <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">AI Feedback</h3>
            <div className="text-sm text-blue-900 dark:text-blue-200 max-h-60 overflow-y-auto pr-2">
              <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
                {String(aiFeedback.feedback || aiFeedback.goal || JSON.stringify(aiFeedback))}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Career Development</h1>
                <p className="mt-2 text-gray-600 dark:text-gray-300">
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
                {/* Reality Check button removed per request; banner tip remains below */}
              </div>
            </div>
          </div>
        </div>
      </div>

  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-gray-900 dark:text-gray-100">
        {/* Reality Check tip banner */}
        {showRealityTip && (
          <div className="mb-6 p-4 rounded-lg border bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-200 flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-300" />
              </div>
              <div>
                <p className="font-medium">Tip: Get a quick Reality Check for your chosen path.</p>
                <p className="text-sm opacity-90">Use the Reality Check page to estimate 5-year outlook, ROI vs. investment, and practical alternatives tailored to your education and location.</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <a href="/reality-check" className="inline-flex items-center px-3 py-1.5 rounded-md bg-green-600 text-white hover:bg-green-700 text-sm">Try Reality Check</a>
              <button onClick={() => setShowRealityTip(false)} className="text-sm text-amber-700 dark:text-amber-300 hover:underline">Dismiss</button>
            </div>
          </div>
        )}
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
                    onAIAdvice={() => handleAIAdvice(goal.id)}
                    aiLoading={postGoalAdviceMutation.isLoading}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Skills and Learning Paths */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Skills Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Skills</h2>
            </div>
            <div className="p-6">
              {skills?.length === 0 ? (
                <div className="text-center py-8">
                  <TrendingUp className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">No skills added yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {skills?.map((skill) => (
                    <div key={skill.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-gray-100">{skill.name}</h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Level {skill.current_level}</p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <button
                          type="button"
                          aria-label="Delete skill"
                          title="Delete skill"
                          onClick={() => handleDeleteSkill(skill.id)}
                          disabled={deleteSkillMutation.isLoading}
                          className="p-2 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 disabled:opacity-60"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-2">AI Recommendations</h3>
                <AIRecommendations />
              </div>
            </div>
          </div>

          {/* Learning Paths Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Learning Paths</h2>
            </div>
            <div className="p-6">
              {learningPaths?.length === 0 ? (
                <div className="text-center py-8">
                  <TrendingUp className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">No learning paths created yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {learningPaths?.map((path) => (
                    <button
                      key={path.id}
                      type="button"
                      onClick={() => openPathModal(path)}
                      className="w-full text-left p-4 bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-gray-100">{path.title}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">{path.description}</p>
                        </div>
                        <span className={`px-2 py-0.5 text-xs rounded-full border ${path.status === 'active' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-200 dark:border-gray-600'}`}>{path.status || 'planned'}</span>
                      </div>
                      <div className="mt-3">
                        <ProgressBar progress={path.progress || 0} size="sm" />
                      </div>
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {path.estimated_hours ? `${path.estimated_hours} hrs • ${Math.max(1, Math.ceil(path.estimated_hours/20))} weeks` : 'Timeline TBD'}
                      </div>
                    </button>
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

      {/* AI Advice modal trigger */}
      <AIAdviceModal
        isOpen={aiModalOpen}
        onClose={() => setAiModalOpen(false)}
        goalId={aiTargetGoalId}
        question={aiQuestion}
        setQuestion={setAiQuestion}
        onSubmit={handleSubmitAI}
        loading={postGoalAdviceMutation.isLoading}
        response={aiResponse}
      />

      {/* Learning Path Detail Modal */}
      <LearningPathModal
        isOpen={pathModalOpen}
        onClose={() => setPathModalOpen(false)}
        path={selectedPath}
        startDate={pathStartDate}
        onChangeStartDate={setPathStartDate}
      />

    </div>
  );
};

// AI Advice Modal Component (simple inline modal using existing Modal)
const AIAdviceModal = ({ isOpen, onClose, goalId, question, setQuestion, onSubmit, loading, response }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={goalId ? 'Ask AI about this goal' : 'Ask AI'}>
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">Your question</label>
        <Textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask the AI for practical steps, resources, or suggestions..." />
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={onSubmit} disabled={loading || !question}>
            {loading ? 'Asking...' : 'Ask AI'}
          </Button>
        </div>

        {response && (
          <div className="mt-4 bg-gray-50 dark:bg-gray-800/60 p-4 rounded border border-gray-200 dark:border-gray-700">
            <h4 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">AI Response</h4>
            <div className="text-sm text-gray-800 dark:text-gray-200 max-h-60 overflow-y-auto pr-2">
              <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
                {String(response.advice || response)}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};


// Hook up the AI modal submission using the careerAPI helper
// (This is placed after export default to keep the page component uncluttered)
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

// Learning Path detail modal with coverage, timeline, start date, and example projects
const LearningPathModal = ({ isOpen, onClose, path, startDate, onChangeStartDate }) => {
  const navigate = useNavigate();
  const [detail, setDetail] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  React.useEffect(() => {
    let active = true;
    const fetchDetail = async () => {
      if (!isOpen || !path) return;
      setLoading(true);
      try {
        const data = await careerAPI.getLearningPath(path.id);
        if (active) setDetail(data);
      } catch (e) {
        console.error('Failed to load learning path detail', e);
        if (active) setDetail(null);
      } finally {
        if (active) setLoading(false);
      }
    };
    fetchDetail();
    return () => { active = false; };
  }, [isOpen, path?.id]);

  if (!path) return null;

  const weeks = Math.max(1, Math.ceil(((detail?.estimated_hours ?? path.estimated_hours) || 20) / 20));
  const milestones = Array.isArray(detail?.milestones) ? detail.milestones : [];
  const projects = Array.isArray(detail?.projects) ? detail.projects : [];

  const queryClient = useQueryClient();
  const updatePathMutation = useMutation({
    mutationFn: (payload) => careerAPI.updateLearningPath(path.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries(['career', 'learning-paths']);
      queryClient.invalidateQueries(['career', 'dashboard']);
      onClose();
    }
  });

  const handleStart = () => {
    if (!startDate) return;
    updatePathMutation.mutate({ started_at: startDate });
  };

  const handleRealityCheck = () => {
    if (!path) return;
    const params = new URLSearchParams();
    if (path.title) params.set('career_path', path.title);
    navigate(`/reality-check?${params.toString()}`);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={path?.title || 'Learning Path'}>
      <div className="space-y-4 text-gray-900 dark:text-gray-100">
        <p className="text-sm text-gray-700 dark:text-gray-300">{detail?.description || path?.description}</p>

        <div>
          <h4 className="font-semibold mb-2">What you'll cover</h4>
          {loading && <div className="text-sm text-gray-500 dark:text-gray-400">Loading…</div>}
          {!loading && milestones.length === 0 && (
            <div className="text-sm text-gray-500 dark:text-gray-400">No milestones yet.</div>
          )}
          {!loading && milestones.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
              {milestones.map((m) => (
                <li key={m.id || m.title}><span className="font-medium">{m.title}</span>{m.description ? ` — ${m.description}` : ''}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h4 className="font-semibold mb-2">Timeline</h4>
          <div className="flex flex-wrap gap-2">
            {Array.from({ length: weeks }).map((_, i) => (
              <span key={i} className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600">Week {i+1}</span>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Estimated: {path?.estimated_hours || weeks*20} hours • {weeks} weeks</p>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Projects</h4>
          {loading && <div className="text-sm text-gray-500 dark:text-gray-400">Loading…</div>}
          {!loading && projects.length === 0 && (
            <div className="text-sm text-gray-500 dark:text-gray-400">No projects yet.</div>
          )}
          {!loading && projects.length > 0 && (
            <ul className="space-y-2">
              {projects.map((p) => (
                <li key={p.id || p.title} className="p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded">
                  <div className="font-medium text-gray-900 dark:text-gray-100">{p.title}</div>
                  {p.description && <div className="text-sm text-gray-600 dark:text-gray-300">{p.description}</div>}
                  {p.est_hours && <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">~{p.est_hours} hours</div>}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pt-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Choose a start date</label>
          <Input type="date" value={startDate} onChange={(e) => onChangeStartDate(e.target.value)} />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={onClose}>Close</Button>
          <Button variant="outline" onClick={handleRealityCheck}>Reality Check</Button>
          <Button onClick={handleStart} disabled={updatePathMutation.isLoading}>{updatePathMutation.isLoading ? 'Saving...' : 'Start this path'}</Button>
        </div>
      </div>
    </Modal>
  );
};

