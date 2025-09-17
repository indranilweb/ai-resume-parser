import React from 'react';
import { X, FileCheck, FileX, AlertCircle } from 'lucide-react';
import { ParseStats } from '../types';

interface ParseStatsModalProps {
  isOpen: boolean;
  onClose: () => void;
  parseStats: ParseStats | null;
}

const ParseStatsModal: React.FC<ParseStatsModalProps> = ({ isOpen, onClose, parseStats }) => {
  if (!isOpen || !parseStats) return null;

  const { successful_files, failed_files, success_count, failure_count, total_files } = parseStats;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <AlertCircle className="text-white w-4 h-4" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Resume Parsing Statistics
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{total_files}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Files</div>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">{success_count}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Successfully Read</div>
            </div>
            <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">{failure_count}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Failed to Read</div>
            </div>
          </div>

          {/* File Lists - Side by Side */}
          {(successful_files.length > 0 || failed_files.length > 0) && (
            <div className="mb-4">
              {/* Headers */}
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="flex items-center space-x-2">
                  <FileCheck className="w-5 h-5 text-green-500" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Successfully Read Files ({success_count})
                  </h3>
                </div>
                <div className="flex items-center space-x-2">
                  <FileX className="w-5 h-5 text-red-500" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Failed to Read Files ({failure_count})
                  </h3>
                </div>
              </div>
              
              {/* Single Scrollable Section with Side-by-Side Content */}
              <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4 max-h-60 overflow-y-auto">
                <div className="grid grid-cols-2 gap-4 h-full">
                  {/* Successful Files Column */}
                  <div className="bg-green-50 dark:bg-green-900/10 rounded-lg p-3">
                    {successful_files.length > 0 ? (
                      <div className="space-y-1">
                        {successful_files.map((filename, index) => (
                          <div key={index} className="flex items-center space-x-2 text-sm">
                            <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
                            <span className="text-gray-700 dark:text-gray-300 break-all">{filename}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500 dark:text-gray-400 italic text-center py-4">
                        No successful files
                      </div>
                    )}
                  </div>
                  
                  {/* Failed Files Column */}
                  <div className="bg-red-50 dark:bg-red-900/10 rounded-lg p-3">
                    {failed_files.length > 0 ? (
                      <div className="space-y-1">
                        {failed_files.map((filename, index) => (
                          <div key={index} className="flex items-center space-x-2 text-sm">
                            <div className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0"></div>
                            <span className="text-gray-700 dark:text-gray-300 break-all">{filename}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500 dark:text-gray-400 italic text-center py-4">
                        No failed files
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
};

export default ParseStatsModal;
