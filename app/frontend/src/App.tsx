import React, { useState } from 'react';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import Extractor from './components/Extractor';
import Profiler from './components/Profiler';
import { CacheInfo } from './types';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'extractor' | 'profiler'>('extractor');
  const [cacheInfo] = useState<CacheInfo | null>(null);

  return (
    <div className="bg-gray-900 text-gray-100 min-h-screen font-sans">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header Section */}
        <div className="border border-gray-700 rounded-lg bg-gray-800 p-6 mb-6">
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
  );
};

export default App;
