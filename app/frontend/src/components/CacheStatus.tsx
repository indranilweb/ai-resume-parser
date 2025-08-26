import React from 'react';
import { Database, Zap, Trash, Trash2 } from 'lucide-react';
import { CacheInfo } from '../types';

interface CacheStatusProps {
  cacheInfo: CacheInfo | null;
  onClearCurrentCache: () => void;
  onClearAllCache: () => void;
}

const CacheStatus: React.FC<CacheStatusProps> = ({
  cacheInfo,
  onClearCurrentCache,
  onClearAllCache,
}) => {
  if (!cacheInfo) {
    return null;
  }

  return (
    <div className="border border-gray-700 rounded-lg bg-gray-800 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-2">
            {/* Vector cache indicator */}
            <div 
              className={`flex items-center space-x-2 px-2 py-1 rounded-2xl text-xs font-medium ${
                cacheInfo.vector_cache_hit ? 'cache-hit' : 'cache-miss'
              }`}
            >
              <Database className="w-3 h-3" />
              <span>Vector: {cacheInfo.vector_cache_hit ? 'Cached' : 'Fresh'}</span>
            </div>

            {/* Gemini cache indicator */}
            <div 
              className={`flex items-center space-x-2 px-2 py-1 rounded-2xl text-xs font-medium ${
                cacheInfo.gemini_cache_hit ? 'cache-hit' : 'cache-miss'
              }`}
            >
              <Zap className="w-3 h-3" />
              <span>Gemini: {cacheInfo.gemini_cache_hit ? 'Cached' : 'Fresh'}</span>
            </div>
          </div>

          <div className="flex items-center space-x-2 ml-4 pl-3 border-l border-gray-500">
            <div className="text-xs text-gray-400 font-medium mr-1">Clear Cache:</div>
            <button
              onClick={onClearCurrentCache}
              title="Clear current search cache"
              className="px-3 py-1 bg-amber-600 text-white text-xs font-medium rounded-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-1"
            >
              <Trash className="w-3 h-3" />
              <span>Current</span>
            </button>
            <button
              onClick={onClearAllCache}
              title="Clear all cache"
              className="px-3 py-1 bg-amber-600 text-white text-xs font-medium rounded-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-1"
            >
              <Trash2 className="w-3 h-3" />
              <span>All</span>
            </button>
          </div>
        </div>
        
        <div className="text-xs text-gray-400 font-mono">
          {cacheInfo.total_resumes} resumes → {cacheInfo.filtered_resumes} filtered
          {cacheInfo.processing_time && ` • ${cacheInfo.processing_time}s`}
          {cacheInfo.cache_key && ` • ${cacheInfo.cache_key}`}
        </div>
      </div>
    </div>
  );
};

export default CacheStatus;
