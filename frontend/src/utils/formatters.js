/**
 * Utility functions for formatting data
 */

/**
 * Format currency amount
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code (default: 'INR')
 * @param {string} locale - The locale (default: 'en-IN')
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency = 'INR', locale = 'en-IN') => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '₹0.00';
  }

  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch (error) {
    // Fallback formatting
    return `₹${parseFloat(amount).toFixed(2)}`;
  }
};

/**
 * Format percentage
 * @param {number} value - The value to format as percentage
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0%';
  }

  return `${parseFloat(value).toFixed(decimals)}%`;
};

/**
 * Format date
 * @param {Date|string} date - The date to format
 * @param {string} format - The format style ('short', 'long', 'relative', 'time')
 * @param {string} locale - The locale (default: 'en-IN')
 * @returns {string} Formatted date string
 */
export const formatDate = (date, format = 'short', locale = 'en-IN') => {
  if (!date) return 'N/A';

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return 'Invalid Date';
  }

  try {
    switch (format) {
      case 'short':
        return new Intl.DateTimeFormat(locale, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        }).format(dateObj);

      case 'long':
        return new Intl.DateTimeFormat(locale, {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        }).format(dateObj);

      case 'time':
        return new Intl.DateTimeFormat(locale, {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        }).format(dateObj);

      case 'datetime':
        return new Intl.DateTimeFormat(locale, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        }).format(dateObj);

      case 'relative':
        return formatRelativeTime(dateObj);

      default:
        return dateObj.toLocaleDateString(locale);
    }
  } catch (error) {
    // Fallback formatting
    return dateObj.toLocaleDateString();
  }
};

/**
 * Format relative time (e.g., "2 hours ago", "3 days ago")
 * @param {Date} date - The date to format
 * @returns {string} Relative time string
 */
const formatRelativeTime = (date) => {
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }

  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks > 1 ? 's' : ''} ago`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths > 1 ? 's' : ''} ago`;
  }

  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} year${diffInYears > 1 ? 's' : ''} ago`;
};

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted file size string
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format duration in seconds to human readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration string
 */
export const formatDuration = (seconds) => {
  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes < 60) {
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes > 0) {
    return `${hours}h ${remainingMinutes}m`;
  }

  return `${hours}h`;
};

/**
 * Format number with appropriate suffix (K, M, B)
 * @param {number} num - The number to format
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted number string
 */
export const formatNumber = (num, decimals = 1) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0';
  }

  if (num < 1000) {
    return num.toString();
  }

  if (num < 1000000) {
    return (num / 1000).toFixed(decimals) + 'K';
  }

  if (num < 1000000000) {
    return (num / 1000000).toFixed(decimals) + 'M';
  }

  return (num / 1000000000).toFixed(decimals) + 'B';
};

/**
 * Format phone number
 * @param {string} phone - The phone number to format
 * @param {string} country - The country code (default: 'IN')
 * @returns {string} Formatted phone number string
 */
export const formatPhoneNumber = (phone, country = 'IN') => {
  if (!phone) return 'N/A';

  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, '');

  if (country === 'IN') {
    // Indian phone number format: +91 98765 43210
    if (cleaned.length === 10) {
      return `+91 ${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
    } else if (cleaned.length === 12 && cleaned.startsWith('91')) {
      return `+91 ${cleaned.slice(2, 7)} ${cleaned.slice(7)}`;
    }
  }

  // Default formatting
  return phone;
};

/**
 * Format name (capitalize first letter of each word)
 * @param {string} name - The name to format
 * @returns {string} Formatted name string
 */
export const formatName = (name) => {
  if (!name) return '';

  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Format time from minutes to HH:MM format
 * @param {number} minutes - Total minutes
 * @returns {string} Formatted time string
 */
export const formatTimeFromMinutes = (minutes) => {
  if (minutes === null || minutes === undefined || isNaN(minutes)) {
    return '00:00';
  }

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
};

/**
 * Format progress percentage with color classes
 * @param {number} progress - Progress value (0-100)
 * @returns {object} Object with percentage and color classes
 */
export const formatProgress = (progress) => {
  if (progress >= 80) {
    return {
      percentage: progress,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      status: 'Excellent'
    };
  } else if (progress >= 60) {
    return {
      percentage: progress,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      status: 'Good'
    };
  } else if (progress >= 40) {
    return {
      percentage: progress,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      status: 'Fair'
    };
  } else {
    return {
      percentage: progress,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      status: 'Needs Improvement'
    };
  }
};

/**
 * Format status with appropriate styling
 * @param {string} status - The status to format
 * @returns {object} Object with status and styling classes
 */
export const formatStatus = (status) => {
  const statusMap = {
    'completed': {
      text: 'Completed',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      borderColor: 'border-green-200'
    },
    'in_progress': {
      text: 'In Progress',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      borderColor: 'border-blue-200'
    },
    'pending': {
      text: 'Pending',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      borderColor: 'border-yellow-200'
    },
    'on_hold': {
      text: 'On Hold',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      borderColor: 'border-orange-200'
    },
    'cancelled': {
      text: 'Cancelled',
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      borderColor: 'border-red-200'
    }
  };

  return statusMap[status] || {
    text: status || 'Unknown',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200'
  };
};

/**
 * Format priority with appropriate styling
 * @param {string} priority - The priority to format
 * @returns {object} Object with priority and styling classes
 */
export const formatPriority = (priority) => {
  const priorityMap = {
    'low': {
      text: 'Low',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      borderColor: 'border-green-200'
    },
    'medium': {
      text: 'Medium',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      borderColor: 'border-yellow-200'
    },
    'high': {
      text: 'High',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      borderColor: 'border-orange-200'
    },
    'urgent': {
      text: 'Urgent',
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      borderColor: 'border-red-200'
    }
  };

  return priorityMap[priority] || {
    text: priority || 'Unknown',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200'
  };
};
