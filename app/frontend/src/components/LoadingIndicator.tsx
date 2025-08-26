import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  isVisible: boolean;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="flex justify-center items-center py-12">
      <div className="flex items-center space-x-3">
        <Loader2 className="text-blue-400 w-5 h-5 animate-spin" />
        <span className="text-gray-400 text-sm">Analyzing resumes...</span>
      </div>
    </div>
  );
};

export default LoadingIndicator;
