import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  isVisible: boolean;
  forceAnalyze?: boolean;
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  isVisible, 
  forceAnalyze = false,
  message 
}) => {
  if (!isVisible) return null;

  const defaultMessage = forceAnalyze 
    ? 'Force analyzing resumes... This may take a while for large datasets.' 
    : 'Processing resumes... Please wait.';

  return (
    <div className="flex justify-center items-center py-12">
      <div className="flex flex-col items-center space-y-3">
        <div className="flex items-center space-x-3">
          <Loader2 className="text-blue-600 dark:text-blue-400 w-5 h-5 animate-spin" />
          <span className="text-gray-600 dark:text-gray-400 text-sm">Analyzing resumes...</span>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-500 max-w-md text-center">
          {message || defaultMessage}
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
