import React from 'react';
import { FileText } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

interface HeaderProps {}

const Header: React.FC<HeaderProps> = () => {
  return (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-pink-500 rounded-lg flex items-center justify-center">
          <FileText className="text-white w-4 h-4" />
        </div>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          <span className="text-blue-600 dark:text-blue-400">AI-powered</span> Resume Screener
        </h1>
      </div>
      <div className="flex items-center space-x-4">
        <ThemeToggle />
      </div>
    </div>
  );
};

export default Header;
