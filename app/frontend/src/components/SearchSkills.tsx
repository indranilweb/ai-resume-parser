import React from 'react';
import { Search, ListRestart, Tag } from 'lucide-react';

interface SearchSkillsProps {
  skills: string;
  onSkillsChange: (skills: string) => void;
  onSearch: () => void;
  onForceAnalyze: () => void;
  isEnabled: boolean;
  isLoading: boolean;
}

const SearchSkills: React.FC<SearchSkillsProps> = ({
  skills,
  onSkillsChange,
  onSearch,
  onForceAnalyze,
  isEnabled,
  isLoading,
}) => {
  const handleKeyUp = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && isEnabled && !isLoading) {
      onSearch();
    }
  };

  return (
    <div 
      className={`space-y-4 transition-all duration-300 ${
        isEnabled ? 'opacity-100' : 'opacity-50 pointer-events-none'
      }`}
    >
      <label htmlFor="search-input" className="block text-sm font-medium text-gray-100 mb-3">
        <span className="flex items-center space-x-3">
          <span 
            className={`w-6 h-6 text-white rounded-md text-xs flex items-center justify-center font-semibold ${
              isEnabled ? 'bg-blue-600' : 'bg-gray-500'
            }`}
          >
            2
          </span>
          <Search className={`w-4 h-4 ${isEnabled ? 'text-blue-400' : 'text-gray-500'}`} />
          <span>Enter Skills to Search</span>
        </span>
      </label>
      <div className="flex space-x-3">
        <div className="relative flex-1">
          <Tag className="text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none w-4 h-4" />
          <input
            type="text"
            id="search-input"
            value={skills}
            onChange={(e) => onSkillsChange(e.target.value)}
            onKeyUp={handleKeyUp}
            disabled={!isEnabled || isLoading}
            className="w-full pl-10 pr-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm font-mono"
            placeholder="e.g., Angular, .NET, C#, React, Python"
          />
        </div>
        <button
          onClick={onSearch}
          disabled={!isEnabled || isLoading}
          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Search className="w-4 h-4" />
          <span>Search</span>
        </button>
        <button
          onClick={onForceAnalyze}
          disabled={!isEnabled || isLoading}
          title="Force fresh analysis, bypassing cache"
          className="px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ListRestart className="w-5 h-5" />
          <span>Force</span>
        </button>
      </div>
    </div>
  );
};

export default SearchSkills;
