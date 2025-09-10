import React, { useState } from 'react';
import { Search, ListRestart, Tag, Maximize2, Minimize2 } from 'lucide-react';

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
  const [isExpanded, setIsExpanded] = useState(false);

  const handleKeyUp = (event: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && isEnabled && !isLoading && !event.shiftKey) {
      onSearch();
    }
  };

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div 
      className={`space-y-4 transition-all duration-300 ${
        isEnabled ? 'opacity-100' : 'opacity-50 pointer-events-none'
      }`}
    >
      <label htmlFor="search-input" className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
        <span className="flex items-center space-x-3">
          <span 
            className={`w-6 h-6 text-white rounded-md text-xs flex items-center justify-center font-semibold ${
              isEnabled ? 'bg-blue-600' : 'bg-gray-500'
            }`}
          >
            2
          </span>
          <Search className={`w-4 h-4 ${isEnabled ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'}`} />
          <span>{isExpanded ? 'Enter Detailed Job Requirements' : 'Enter Skills to Search'}</span>
        </span>
      </label>
      <div className="flex items-start space-x-3">
        <div className="relative flex-1">
          <Tag className="text-gray-500 dark:text-gray-400 absolute left-3 top-3 pointer-events-none w-4 h-4" />
          {isExpanded ? (
            <textarea
              id="search-input"
              value={skills}
              onChange={(e) => onSkillsChange(e.target.value)}
              onKeyUp={handleKeyUp}
              disabled={!isEnabled || isLoading}
              rows={4}
              className="w-full pl-10 pr-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-md text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm resize-y transition-colors duration-200"
              placeholder="Describe the job requirements in detail. Include skills like Angular, .NET, C#, React, Python, responsibilities, experience level, soft skills, etc."
            />
          ) : (
            <input
              type="text"
              id="search-input"
              value={skills}
              onChange={(e) => onSkillsChange(e.target.value)}
              onKeyUp={handleKeyUp}
              disabled={!isEnabled || isLoading}
              className="w-full pl-10 pr-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-md text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm font-mono transition-colors duration-200"
              placeholder="e.g., Angular, .NET, C#, React, Python"
            />
          )}
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleToggleExpand}
            disabled={!isEnabled || isLoading}
            title={isExpanded ? "Switch to simple skills input" : "Switch to detailed job description"}
            className="px-3 py-2 bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-white text-sm font-medium rounded-md hover:bg-gray-400 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 dark:focus:ring-gray-600 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 transition-colors flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onSearch}
            disabled={!isEnabled || isLoading}
            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Search className="w-4 h-4" />
            <span>Search</span>
          </button>
          <button
            onClick={onForceAnalyze}
            disabled={!isEnabled || isLoading}
            title="Force fresh analysis, bypassing cache"
            className="px-4 py-2 bg-gray-300 dark:bg-gray-700 text-green-600 dark:text-green-500 text-sm font-medium rounded-md hover:bg-green-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ListRestart className="w-5 h-5" />
            <span>Force</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchSkills;
