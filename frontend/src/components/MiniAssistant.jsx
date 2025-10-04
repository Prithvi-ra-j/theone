import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { miniAssistantAPI, aiAPI } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Settings, Send, X, Bot, User } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { API_CONFIG } from '../api/config';
import moodAPI from '../api/mood';
import ReactMarkdown from 'react-markdown';

const MiniAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState('');
  const [typing, setTyping] = useState(false);
  const [streamText, setStreamText] = useState('');
  const listRef = useRef(null);
  const endRef = useRef(null);
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

  // AI service status
  const { data: aiStatus } = useQuery({
    queryKey: ['aiStatus'],
    queryFn: aiAPI.getAIServiceStatus,
    staleTime: 60_000,
  });

  // Oldest -> newest like ChatGPT
  const sortedInteractions = useMemo(() => {
    if (!interactions || interactions.length === 0) return [];
    return [...interactions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  }, [interactions]);

  // Fetch mood dashboard for emotion-aware header
  const { data: moodDashboard } = useQuery({
    queryKey: ['moodDashboardHeader'],
    queryFn: () => moodAPI.getMoodDashboard().then(r => r),
    enabled: !!assistant, // show only when assistant exists
    staleTime: 60_000,
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

  // Auto-scroll to bottom on updates (like ChatGPT)
  useEffect(() => {
    if (!isOpen) return;
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isOpen, sortedInteractions, streamText, typing]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    // Immediately add user message
    createInteractionMutation.mutate({ content: message, interaction_type: 'user_message' });

    // Start streaming assistant response
    setTyping(true);
    setStreamText('');
    (async () => {
      try {
        const base = API_CONFIG.FULL_BASE_URL;
        const token = localStorage.getItem('access_token');
        const res = await fetch(`${base}/mini-assistant/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...(token ? { 'Authorization': `Bearer ${token}` } : {}) },
          body: JSON.stringify({ prompt: message })
        });
        if (!res.ok || !res.body) {
          throw new Error('Failed to stream response');
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let acc = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          acc += decoder.decode(value, { stream: true });
          // Show progressive text in the UI
          setStreamText(acc);
          // Turn off typing indicator once first chunk arrives
          if (typing) setTyping(false);
        }
        // Persist final assistant message
        try {
          await miniAssistantAPI.createInteraction({ interaction_type: 'assistant_message', content: acc });
        } catch (err) {
          console.error('Failed to persist assistant message', err);
        }
        queryClient.invalidateQueries(['miniAssistantInteractions']);
      } catch (err) {
        console.error('stream error', err);
      } finally {
        setTyping(false);
        setStreamText('');
      }
    })();
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

  const moodBadge = () => {
    if (!moodDashboard?.weekly_averages) return null;
    const avg = moodDashboard.weekly_averages.mood_score || 0;
    let emoji = '😐';
    if (avg >= 7) emoji = '😊';
    else if (avg <= 3) emoji = '😟';
    const label = `Avg mood ${avg}`;
    return (
      <div className="ml-2 px-2 py-1 text-xs rounded-full bg-white/20 text-white flex items-center gap-1">
        <span>{emoji}</span>
        <span>{label}</span>
      </div>
    );
  };

  const aiBadge = () => {
    if (!aiStatus) return null;
    const available = aiStatus.available ?? false;
    const model = aiStatus.model || 'AI';
    return (
      <div className={`ml-2 px-2 py-1 text-xs rounded-full flex items-center gap-1 ${available ? 'bg-green-500/20 text-green-700 dark:text-green-300' : 'bg-yellow-500/20 text-yellow-700 dark:text-yellow-300'}`}>
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: available ? '#22c55e' : '#f59e0b' }}></span>
        <span>{available ? model : 'AI off'}</span>
      </div>
    );
  };

  const renderHeaderAvatar = () => {
    const av = assistant?.avatar || editForm.avatar || '';
    // If it's a URL, render image
    if (typeof av === 'string' && /^(https?:|data:)/.test(av)) {
      return (
        <img src={av} alt="avatar" className="w-7 h-7 rounded-full object-cover" onError={(e)=>{e.currentTarget.style.display='none';}} />
      );
    }
    // If there's a short emoji-like string, render as text; else fallback to icon
    if (av && av.length <= 3) {
      return <span className="text-2xl leading-none">{av}</span>;
    }
    return <Bot size={22} />;
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
            className="fixed bottom-24 right-6 w-[26rem] max-w-[92vw] bg-white dark:bg-gray-900 rounded-xl shadow-2xl z-50 overflow-hidden border border-gray-200 dark:border-gray-700"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div className="p-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-gray-900 dark:text-white">
                <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-700 dark:text-gray-200">
                  {renderHeaderAvatar()}
                </div>
                <h3 className="font-semibold">{assistant?.name || 'Assistant'}</h3>
                {moodBadge()}
                {aiBadge()}
              </div>
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200"
                title="Settings"
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
                <div ref={listRef} className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800">
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
                      {sortedInteractions.length === 0 ? (
                        <div className="text-center py-4">
                          <p className="text-gray-500 dark:text-gray-400">{assistant.greeting_message || 'Hello! How can I help you today?'}</p>
                        </div>
                      ) : (
                        sortedInteractions.map((interaction) => {
                          const isUser = interaction.interaction_type === 'user_message';
                          return (
                            <div key={interaction.id} className={`flex items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                              {!isUser && (
                                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                                  <Bot size={18} />
                                </div>
                              )}
                              <div className={`max-w-[80%] px-4 py-3 rounded-lg shadow-sm border text-sm leading-relaxed whitespace-pre-wrap ${isUser ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800' : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600'} prose prose-sm dark:prose-invert prose-pre:bg-transparent prose-pre:p-0`}>
                                <ReactMarkdown>{interaction.content}</ReactMarkdown>
                              </div>
                              {isUser && (
                                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-300">
                                  <User size={18} />
                                </div>
                              )}
                            </div>
                          );
                        })
                      )}
                    </>
                  )}
                      {/* Live streaming (assistant) */}
                      {streamText && (
                        <div className="flex items-start gap-3 justify-start">
                          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                            <Bot size={18} />
                          </div>
                          <div className="max-w-[80%] px-4 py-3 rounded-lg shadow-sm border bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-sm prose prose-sm dark:prose-invert prose-pre:bg-transparent prose-pre:p-0">
                            <ReactMarkdown>{streamText}</ReactMarkdown>
                          </div>
                        </div>
                      )}
                      {typing && !streamText && (
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                            <Bot size={18} />
                          </div>
                          <div className="flex-1 px-4 py-3 rounded-md shadow-sm border bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                            <div className="flex gap-1 items-center">
                              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'0ms'}}></span>
                              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'150ms'}}></span>
                              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'300ms'}}></span>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={endRef} />
                </div>
                
                {/* Input area */}
                {assistant && (
                  <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-800 p-3 flex gap-2 bg-white dark:bg-gray-900 sticky bottom-0">
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Message your assistant..."
                      className="flex-1 px-3 py-2 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                    />
                    <button
                      type="submit"
                      className={`px-4 py-2 rounded-md shadow-sm text-white bg-gradient-to-r ${getThemeColor()} hover:opacity-90`}
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