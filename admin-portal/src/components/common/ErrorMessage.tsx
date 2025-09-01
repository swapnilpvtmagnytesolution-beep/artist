import React from 'react';
import { motion } from 'framer-motion';
import {
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

type ErrorType = 'error' | 'warning' | 'info' | 'success';

interface ErrorMessageProps {
  message: string;
  type?: ErrorType;
  title?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
  showIcon?: boolean;
  retryText?: string;
  dismissText?: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  type = 'error',
  title,
  onRetry,
  onDismiss,
  className = '',
  showIcon = true,
  retryText = 'Try Again',
  dismissText = 'Dismiss',
}) => {
  const getIcon = () => {
    switch (type) {
      case 'error':
        return XCircleIcon;
      case 'warning':
        return ExclamationTriangleIcon;
      case 'info':
        return InformationCircleIcon;
      case 'success':
        return CheckCircleIcon;
      default:
        return XCircleIcon;
    }
  };

  const getColors = () => {
    switch (type) {
      case 'error':
        return {
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-red-200 dark:border-red-800',
          icon: 'text-red-400 dark:text-red-500',
          title: 'text-red-800 dark:text-red-200',
          message: 'text-red-700 dark:text-red-300',
          button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-yellow-200 dark:border-yellow-800',
          icon: 'text-yellow-400 dark:text-yellow-500',
          title: 'text-yellow-800 dark:text-yellow-200',
          message: 'text-yellow-700 dark:text-yellow-300',
          button: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500',
        };
      case 'info':
        return {
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-blue-200 dark:border-blue-800',
          icon: 'text-blue-400 dark:text-blue-500',
          title: 'text-blue-800 dark:text-blue-200',
          message: 'text-blue-700 dark:text-blue-300',
          button: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
        };
      case 'success':
        return {
          bg: 'bg-green-50 dark:bg-green-900/20',
          border: 'border-green-200 dark:border-green-800',
          icon: 'text-green-400 dark:text-green-500',
          title: 'text-green-800 dark:text-green-200',
          message: 'text-green-700 dark:text-green-300',
          button: 'bg-green-600 hover:bg-green-700 focus:ring-green-500',
        };
      default:
        return {
          bg: 'bg-gray-50 dark:bg-gray-900/20',
          border: 'border-gray-200 dark:border-gray-800',
          icon: 'text-gray-400 dark:text-gray-500',
          title: 'text-gray-800 dark:text-gray-200',
          message: 'text-gray-700 dark:text-gray-300',
          button: 'bg-gray-600 hover:bg-gray-700 focus:ring-gray-500',
        };
    }
  };

  const Icon = getIcon();
  const colors = getColors();

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className={`rounded-lg border p-4 ${colors.bg} ${colors.border} ${className}`}
    >
      <div className="flex items-start">
        {showIcon && (
          <div className="flex-shrink-0">
            <Icon className={`h-5 w-5 ${colors.icon}`} aria-hidden="true" />
          </div>
        )}
        <div className={`${showIcon ? 'ml-3' : ''} flex-1`}>
          {title && (
            <h3 className={`text-sm font-medium ${colors.title} mb-1`}>
              {title}
            </h3>
          )}
          <div className={`text-sm ${colors.message}`}>
            {message}
          </div>
          {(onRetry || onDismiss) && (
            <div className="mt-4 flex space-x-3">
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white ${colors.button} focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200`}
                >
                  <ArrowPathIcon className="w-4 h-4 mr-1" />
                  {retryText}
                </button>
              )}
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
                >
                  {dismissText}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Specialized error components
export const NetworkError: React.FC<{
  onRetry?: () => void;
  className?: string;
}> = ({ onRetry, className }) => {
  return (
    <ErrorMessage
      type="error"
      title="Network Error"
      message="Unable to connect to the server. Please check your internet connection and try again."
      onRetry={onRetry}
      className={className}
    />
  );
};

export const NotFoundError: React.FC<{
  resource?: string;
  className?: string;
}> = ({ resource = 'resource', className }) => {
  return (
    <ErrorMessage
      type="warning"
      title="Not Found"
      message={`The requested ${resource} could not be found.`}
      className={className}
    />
  );
};

export const PermissionError: React.FC<{
  className?: string;
}> = ({ className }) => {
  return (
    <ErrorMessage
      type="error"
      title="Permission Denied"
      message="You don't have permission to access this resource."
      className={className}
    />
  );
};

export const ValidationError: React.FC<{
  errors: string[];
  className?: string;
}> = ({ errors, className }) => {
  return (
    <ErrorMessage
      type="error"
      title="Validation Error"
      message={String(
        <ul className="list-disc list-inside space-y-1">
          {errors.map((error, index) => (
            <li key={index}>{error}</li>
          ))}
        </ul>
      )}
      className={className}
    />
  );
};

// Success message component
export const SuccessMessage: React.FC<{
  message: string;
  title?: string;
  onDismiss?: () => void;
  className?: string;
}> = ({ message, title, onDismiss, className }) => {
  return (
    <ErrorMessage
      type="success"
      title={title}
      message={message}
      onDismiss={onDismiss}
      className={className}
      dismissText="OK"
    />
  );
};

// Info message component
export const InfoMessage: React.FC<{
  message: string;
  title?: string;
  onDismiss?: () => void;
  className?: string;
}> = ({ message, title, onDismiss, className }) => {
  return (
    <ErrorMessage
      type="info"
      title={title}
      message={message}
      onDismiss={onDismiss}
      className={className}
    />
  );
};

export default ErrorMessage;