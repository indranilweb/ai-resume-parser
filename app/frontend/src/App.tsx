import React, { useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import Extractor from './components/Extractor';
import Profiler from './components/Profiler';
import { CacheInfo } from './types';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'extractor' | 'profiler'>('extractor');
  const [cacheInfo] = useState<CacheInfo | null>(null);

  return (
    <ThemeProvider>
      <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen font-sans transition-colors duration-200">
        <div className="container mx-auto px-4 py-6 max-w-7xl">
          {/* Header Section */}
          <div className="border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 p-6 mb-6">
            <Header resumeCount={cacheInfo?.total_resumes || 0} />
          </div>

          {/* Tab Navigation */}
          <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

          <main>
            {/* Tab Content */}
            {activeTab === 'extractor' && <Extractor />}
            {activeTab === 'profiler' && <Profiler />}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
};

export default App;
