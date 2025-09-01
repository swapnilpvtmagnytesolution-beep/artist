import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = '',
  text,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white',
    gray: 'text-gray-400',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <motion.div
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
        className={`${sizeClasses[size]} ${colorClasses[color]}`}
      >
        <svg
          className="animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </motion.div>
      {text && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`mt-2 ${textSizeClasses[size]} ${colorClasses[color]} font-medium`}
        >
          {text}
        </motion.p>
      )}
    </div>
  );
};

// Overlay spinner for full-screen loading
export const OverlaySpinner: React.FC<{
  text?: string;
  className?: string;
}> = ({ text = 'Loading...', className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
        <LoadingSpinner size="lg" text={text} />
      </div>
    </motion.div>
  );
};

// Inline spinner for buttons
export const ButtonSpinner: React.FC<{
  size?: 'sm' | 'md';
  className?: string;
}> = ({ size = 'sm', className = '' }) => {
  return (
    <LoadingSpinner
      size={size}
      color="white"
      className={`${className}`}
    />
  );
};

// Page loading spinner
export const PageSpinner: React.FC<{
  text?: string;
}> = ({ text = 'Loading page...' }) => {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="xl" text={text} />
    </div>
  );
};

export default LoadingSpinner;