import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Heart, 
  Plus, 
  TrendingUp,
  TrendingDown,
  Activity,
  Moon,
  Coffee,
  BookOpen,
  Music,
  Sun,
  Cloud,
  CloudRain,
  Zap,
  Target,
  BarChart3
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { moodAPI } from '../api';
import { toast } from 'react-hot-toast';
import Modal from '../components/ui/Modal.jsx';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import Textarea from '../components/ui/Textarea.jsx';
import Select from '../components/ui/Select.jsx';
import { format, subDays, startOfWeek, endOfWeek } from 'date-fns';

const Mood = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [filters, setFilters] = useState({
    dateRange: 'week',
    moodRange: 'all'
  });

  const queryClient = useQueryClient();

  // Fetch mood data
  const { data: moodData, isLoading: moodLoading, isError: moodError, error: moodErrObj } = useQuery({
    queryKey: ['mood-dashboard'],
    queryFn: moodAPI.getMoodDashboard,
  });

  const { data: moodLogs, isLoading: logsLoading, isError: logsError, error: logsErrObj } = useQuery({
    queryKey: ['mood-logs'],
    queryFn: moodAPI.getMoodLogs,
  });

  // Timeout logic
  const [timedOut, setTimedOut] = React.useState(false);
  React.useEffect(() => {
    if (!(moodLoading || logsLoading)) return;
    const timeout = setTimeout(() => setTimedOut(true), 30000);
    return () => clearTimeout(timeout);
  }, [moodLoading, logsLoading]);

  // Error logging and error UI
  if (moodError || logsError) {
    console.error('Mood page load error:', {
      mood: moodErrObj,
      logs: logsErrObj,
    });
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50 dark:bg-red-900">
        <div>
          <h2 className="text-xl font-bold text-red-700 dark:text-red-300">Error loading mood data</h2>
          <pre className="text-xs text-red-600 dark:text-red-200">
            {JSON.stringify({
              mood: moodErrObj?.message,
              logs: logsErrObj?.message,
            }, null, 2)}
          </pre>
        </div>
      </div>
    );
  }
  if (timedOut) {
    console.error('Mood page load timeout: Data did not load within 30 seconds');
    return (
      <div className="flex items-center justify-center min-h-screen bg-yellow-50 dark:bg-yellow-900">
        <div>
          <h2 className="text-xl font-bold text-yellow-700 dark:text-yellow-300">Timeout: Mood data did not load within 30 seconds</h2>
          <p className="text-xs text-yellow-600 dark:text-yellow-200">Please check your network or backend server.</p>
        </div>
      </div>
    );
  }

  // Mutations
  const createMoodLogMutation = useMutation({
    mutationFn: moodAPI.logMood,
    onSuccess: () => {
      queryClient.invalidateQueries(['mood-dashboard']);
      queryClient.invalidateQueries(['mood-logs']);
      toast.success('Mood logged successfully!');
      setIsModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to log mood');
      console.error('Error logging mood:', error);
    },
  });

  const handleCreateNew = () => {
    setEditingEntry(null);
    setIsModalOpen(true);
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setIsModalOpen(true);
  };

  const handleSubmit = (formData) => {
    createMoodLogMutation.mutate(formData);
  };

  const getDateRange = () => {
    const now = new Date();
    switch (filters.dateRange) {
      case 'week':
        return { start: startOfWeek(now), end: endOfWeek(now) };
      case 'month':
        return { start: subDays(now, 30), end: now };
      case 'quarter':
        return { start: subDays(now, 90), end: now };
      default:
        return { start: startOfWeek(now), end: endOfWeek(now) };
    }
  };

  const getMoodEmoji = (score) => {
    if (score >= 9) return '😍';
    if (score >= 8) return '😊';
    if (score >= 7) return '🙂';
    if (score >= 6) return '😐';
    if (score >= 5) return '😕';
    if (score >= 4) return '😟';
    if (score >= 3) return '😔';
    if (score >= 2) return '😢';
    return '😭';
  };

  const getMoodColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-blue-600 bg-blue-100';
    if (score >= 4) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (moodLoading || logsLoading) {
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
                <h1 className="text-3xl font-bold text-gray-900">Mood & Wellness</h1>
                <p className="mt-2 text-gray-600">
                  Track your daily mood, energy, and wellness metrics.
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  {todayFormatted}
                </p>
              </div>
              <Button
                onClick={handleCreateNew}
                className="flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Log Mood</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Current Mood Overview */}
        <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl p-6 text-white mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">How are you feeling today?</h2>
              <p className="text-primary-100">Take a moment to check in with yourself</p>
            </div>
            <div className="text-right">
              <div className="text-6xl mb-2">
                {moodData?.today_mood ? getMoodEmoji(moodData.today_mood) : '🤔'}
              </div>
              <div className="text-primary-100">
                {moodData?.today_mood ? `Score: ${moodData.today_mood}/10` : 'Not logged yet'}
              </div>
            </div>
          </div>
        </div>

        {/* Wellness Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Heart className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Weekly Mood Avg</p>
                <p className="text-2xl font-bold text-gray-900">
                  {moodData?.weekly_mood_average || 0}/10
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-green-50 rounded-lg">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Energy Level</p>
                <p className="text-2xl font-bold text-gray-900">
                  {moodData?.current_energy_level || 0}/10
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-purple-50 rounded-lg">
                <Moon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Sleep Hours</p>
                <p className="text-2xl font-bold text-gray-900">
                  {moodData?.weekly_sleep_average || 0}h
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
                <p className="text-sm font-medium text-gray-600">Stress Level</p>
                <p className="text-2xl font-bold text-gray-900">
                  {moodData?.current_stress_level || 0}/10
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <Select
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
            </Select>
            <Select
              value={filters.moodRange}
              onChange={(e) => setFilters(prev => ({ ...prev, moodRange: e.target.value }))}
              className="w-full sm:w-40"
            >
              <option value="all">All Moods</option>
              <option value="high">High (8-10)</option>
              <option value="medium">Medium (5-7)</option>
              <option value="low">Low (1-4)</option>
            </Select>
          </div>
        </div>

        {/* Mood Trends */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Mood Trends</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-7 gap-2 mb-4">
              {Array.from({ length: 7 }, (_, i) => {
                const date = subDays(today, 6 - i);
                const dayName = format(date, 'EEE');
                const dayNumber = format(date, 'd');
                const isToday = format(date, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd');
                
                return (
                  <div key={i} className="text-center">
                    <div className="text-xs text-gray-500 mb-1">{dayName}</div>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      isToday ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {dayNumber}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {Array.from({ length: 7 }, (_, i) => {
                const date = subDays(today, 6 - i);
                const moodScore = moodLogs?.find(log => 
                  format(new Date(log.logged_at), 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
                )?.mood_score;
                
                if (!moodScore) {
                  return (
                    <div key={i} className="text-center">
                      <div className="w-8 h-8 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-400 text-xs">-</span>
                      </div>
                    </div>
                  );
                }
                
                return (
                  <div key={i} className="text-center">
                    <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-lg ${
                      getMoodColor(moodScore).split(' ')[0]
                    }`}>
                      {getMoodEmoji(moodScore)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{moodScore}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Recent Mood Logs */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Mood Logs</h2>
          </div>
          <div className="p-6">
            {moodLogs?.length === 0 ? (
              <div className="text-center py-12">
                <Heart className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No mood logs yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Start tracking your mood to see patterns and insights.
                </p>
                <div className="mt-6">
                  <Button onClick={handleCreateNew}>
                    <Plus className="w-4 h-4 mr-2" />
                    Log First Mood
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {moodLogs?.slice(0, 10).map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-lg ${getMoodColor(log.mood_score)}`}>
                        <span className="text-2xl">{getMoodEmoji(log.mood_score)}</span>
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900">
                            Mood Score: {log.mood_score}/10
                          </h4>
                          <span className={`px-2 py-1 text-xs rounded-full ${getMoodColor(log.mood_score)}`}>
                            {log.mood_score >= 8 ? 'Great' : log.mood_score >= 6 ? 'Good' : log.mood_score >= 4 ? 'Okay' : 'Low'}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                          {log.energy_level && (
                            <span className="flex items-center space-x-1">
                              <Activity className="w-4 h-4" />
                              <span>Energy: {log.energy_level}/10</span>
                            </span>
                          )}
                          {log.sleep_hours && (
                            <span className="flex items-center space-x-1">
                              <Moon className="w-4 h-4" />
                              <span>Sleep: {log.sleep_hours}h</span>
                            </span>
                          )}
                          {log.exercise_minutes && (
                            <span className="flex items-center space-x-1">
                              <Zap className="w-4 h-4" />
                              <span>Exercise: {log.exercise_minutes}m</span>
                            </span>
                          )}
                        </div>
                        {log.notes && (
                          <p className="text-sm text-gray-600 mt-2">{log.notes}</p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {format(new Date(log.logged_at), 'MMM d, h:mm a')}
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(log)}
                        className="mt-2"
                      >
                        Edit
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Wellness Tips */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Wellness Tips</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Sun className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Morning Routine</h4>
                <p className="text-sm text-gray-600">
                  Start your day with 10 minutes of sunlight exposure and gentle stretching.
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Coffee className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Hydration</h4>
                <p className="text-sm text-gray-600">
                  Drink a glass of water first thing in the morning to kickstart your metabolism.
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <BookOpen className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Mindfulness</h4>
                <p className="text-sm text-gray-600">
                  Take 5 minutes to practice deep breathing or meditation throughout the day.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingEntry(null);
        }}
        title={editingEntry ? 'Edit Mood Entry' : 'Log Your Mood'}
      >
        <MoodForm
          editingEntry={editingEntry}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            setEditingEntry(null);
          }}
        />
      </Modal>
    </div>
  );
};

// Form Component
const MoodForm = ({ editingEntry, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    mood_score: editingEntry?.mood_score || 5,
    energy_level: editingEntry?.energy_level || 5,
    stress_level: editingEntry?.stress_level || 5,
    sleep_hours: editingEntry?.sleep_hours || 7,
    exercise_minutes: editingEntry?.exercise_minutes || 0,
    notes: editingEntry?.notes || '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getMoodEmoji = (score) => {
    if (score >= 9) return '😍';
    if (score >= 8) return '😊';
    if (score >= 7) return '🙂';
    if (score >= 6) return '😐';
    if (score >= 5) return '😕';
    if (score >= 4) return '😟';
    if (score >= 3) return '😔';
    if (score >= 2) return '😢';
    return '😭';
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Mood Score */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          How are you feeling today?
        </label>
        <div className="text-center">
          <div className="text-6xl mb-4">{getMoodEmoji(formData.mood_score)}</div>
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {formData.mood_score}/10
          </div>
          <input
            type="range"
            name="mood_score"
            min="1"
            max="10"
            value={formData.mood_score}
            onChange={handleChange}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Terrible</span>
            <span>Great</span>
          </div>
        </div>
      </div>

      {/* Other Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Energy Level (1-10)
          </label>
          <Select
            name="energy_level"
            value={formData.energy_level}
            onChange={handleChange}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(level => (
              <option key={level} value={level}>
                {level} - {level === 1 ? 'Exhausted' : level === 5 ? 'Neutral' : level === 10 ? 'Energized' : ''}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Stress Level (1-10)
          </label>
          <Select
            name="stress_level"
            value={formData.stress_level}
            onChange={handleChange}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(level => (
              <option key={level} value={level}>
                {level} - {level === 1 ? 'Relaxed' : level === 5 ? 'Moderate' : level === 10 ? 'Overwhelmed' : ''}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sleep Hours
          </label>
          <Input
            type="number"
            name="sleep_hours"
            value={formData.sleep_hours}
            onChange={handleChange}
            min="0"
            max="24"
            step="0.5"
            placeholder="7"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Exercise Minutes
          </label>
          <Input
            type="number"
            name="exercise_minutes"
            value={formData.exercise_minutes}
            onChange={handleChange}
            min="0"
            max="300"
            placeholder="30"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notes (Optional)
        </label>
        <Textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="How was your day? Any specific events or feelings you want to remember?"
          rows={3}
        />
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {editingEntry ? 'Update Entry' : 'Log Mood'}
        </Button>
      </div>
    </form>
  );
};

export default Mood;
