import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, Clock, AlertCircle, Trash2, Edit3 } from 'lucide-react';
import { MessageSquare } from 'lucide-react';

const TaskCard = ({
  id,
  title,
  description,
  status = 'pending',
  priority = 'medium',
  dueDate,
  completedAt,
  onComplete,
  onEdit,
  onDelete,
  onAIAdvice,
  aiLoading = false,
  type = 'task', // 'task', 'habit', 'goal'
  streak = 0,
  className = '',
  ...props
}) => {
  // Status variants
  const statusConfig = {
    pending: {
      icon: Circle,
      color: 'text-gray-500',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-200'
    },
    in_progress: {
      icon: Clock,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
      borderColor: 'border-blue-200'
    },
    completed: {
      icon: CheckCircle,
      color: 'text-success-500',
      bgColor: 'bg-success-100',
      borderColor: 'border-success-200'
    },
    overdue: {
      icon: AlertCircle,
      color: 'text-danger-500',
      bgColor: 'bg-danger-100',
      borderColor: 'border-danger-200'
    }
  };

  // Priority variants
  const priorityConfig = {
    low: { color: 'text-gray-500', bgColor: 'bg-gray-100' },
    medium: { color: 'text-blue-500', bgColor: 'bg-blue-100' },
    high: { color: 'text-warning-500', bgColor: 'bg-warning-100' },
    urgent: { color: 'text-danger-500', bgColor: 'bg-danger-100' }
  };

  const currentStatus = statusConfig[status] || statusConfig.pending;
  const currentPriority = priorityConfig[priority] || priorityConfig.medium;
  const StatusIcon = currentStatus.icon;

  // Check if overdue
  const isOverdue = dueDate && new Date(dueDate) < new Date() && status !== 'completed';
  const displayStatus = isOverdue ? 'overdue' : status;

  const formatDate = (date) => {
    if (!date) return null;
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (date) => {
    if (!date) return null;
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <motion.div
      className={`bg-white rounded-lg border ${currentStatus.borderColor} shadow-sm hover:shadow-md transition-all duration-200 ${className}`}
      whileHover={{ y: -2 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      {...props}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <StatusIcon 
              className={`w-5 h-5 ${currentStatus.color}`} 
              onClick={() => onComplete && onComplete(id)}
              style={{ cursor: onComplete ? 'pointer' : 'default' }}
            />
            <h3 className="font-semibold text-gray-900 line-clamp-2">{title}</h3>
          </div>
          
          <div className="flex items-center space-x-1">
            {onEdit && (
              <button
                onClick={() => onEdit(id)}
                className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
              </button>
            )}
                    {typeof onAIAdvice === 'function' && (
                      <button
                        onClick={() => onAIAdvice(id)}
                        title="Get AI Advice"
                        className="p-1 text-gray-400 hover:text-indigo-500 transition-colors"
                      >
                        <MessageSquare className="w-4 h-4" />
                      </button>
                    )}
            {onDelete && (
              <button
                onClick={() => onDelete(id)}
                className="p-1 text-gray-400 hover:text-danger-500 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Description */}
        {description && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{description}</p>
        )}

        {/* Metadata */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-3">
            {/* Priority Badge */}
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${currentPriority.bgColor} ${currentPriority.color}`}>
              {priority}
            </span>

            {/* Type Badge */}
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
              {type}
            </span>

            {/* Streak for habits */}
            {type === 'habit' && streak > 0 && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-600">
                🔥 {streak} day{streak !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {/* Due Date */}
          {dueDate && (
            <div className="text-gray-500">
              {formatDate(dueDate)}
              {formatTime(dueDate) && (
                <span className="ml-1 text-xs">{formatTime(dueDate)}</span>
              )}
            </div>
          )}
        </div>

        {/* Completion Date */}
        {completedAt && (
          <div className="mt-2 text-xs text-success-600">
            Completed on {formatDate(completedAt)}
          </div>
        )}

        {/* AI Advice Button */}
        {typeof onAIAdvice === 'function' && (
          <button
            onClick={() => onAIAdvice(id)}
            disabled={aiLoading}
            className="mt-4 px-3 py-1 rounded-md text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition-colors flex items-center justify-center"
          >
            {aiLoading ? 'Asking AI...' : 'Ask AI'}
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default TaskCard;
