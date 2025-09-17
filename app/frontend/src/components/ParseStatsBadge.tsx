import React, { useState } from 'react';
import { FileCheck, FileX, Info } from 'lucide-react';
import { ParseStats } from '../types';
import ParseStatsModal from './ParseStatsModal';

interface ParseStatsBadgeProps {
  parseStats: ParseStats | null;
}

const ParseStatsBadge: React.FC<ParseStatsBadgeProps> = ({ parseStats }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!parseStats || parseStats.total_files === 0) {
    return null;
  }

  const { success_count, failure_count, total_files } = parseStats;

  return (
    <>
      <div 
        className="group inline-flex items-center space-x-2 bg-transparent dark:bg-transparent border border-gray-300 dark:border-gray-600 rounded-full px-3 py-1.5 cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-800/30 hover:border-blue-200 dark:hover:border-blue-700 transition-all duration-300"
        onClick={() => setIsModalOpen(true)}
        title="Click to view parsing details"
      >
        <div className="flex items-center space-x-1">
          <div className="relative">
            <FileCheck className="w-3.5 h-3.5 text-green-500" />
          </div>
          <span className="text-green-600 dark:text-green-400 font-semibold text-xs">{success_count}</span>
        </div>
        
        {failure_count > 0 && (
          <>
            <div className="w-px h-3 bg-gray-300 dark:bg-gray-600"></div>
            <div className="flex items-center space-x-1">
              <FileX className="w-3.5 h-3.5 text-red-500" />
              <span className="text-red-600 dark:text-red-400 font-semibold text-xs">{failure_count}</span>
            </div>
          </>
        )}
        
        <div className="flex items-center space-x-1 text-gray-500 dark:text-gray-400">
          <span className="text-xs">of {total_files} analyzed</span>
          <Info className="w-3 h-3 group-hover:text-blue-500 transition-colors duration-200" />
        </div>
      </div>

      <ParseStatsModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        parseStats={parseStats}
      />
    </>
  );
};

export default ParseStatsBadge;
