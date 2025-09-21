import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { miniAssistantAPI } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Settings, Send, X, Edit3, Save } from 'lucide-react';
import { toast } from 'react-hot-toast';

const MiniAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState('');
  const [editForm, setEditForm] = useState({
    name: '',
    avatar: '',
    personality: '',
    color_theme: 'blue',
    greeting_message: '',
    preferences: {}
  });
  
  const queryClient = useQueryClient();
  
  // Fetch mini assistant data
  const { data: assistant, isLoading, isError } = useQuery({
    queryKey: ['miniAssistant'],
    queryFn: miniAssistantAPI.getMiniAssistant,
    onError: () => {
      // If there's an error, it might be because the assistant doesn't exist yet
      console.log('No mini assistant found or error fetching');
    }
  });
  
  // Fetch interactions
  const { data: interactions = [] } = useQuery({
    queryKey: ['miniAssistantInteractions'],
    queryFn: miniAssistantAPI.getInteractions,
    enabled: !!assistant, // Only fetch if assistant exists
  });
  
  // Create assistant mutation
  const createAssistantMutation = useMutation({
    mutationFn: miniAssistantAPI.createMiniAssistant,
    onSuccess: () => {
      queryClient.invalidateQueries(['miniAssistant']);
      toast.success('Mini assistant created!');
      setIsEditing(false);
    },
    onError: (error) => {
      toast.error(`Failed to create assistant: ${error.message}`);
    }
  });
  
  // Update assistant mutation
  const updateAssistantMutation = useMutation({
    mutationFn: miniAssistantAPI.updateMiniAssistant,
    onSuccess: () => {
      queryClient.invalidateQueries(['miniAssistant']);
      toast.success('Mini assistant updated!');
      setIsEditing(false);
    },
    onError: (error) => {
      toast.error(`Failed to update assistant: ${error.message}`);
    }
  });
  
  // Create interaction mutation
  const createInteractionMutation = useMutation({
    mutationFn: miniAssistantAPI.createInteraction,
    onSuccess: () => {
      queryClient.invalidateQueries(['miniAssistantInteractions']);
      setMessage('');
    }
  });
  
  // Mark interactions as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: miniAssistantAPI.markInteractionsAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['miniAssistantInteractions']);
    }
  });
  
  // Initialize edit form when assistant data is loaded
  useEffect(() => {
    if (assistant) {
      setEditForm({
        name: assistant.name || '',
        avatar: assistant.avatar || '',
        personality: assistant.personality || '',
        color_theme: assistant.color_theme || 'blue',
        greeting_message: assistant.greeting_message || '',
        preferences: assistant.preferences || {}
      });
    } else if (!isLoading && !isError) {
      // If no assistant exists and there's no loading or error state, set default values
      setEditForm({
        name: 'Dristhi Assistant',
        avatar: '👨‍💼',
        personality: 'Helpful and friendly',
        color_theme: 'blue',
        greeting_message: 'Hello! I\'m your personal assistant. How can I help you today?',
        preferences: { notifications: true }
      });
    }
  }, [assistant, isLoading, isError]);
  
  // Mark interactions as read when opening the assistant
  useEffect(() => {
    if (isOpen && assistant) {
      markAsReadMutation.mutate();
    }
  }, [isOpen, assistant]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    createInteractionMutation.mutate({
      content: message,
      interaction_type: 'user_message'
    });
  };
  
  const handleSaveAssistant = () => {
    if (assistant) {
      updateAssistantMutation.mutate(editForm);
    } else {
      createAssistantMutation.mutate(editForm);
    }
  };
  
  const getThemeColor = () => {
    const theme = assistant?.color_theme || editForm.color_theme || 'blue';
    switch (theme) {
      case 'blue': return 'from-blue-500 to-blue-600';
      case 'purple': return 'from-purple-500 to-purple-600';
      case 'green': return 'from-green-500 to-green-600';
      case 'red': return 'from-red-500 to-red-600';
      case 'orange': return 'from-orange-500 to-orange-600';
      default: return 'from-blue-500 to-blue-600';
    }
  };
  
  // Render assistant button or full interface
  return (
    <>
      {/* Floating button */}
      <motion.button
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-r ${getThemeColor()} text-white shadow-lg flex items-center justify-center z-50`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X size={24} /> : <MessageSquare size={24} />}
      </motion.button>
      
      {/* Assistant panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed bottom-24 right-6 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl z-50 overflow-hidden"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div className={`p-4 bg-gradient-to-r ${getThemeColor()} text-white flex items-center justify-between`}>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{assistant?.avatar || editForm.avatar}</span>
                <h3 className="font-bold">{assistant?.name || 'Mini Assistant'}</h3>
              </div>
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="p-1 hover:bg-white/20 rounded-full"
              >
                <Settings size={18} />
              </button>
            </div>
            
            {/* Edit mode */}
            {isEditing ? (
              <div className="p-4 space-y-4">
                <h3 className="font-semibold text-gray-900 dark:text-white">Customize Your Assistant</h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      value={editForm.name}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Avatar (emoji)
                    </label>
                    <input
                      type="text"
                      value={editForm.avatar}
                      onChange={(e) => setEditForm({...editForm, avatar: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                      maxLength={2}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Personality
                    </label>
                    <input
                      type="text"
                      value={editForm.personality}
                      onChange={(e) => setEditForm({...editForm, personality: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Color Theme
                    </label>
                    <select
                      value={editForm.color_theme}
                      onChange={(e) => setEditForm({...editForm, color_theme: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="blue">Blue</option>
                      <option value="purple">Purple</option>
                      <option value="green">Green</option>
                      <option value="red">Red</option>
                      <option value="orange">Orange</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Greeting Message
                    </label>
                    <textarea
                      value={editForm.greeting_message}
                      onChange={(e) => setEditForm({...editForm, greeting_message: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                      rows={3}
                    />
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2 pt-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveAssistant}
                    className={`px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r ${getThemeColor()} hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500`}
                    disabled={createAssistantMutation.isLoading || updateAssistantMutation.isLoading}
                  >
                    {createAssistantMutation.isLoading || updateAssistantMutation.isLoading ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* Chat area */}
                <div className="h-80 overflow-y-auto p-4 space-y-3">
                  {!assistant ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500 dark:text-gray-400 mb-4">You haven't set up your mini assistant yet!</p>
                      <button
                        onClick={() => setIsEditing(true)}
                        className={`px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r ${getThemeColor()} hover:opacity-90`}
                      >
                        Set Up Now
                      </button>
                    </div>
                  ) : (
                    <>
                      {interactions.length === 0 ? (
                        <div className="text-center py-4">
                          <p className="text-gray-500 dark:text-gray-400">{assistant.greeting_message || 'Hello! How can I help you today?'}</p>
                        </div>
                      ) : (
                        interactions.map((interaction) => (
                          <div 
                            key={interaction.id}
                            className={`p-3 rounded-lg max-w-[85%] ${
                              interaction.interaction_type === 'user_message' 
                                ? 'bg-gray-100 dark:bg-gray-700 ml-auto' 
                                : `bg-gradient-to-r ${getThemeColor()} text-white mr-auto`
                            }`}
                          >
                            {interaction.content}
                          </div>
                        ))
                      )}
                    </>
                  )}
                </div>
                
                {/* Input area */}
                {assistant && (
                  <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-700 p-3 flex">
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-l-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                    />
                    <button
                      type="submit"
                      className={`px-3 py-2 rounded-r-md shadow-sm text-white bg-gradient-to-r ${getThemeColor()} hover:opacity-90`}
                      disabled={createInteractionMutation.isLoading || !message.trim()}
                    >
                      <Send size={18} />
                    </button>
                  </form>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default MiniAssistant;