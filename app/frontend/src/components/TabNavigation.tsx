import React from 'react';
import { FileDown, UserSearch } from 'lucide-react';

interface TabNavigationProps {
  activeTab: 'extractor' | 'profiler';
  onTabChange: (tab: 'extractor' | 'profiler') => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="border-b border-gray-700 mb-6">
      <nav className="flex space-x-8">
        <button
          onClick={() => onTabChange('extractor')}
          className={`py-4 px-1 border-b-2 focus:shadow-none font-medium text-sm flex items-center space-x-2 ${
            activeTab === 'extractor'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-500'
          }`}
        >
          <FileDown className="w-4 h-4" />
          <span>Extractor</span>
        </button>
        <button
          onClick={() => onTabChange('profiler')}
          className={`py-4 px-1 border-b-2 focus:shadow-none font-medium text-sm flex items-center space-x-2 ${
            activeTab === 'profiler'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-500'
          }`}
        >
          <UserSearch className="w-4 h-4" />
          <span>Profiler</span>
        </button>
      </nav>
    </div>
  );
};

export default TabNavigation;
