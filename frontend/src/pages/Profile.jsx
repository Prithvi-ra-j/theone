import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Settings, 
  Bell, 
  Shield, 
  Palette, 
  Save,
  Edit3,
  Camera,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../api';
import { toast } from 'react-hot-toast';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import Select from '../components/ui/Select';
import { useAuth } from '../hooks/useAuth';

const Profile = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();

  // Fetch user profile data
  const { data: userProfile, isLoading } = useQuery({
    queryKey: ['user-profile'],
    queryFn: authAPI.getCurrentUserProfile,
  });

  // Mutations
  const updateProfileMutation = useMutation({
    mutationFn: authAPI.updateUserProfile,
    onSuccess: (data) => {
      updateUser(data);
      queryClient.invalidateQueries(['user-profile']);
      toast.success('Profile updated successfully!');
      setIsEditing(false);
    },
    onError: (error) => {
      toast.error('Failed to update profile');
      console.error('Error updating profile:', error);
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: authAPI.changePassword,
    onSuccess: () => {
      toast.success('Password changed successfully!');
      // Reset password fields
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    },
    onError: (error) => {
      toast.error('Failed to change password');
      console.error('Error changing password:', error);
    },
  });

  const [profileData, setProfileData] = useState({
    name: userProfile?.name || '',
    email: userProfile?.email || '',
    bio: userProfile?.bio || '',
    location: userProfile?.location || '',
    website: userProfile?.website || '',
    phone: userProfile?.phone || '',
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [preferences, setPreferences] = useState({
    daily_tips_enabled: userProfile?.preferences?.daily_tips_enabled ?? true,
    notification_style: userProfile?.preferences?.notification_style ?? 'gentle',
    hybrid_roadmap_choice: userProfile?.preferences?.hybrid_roadmap_choice ?? 'both',
    theme: userProfile?.preferences?.theme ?? 'light',
    language: userProfile?.preferences?.language ?? 'en',
    timezone: userProfile?.preferences?.timezone ?? 'UTC',
  });

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  const handlePreferenceChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
  };

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileData);
  };

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }
    if (passwordData.new_password.length < 8) {
      toast.error('New password must be at least 8 characters long');
      return;
    }
    changePasswordMutation.mutate({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password
    });
  };

  const handlePreferencesSubmit = (e) => {
    e.preventDefault();
    updateProfileMutation.mutate({ preferences });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'preferences', label: 'Preferences', icon: Settings },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
            <p className="mt-2 text-gray-600">
              Manage your profile information and preferences.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="p-6">
            <div className="flex items-center space-x-6">
              <div className="relative">
                <div className="w-24 h-24 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  {userProfile?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <button className="absolute bottom-0 right-0 p-2 bg-white rounded-full border-2 border-gray-200 hover:border-primary-300 transition-colors">
                  <Camera className="w-4 h-4 text-gray-600" />
                </button>
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900">{userProfile?.name || 'User'}</h2>
                <p className="text-gray-600">{userProfile?.email}</p>
                {userProfile?.bio && (
                  <p className="text-gray-500 mt-2">{userProfile.bio}</p>
                )}
                <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                  {userProfile?.location && (
                    <span className="flex items-center space-x-1">
                      <span>📍</span>
                      <span>{userProfile.location}</span>
                    </span>
                  )}
                  {userProfile?.website && (
                    <span className="flex items-center space-x-1">
                      <span>🌐</span>
                      <span>{userProfile.website}</span>
                    </span>
                  )}
                </div>
              </div>
              <div className="flex space-x-3">
                <Button
                  onClick={() => setIsEditing(!isEditing)}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>{isEditing ? 'Cancel' : 'Edit Profile'}</span>
                </Button>
                {isEditing && (
                  <Button
                    onClick={handleProfileSubmit}
                    className="flex items-center space-x-2"
                    disabled={updateProfileMutation.isLoading}
                  >
                    <Save className="w-4 h-4" />
                    <span>Save</span>
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg border border-gray-200 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      isActive
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'profile' && (
              <ProfileTab
                profileData={profileData}
                isEditing={isEditing}
                onChange={handleProfileChange}
                onSubmit={handleProfileSubmit}
                isLoading={updateProfileMutation.isLoading}
              />
            )}
            {activeTab === 'preferences' && (
              <PreferencesTab
                preferences={preferences}
                onChange={handlePreferenceChange}
                onSubmit={handlePreferencesSubmit}
                isLoading={updateProfileMutation.isLoading}
              />
            )}
            {activeTab === 'security' && (
              <SecurityTab
                passwordData={passwordData}
                onChange={handlePasswordChange}
                onSubmit={handlePasswordSubmit}
                isLoading={changePasswordMutation.isLoading}
                showPassword={showPassword}
                setShowPassword={setShowPassword}
                showNewPassword={showNewPassword}
                setShowNewPassword={setShowNewPassword}
                showConfirmPassword={showConfirmPassword}
                setShowConfirmPassword={setShowConfirmPassword}
              />
            )}
            {activeTab === 'notifications' && (
              <NotificationsTab />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Components
const ProfileTab = ({ profileData, isEditing, onChange, onSubmit, isLoading }) => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
    
    <form onSubmit={onSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <Input
            name="name"
            value={profileData.name}
            onChange={onChange}
            disabled={!isEditing}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <Input
            type="email"
            name="email"
            value={profileData.email}
            onChange={onChange}
            disabled={!isEditing}
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Bio
        </label>
        <Textarea
          name="bio"
          value={profileData.bio}
          onChange={onChange}
          disabled={!isEditing}
          rows={3}
          placeholder="Tell us a bit about yourself..."
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <Input
            name="location"
            value={profileData.location}
            onChange={onChange}
            disabled={!isEditing}
            placeholder="City, Country"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Website
          </label>
          <Input
            name="website"
            value={profileData.website}
            onChange={onChange}
            disabled={!isEditing}
            placeholder="https://example.com"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Phone Number
        </label>
        <Input
          name="phone"
          value={profileData.phone}
          onChange={onChange}
          disabled={!isEditing}
          placeholder="+1 (555) 123-4567"
        />
      </div>

      {isEditing && (
        <div className="flex justify-end space-x-3 pt-4">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      )}
    </form>
  </div>
);

const PreferencesTab = ({ preferences, onChange, onSubmit, isLoading }) => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold text-gray-900">App Preferences</h3>
    
    <form onSubmit={onSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Theme
          </label>
          <Select
            name="theme"
            value={preferences.theme}
            onChange={onChange}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto (System)</option>
          </Select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Language
          </label>
          <Select
            name="language"
            value={preferences.language}
            onChange={onChange}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
            <option value="bn">Bengali</option>
          </Select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Timezone
        </label>
        <Select
          name="timezone"
          value={preferences.timezone}
          onChange={onChange}
        >
          <option value="UTC">UTC</option>
          <option value="Asia/Kolkata">India (IST)</option>
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
          <option value="Europe/London">London (GMT)</option>
        </Select>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium text-gray-900">Notifications</h4>
        
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-700">Daily Tips</label>
            <p className="text-sm text-gray-500">Receive daily motivational tips and reminders</p>
          </div>
          <input
            type="checkbox"
            name="daily_tips_enabled"
            checked={preferences.daily_tips_enabled}
            onChange={onChange}
            className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notification Style
          </label>
          <Select
            name="notification_style"
            value={preferences.notification_style}
            onChange={onChange}
          >
            <option value="gentle">Gentle</option>
            <option value="moderate">Moderate</option>
            <option value="aggressive">Aggressive</option>
          </Select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Career Roadmap Preference
        </label>
        <Select
          name="hybrid_roadmap_choice"
          value={preferences.hybrid_roadmap_choice}
          onChange={onChange}
        >
          <option value="both">Show Both Traditional & AI-Powered</option>
          <option value="traditional">Traditional Only</option>
          <option value="ai">AI-Powered Only</option>
        </Select>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Preferences'}
        </Button>
      </div>
    </form>
  </div>
);

const SecurityTab = ({ 
  passwordData, 
  onChange, 
  onSubmit, 
  isLoading,
  showPassword,
  setShowPassword,
  showNewPassword,
  setShowNewPassword,
  showConfirmPassword,
  setShowConfirmPassword
}) => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold text-gray-900">Security Settings</h3>
    
    <form onSubmit={onSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Current Password
        </label>
        <div className="relative">
          <Input
            type={showPassword ? 'text' : 'password'}
            name="current_password"
            value={passwordData.current_password}
            onChange={onChange}
            required
            placeholder="Enter your current password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          New Password
        </label>
        <div className="relative">
          <Input
            type={showNewPassword ? 'text' : 'password'}
            name="new_password"
            value={passwordData.new_password}
            onChange={onChange}
            required
            placeholder="Enter your new password"
          />
          <button
            type="button"
            onClick={() => setShowNewPassword(!showNewPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Password must be at least 8 characters long
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Confirm New Password
        </label>
        <div className="relative">
          <Input
            type={showConfirmPassword ? 'text' : 'password'}
            name="confirm_password"
            value={passwordData.confirm_password}
            onChange={onChange}
            required
            placeholder="Confirm your new password"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Changing...' : 'Change Password'}
        </Button>
      </div>
    </form>

    <div className="border-t pt-6">
      <h4 className="font-medium text-gray-900 mb-4">Security Recommendations</h4>
      <div className="space-y-3">
        <div className="flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-900">Use a strong password</p>
            <p className="text-sm text-gray-500">Include uppercase, lowercase, numbers, and special characters</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-900">Enable two-factor authentication</p>
            <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-900">Regular password updates</p>
            <p className="text-sm text-gray-500">Change your password every 3-6 months</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const NotificationsTab = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
    
    <div className="space-y-6">
      <div className="border rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Email Notifications</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Weekly Progress Reports</label>
              <p className="text-sm text-gray-500">Get a summary of your weekly achievements</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Goal Reminders</label>
              <p className="text-sm text-gray-500">Reminders about upcoming deadlines</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">AI Insights</label>
              <p className="text-sm text-gray-500">Personalized recommendations and insights</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Push Notifications</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Habit Reminders</label>
              <p className="text-sm text-gray-500">Daily reminders for your habits</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Achievement Celebrations</label>
              <p className="text-sm text-gray-500">Celebrate when you reach milestones</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Motivational Messages</label>
              <p className="text-sm text-gray-500">Daily motivational content</p>
            </div>
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button>
          Save Notification Settings
        </Button>
      </div>
    </div>
  </div>
);

export default Profile;
