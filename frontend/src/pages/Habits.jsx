import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Plus, 
  Edit3, 
  Trash2, 
  CheckCircle, 
  Clock,
  TrendingUp,
  Target,
  Filter,
  Search,
  Calendar as CalendarIcon,
  Repeat,
  Bell
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { habitsAPI } from '../api';
import { toast } from 'react-hot-toast';
import TaskCard from '../components/ui/TaskCard';
import ProgressBar from '../components/ui/ProgressBar';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import Select from '../components/ui/Select';
import { format } from 'date-fns';

const Habits = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('habit'); // 'habit', 'task', 'event'
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
    search: ''
  });

  const queryClient = useQueryClient();

  // Fetch habits data
  const { data: habitsData, isLoading } = useQuery({
    queryKey: ['habits-dashboard'],
    queryFn: habitsAPI.getHabitsDashboard,
  });

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: habitsAPI.getTasks,
  });

  const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ['events'],
    queryFn: habitsAPI.getEvents,
  });

  // Mutations
  const createHabitMutation = useMutation({
    mutationFn: habitsAPI.createHabit,
    onSuccess: () => {
      queryClient.invalidateQueries(['habits-dashboard']);
      toast.success('Habit created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create habit');
      console.error('Error creating habit:', error);
    },
  });

  const updateHabitMutation = useMutation({
    mutationFn: habitsAPI.updateHabit,
    onSuccess: () => {
      queryClient.invalidateQueries(['habits-dashboard']);
      toast.success('Habit updated successfully!');
      setIsModalOpen(false);
      setEditingItem(null);
    },
    onError: (error) => {
      toast.error('Failed to update habit');
      console.error('Error updating habit:', error);
    },
  });

  const deleteHabitMutation = useMutation({
    mutationFn: habitsAPI.deleteHabit,
    onSuccess: () => {
      queryClient.invalidateQueries(['habits-dashboard']);
      toast.success('Habit deleted successfully!');
    },
    onError: (error) => {
      toast.error('Failed to delete habit');
      console.error('Error deleting habit:', error);
    },
  });

  const completeHabitMutation = useMutation({
    mutationFn: habitsAPI.completeHabit,
    onSuccess: () => {
      queryClient.invalidateQueries(['habits-dashboard']);
      toast.success('Habit completed!');
    },
    onError: (error) => {
      toast.error('Failed to complete habit');
      console.error('Error completing habit:', error);
    },
  });

  const createTaskMutation = useMutation({
    mutationFn: habitsAPI.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks']);
      toast.success('Task created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create task');
      console.error('Error creating task:', error);
    },
  });

  const createEventMutation = useMutation({
    mutationFn: habitsAPI.createEvent,
    onSuccess: () => {
      queryClient.invalidateQueries(['events']);
      toast.success('Event created successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create event');
      console.error('Error creating event:', error);
    },
  });

  const handleCreateNew = (type) => {
    setModalType(type);
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setModalType('habit');
    setIsModalOpen(true);
  };

  const handleDelete = (itemId) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      deleteHabitMutation.mutate(itemId);
    }
  };

  const handleComplete = (habitId) => {
    completeHabitMutation.mutate(habitId);
  };

  const handleSubmit = (formData) => {
    if (modalType === 'habit') {
      if (editingItem) {
        updateHabitMutation.mutate({ id: editingItem.id, ...formData });
      } else {
        createHabitMutation.mutate(formData);
      }
    } else if (modalType === 'task') {
      createTaskMutation.mutate(formData);
    } else if (modalType === 'event') {
      createEventMutation.mutate(formData);
    }
  };

  const filteredHabits = React.useMemo(() => {
    if (!habitsData?.today_habits) return [];
    
    return habitsData.today_habits.filter(habit => {
      const matchesStatus = filters.status === 'all' || habit.is_completed === (filters.status === 'completed');
      const matchesCategory = filters.category === 'all' || habit.category === filters.category;
      const matchesSearch = filters.search === '' || 
        habit.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        habit.description?.toLowerCase().includes(filters.search.toLowerCase());
      
      return matchesStatus && matchesCategory && matchesSearch;
    });
  }, [habitsData?.today_habits, filters]);

  if (isLoading || tasksLoading || eventsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const today = new Date();
  const todayFormatted = format(today, 'EEEE, MMMM d');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Habits & Tasks</h1>
                <p className="mt-2 text-gray-600">
                  Build positive habits and stay organized with daily tasks.
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  {todayFormatted}
                </p>
              </div>
              <div className="flex space-x-3">
                <Button
                  onClick={() => handleCreateNew('habit')}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Habit</span>
                </Button>
                <Button
                  onClick={() => handleCreateNew('task')}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Task</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Habits</p>
                <p className="text-2xl font-bold text-gray-900">
                  {habitsData?.total_habits || 0}
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
                <p className="text-sm font-medium text-gray-600">Completed Today</p>
                <p className="text-2xl font-bold text-gray-900">
                  {habitsData?.completed_habits_today || 0}
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
                <p className="text-sm font-medium text-gray-600">Current Streak</p>
                <p className="text-2xl font-bold text-gray-900">
                  {habitsData?.current_streak || 0} days
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-orange-50 rounded-lg">
                <Target className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Today's Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {habitsData?.total_habits > 0 
                    ? Math.round((habitsData.completed_habits_today / habitsData.total_habits) * 100)
                    : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Today's Progress */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Today's Progress</h2>
          <ProgressBar 
            progress={habitsData?.total_habits > 0 
              ? (habitsData.completed_habits_today / habitsData.total_habits) * 100
              : 0
            }
            size="lg"
            showPercentage
          />
          <p className="text-sm text-gray-600 mt-2">
            {habitsData?.completed_habits_today || 0} of {habitsData?.total_habits || 0} habits completed
          </p>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search habits..."
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
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </Select>
            <Select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Categories</option>
              <option value="health">Health</option>
              <option value="productivity">Productivity</option>
              <option value="learning">Learning</option>
              <option value="fitness">Fitness</option>
              <option value="mindfulness">Mindfulness</option>
            </Select>
          </div>
        </div>

        {/* Today's Habits */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Today's Habits</h2>
          </div>
          <div className="p-6">
            {filteredHabits.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No habits found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {filters.search || filters.status !== 'all' || filters.category !== 'all'
                    ? 'Try adjusting your filters or search terms.'
                    : 'Get started by creating your first habit.'}
                </p>
                {!filters.search && filters.status === 'all' && filters.category === 'all' && (
                  <div className="mt-6">
                    <Button onClick={() => handleCreateNew('habit')}>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Habit
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredHabits.map((habit) => (
                  <TaskCard
                    key={habit.id}
                    id={habit.id}
                    title={habit.name}
                    description={habit.description}
                    status={habit.is_completed ? 'completed' : 'pending'}
                    category={habit.category}
                    streak={habit.current_streak}
                    type="habit"
                    onComplete={() => handleComplete(habit.id)}
                    onEdit={() => handleEdit(habit)}
                    onDelete={() => handleDelete(habit.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Tasks and Events */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Tasks Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Tasks</h2>
                <Button
                  onClick={() => handleCreateNew('task')}
                  size="sm"
                  variant="outline"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="p-6">
              {tasks?.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No tasks yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks?.slice(0, 5).map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={task.status === 'completed'}
                          onChange={() => {}}
                          className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                        />
                        <div>
                          <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                            {task.title}
                          </h4>
                          {task.due_date && (
                            <p className="text-sm text-gray-500">
                              Due: {format(new Date(task.due_date), 'MMM d')}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          task.priority === 'high' ? 'bg-red-100 text-red-800' :
                          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Events Section */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Upcoming Events</h2>
                <Button
                  onClick={() => handleCreateNew('event')}
                  size="sm"
                  variant="outline"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="p-6">
              {events?.length === 0 ? (
                <div className="text-center py-8">
                  <CalendarIcon className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No events scheduled.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {events?.slice(0, 5).map((event) => (
                    <div key={event.id} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-primary-100 rounded-lg">
                          <CalendarIcon className="w-4 h-4 text-primary-600" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{event.title}</h4>
                          <p className="text-sm text-gray-500">
                            {format(new Date(event.start_time), 'MMM d, h:mm a')}
                          </p>
                        </div>
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
          setEditingItem(null);
        }}
        title={
          editingItem 
            ? 'Edit Habit' 
            : modalType === 'habit' 
              ? 'Create Habit'
              : modalType === 'task'
                ? 'Create Task'
                : 'Create Event'
        }
      >
        <HabitsForm
          type={modalType}
          editingItem={editingItem}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            setEditingItem(null);
          }}
        />
      </Modal>
    </div>
  );
};

// Form Component
const HabitsForm = ({ type, editingItem, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: editingItem?.name || '',
    description: editingItem?.description || '',
    category: editingItem?.category || 'productivity',
    frequency: editingItem?.frequency || 'daily',
    reminder_time: editingItem?.reminder_time || '',
    title: editingItem?.title || '', // for tasks
    due_date: editingItem?.due_date ? editingItem.due_date.split('T')[0] : '', // for tasks
    priority: editingItem?.priority || 'medium', // for tasks
    start_time: editingItem?.start_time ? editingItem.start_time.split('T')[0] : '', // for events
    end_time: editingItem?.end_time ? editingItem.end_time.split('T')[0] : '', // for events
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (type === 'task') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Task Title
          </label>
          <Input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Review project proposal"
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
            placeholder="Task details..."
            rows={3}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <Input
              type="date"
              name="due_date"
              value={formData.due_date}
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
            </Select>
          </div>
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Create Task
          </Button>
        </div>
      </form>
    );
  }

  if (type === 'event') {
    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Event Title
          </label>
          <Input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Team meeting"
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
            placeholder="Event details..."
            rows={3}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <Input
              type="date"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <Input
              type="date"
              name="end_time"
              value={formData.end_time}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit">
            Create Event
          </Button>
        </div>
      </form>
    );
  }

  // Default habit form
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Habit Name
        </label>
        <Input
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="e.g., Morning exercise"
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
          placeholder="Describe your habit..."
          rows={3}
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <Select
            name="category"
            value={formData.category}
            onChange={handleChange}
          >
            <option value="health">Health</option>
            <option value="productivity">Productivity</option>
            <option value="learning">Learning</option>
            <option value="fitness">Fitness</option>
            <option value="mindfulness">Mindfulness</option>
          </Select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Frequency
          </label>
          <Select
            name="frequency"
            value={formData.frequency}
            onChange={handleChange}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </Select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reminder Time
        </label>
        <Input
          type="time"
          name="reminder_time"
          value={formData.reminder_time}
          onChange={handleChange}
        />
      </div>
      <div className="flex justify-end space-x-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {editingItem ? 'Update Habit' : 'Create Habit'}
        </Button>
      </div>
    </form>
  );
};

export default Habits;
