import React from 'react';
import { FileText } from 'lucide-react';

interface HeaderProps {
  resumeCount: number;
}

const Header: React.FC<HeaderProps> = ({ resumeCount }) => {
  return (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-pink-500 rounded-lg flex items-center justify-center">
          <FileText className="text-white w-4 h-4" />
        </div>
        <h1 className="text-2xl font-semibold text-gray-100">
          <span className="text-blue-400">AI-powered</span> Resume Parser
        </h1>
      </div>
      {resumeCount > 0 && (
        <div 
          id="resume-count" 
          className="text-xs text-white font-medium border border-gray-500 rounded-2xl px-2 py-1 resume-count-animate"
        >
          <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1"></span>
          <span>{resumeCount}</span> resume(s) analyzed
        </div>
      )}
    </div>
  );
};

export default Header;
