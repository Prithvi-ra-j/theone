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
  AlertCircle,
  AlertTriangle
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../api';
import { toast } from 'react-hot-toast';
import Button from '../components/ui/Button.jsx';
import Input from '../components/ui/Input.jsx';
import Textarea from '../components/ui/Textarea.jsx';
import Select from '../components/ui/Select.jsx';
import Checkbox from '../components/ui/Checkbox.jsx';
import { useAuth } from '../contexts/AuthContext';
import { profileSchema, passwordSchema, preferencesSchema } from '../schemas/profileSchemas';

// Tab Components
const ProfileTab = ({ profileData, isEditing, onChange, onSubmit, isLoading }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    try {
      profileSchema.parse(profileData);
      setErrors({});
      return true;
    } catch (error) {
      const formattedErrors = {};
      error.errors.forEach(err => {
        formattedErrors[err.path[0]] = err.message;
      });
      setErrors(formattedErrors);
      return false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(e);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <Input
            type="text"
            name="name"
            value={profileData.name}
            onChange={onChange}
            disabled={!isEditing}
            placeholder="Your full name"
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.name}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <Input
            type="email"
            name="email"
            value={profileData.email}
            onChange={onChange}
            disabled={!isEditing}
            placeholder="Your email address"
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.email}
            </p>
          )}
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
            placeholder="Tell us about yourself"
            rows={4}
          />
          {errors.bio && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.bio}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <Input
            type="text"
            name="location"
            value={profileData.location}
            onChange={onChange}
            disabled={!isEditing}
            placeholder="Your location"
          />
          {errors.location && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.location}
            </p>
          )}
        </div>

        {isEditing && (
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Profile'}
            </Button>
          </div>
        )}
      </form>
    </div>
  );
};

const PreferencesTab = ({ preferences, onChange, onSubmit, isLoading }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    try {
      preferencesSchema.parse(preferences);
      setErrors({});
      return true;
    } catch (error) {
      const formattedErrors = {};
      error.errors.forEach(err => {
        formattedErrors[err.path[0]] = err.message;
      });
      setErrors(formattedErrors);
      return false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(e);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Theme
          </label>
          <Select
            name="theme"
            value={preferences.theme}
            onChange={onChange}
          >
            <option value="system">System Default</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </Select>
          {errors.theme && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.theme}
            </p>
          )}
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
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="hi">Hindi</option>
          </Select>
          {errors.language && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.language}
            </p>
          )}
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
          {errors.timezone && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.timezone}
            </p>
          )}
        </div>

        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Notifications</h4>
          
          <Checkbox
            name="daily_tips_enabled"
            checked={preferences.daily_tips_enabled}
            onChange={onChange}
            label="Daily Tips"
            description="Receive daily motivational tips and reminders"
          />
          {errors.daily_tips_enabled && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.daily_tips_enabled}
            </p>
          )}

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
            {errors.notification_style && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertTriangle className="w-3 h-3 mr-1" />
                {errors.notification_style}
              </p>
            )}
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
          {errors.hybrid_roadmap_choice && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.hybrid_roadmap_choice}
            </p>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Preferences'}
          </Button>
        </div>
      </form>
    </div>
  );
};

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
}) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    try {
      passwordSchema.parse({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
        confirm_password: passwordData.confirm_password
      });
      setErrors({});
      return true;
    } catch (error) {
      const formattedErrors = {};
      error.errors.forEach(err => {
        formattedErrors[err.path[0]] = err.message;
      });
      setErrors(formattedErrors);
      return false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(e);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Password
          </label>
          <div className="relative">
            <Input
              type={showPassword ? "text" : "password"}
              name="current_password"
              value={passwordData.current_password}
              onChange={onChange}
              placeholder="Enter your current password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          {errors.current_password && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.current_password}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            New Password
          </label>
          <div className="relative">
            <Input
              type={showNewPassword ? "text" : "password"}
              name="new_password"
              value={passwordData.new_password}
              onChange={onChange}
              placeholder="Enter your new password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowNewPassword(!showNewPassword)}
            >
              {showNewPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          {errors.new_password && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.new_password}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Confirm New Password
          </label>
          <div className="relative">
            <Input
              type={showConfirmPassword ? "text" : "password"}
              name="confirm_password"
              value={passwordData.confirm_password}
              onChange={onChange}
              placeholder="Confirm your new password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {errors.confirm_password}
            </p>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Updating...' : 'Update Password'}
          </Button>
        </div>

        <div className="mt-6 bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Security Recommendations</h4>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <span>Use a strong, unique password that you don't use elsewhere</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <span>Include a mix of letters, numbers, and special characters</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <span>Consider using a password manager for better security</span>
            </li>
          </ul>
        </div>
      </form>
    </div>
  );
};

// This component is used in the tab content section but may trigger a false positive linter warning
// It's rendered when activeTab === 'notifications'
const NotificationsTab = () => {
  const [emailNotifications, setEmailNotifications] = useState({
    weeklyReports: true,
    goalReminders: true,
    aiInsights: true
  });

  const [pushNotifications, setPushNotifications] = useState({
    habitReminders: true,
    achievementCelebrations: true,
    motivationalMessages: true
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailChange = (e) => {
    const { name, checked } = e.target;
    setEmailNotifications(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handlePushChange = (e) => {
    const { name, checked } = e.target;
    setPushNotifications(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const validateForm = () => {
    // For notifications, we're just ensuring at least one notification type is enabled
    const hasEmailEnabled = Object.values(emailNotifications).some(value => value === true);
    const hasPushEnabled = Object.values(pushNotifications).some(value => value === true);
    
    const newErrors = {};
    
    if (!hasEmailEnabled && !hasPushEnabled) {
      newErrors.general = "Please enable at least one notification type";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      setIsLoading(true);
      // Simulate API call
      setTimeout(() => {
        setIsLoading(false);
        toast.success('Notification settings saved!');
      }, 500);
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {errors.general && (
          <p className="text-red-500 text-sm flex items-center bg-red-50 p-3 rounded">
            <AlertTriangle className="w-4 h-4 mr-2" />
            {errors.general}
          </p>
        )}
        
        <div className="border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Email Notifications</h4>
          <div className="space-y-3">
            <Checkbox
              name="weeklyReports"
              checked={emailNotifications.weeklyReports}
              onChange={handleEmailChange}
              label="Weekly Progress Reports"
              description="Get a summary of your weekly achievements"
            />
            <Checkbox
              name="goalReminders"
              checked={emailNotifications.goalReminders}
              onChange={handleEmailChange}
              label="Goal Reminders"
              description="Reminders about upcoming deadlines"
            />
            <Checkbox
              name="aiInsights"
              checked={emailNotifications.aiInsights}
              onChange={handleEmailChange}
              label="AI Insights"
              description="Personalized recommendations and insights"
            />
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Push Notifications</h4>
          <div className="space-y-3">
            <Checkbox
              name="habitReminders"
              checked={pushNotifications.habitReminders}
              onChange={handlePushChange}
              label="Habit Reminders"
              description="Daily reminders for your habits"
            />
            <Checkbox
              name="achievementCelebrations"
              checked={pushNotifications.achievementCelebrations}
              onChange={handlePushChange}
              label="Achievement Celebrations"
              description="Celebrate when you reach milestones"
            />
            <Checkbox
              name="motivationalMessages"
              checked={pushNotifications.motivationalMessages}
              onChange={handlePushChange}
              label="Motivational Messages"
              description="Daily motivational content"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Notification Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
};

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
      toast.error(error.message || 'Failed to update profile');
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: authAPI.changePassword,
    onSuccess: () => {
      toast.success('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to change password');
    },
  });

  // State for form data
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    bio: '',
    location: ''
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [preferences, setPreferences] = useState({
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
    daily_tips_enabled: true,
    notification_style: 'moderate',
    hybrid_roadmap_choice: 'both'
  });

  // Update form data when user profile is loaded
  React.useEffect(() => {
    if (userProfile) {
      setProfileData({
        name: userProfile.name || '',
        email: userProfile.email || '',
        bio: userProfile.bio || '',
        location: userProfile.location || ''
      });

      setPreferences({
        theme: userProfile.preferences?.theme || 'system',
        language: userProfile.preferences?.language || 'en',
        timezone: userProfile.preferences?.timezone || 'UTC',
        daily_tips_enabled: userProfile.preferences?.daily_tips_enabled ?? true,
        notification_style: userProfile.preferences?.notification_style || 'moderate',
        hybrid_roadmap_choice: userProfile.preferences?.hybrid_roadmap_choice || 'both'
      });
    }
  }, [userProfile]);

  // Form change handlers
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreferenceChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Submit handlers
  const handleProfileSubmit = (e) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileData);
  };

  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    changePasswordMutation.mutate(passwordData);
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
                  {profileData.name ? profileData.name.charAt(0).toUpperCase() : 'U'}
                </div>
                {isEditing && (
                  <button className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-md border border-gray-200">
                    <Camera className="w-4 h-4 text-gray-600" />
                  </button>
                )}
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-gray-900">{profileData.name || 'User'}</h2>
                <p className="text-gray-500">{profileData.email || 'user@example.com'}</p>
                <p className="text-gray-500 mt-1">{profileData.location || 'No location set'}</p>
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

export default Profile;
