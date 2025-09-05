import React, { useState } from 'react';
import FolderSelection from './FolderSelection';
import SearchSkills from './SearchSkills';
import CacheStatus from './CacheStatus';
import LoadingIndicator from './LoadingIndicator';
import ResumeTable from './ResumeTable';
import ResumeDetailsModal from './ResumeDetailsModal';
import { Resume, CacheInfo } from '../types';
import { ApiService } from '../services/api';
import { sortResumesByScore } from '../utils/resume';

const Profiler: React.FC = () => {
  const [folderPath, setFolderPath] = useState<string>('');
  const [skills, setSkills] = useState<string>('');
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isStep2Enabled, setIsStep2Enabled] = useState<boolean>(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isForceAnalyze, setIsForceAnalyze] = useState<boolean>(false);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const handleFolderPathChange = (path: string) => {
    setFolderPath(path);
    setHasSearched(false);
    setIsStep2Enabled(path.trim() !== '');
  };

  const handleProceed = () => {
    if (folderPath.trim()) {
      setIsStep2Enabled(true);
    }
  };

  const handleSearch = async (forceAnalyze: boolean = false) => {
    if (!folderPath.trim() || !skills.trim()) {
      alert(folderPath.trim() ? 'Please enter at least one skill to search for.' : 'Please select a folder first.');
      return;
    }

    setIsLoading(true);
    setIsForceAnalyze(forceAnalyze);
    setResumes([]);
    setCacheInfo(null);
    setHasSearched(true);

    try {
      const response = await ApiService.parseResumes(folderPath, skills, forceAnalyze);
      const sortedResumes = sortResumesByScore(response.result);
      setResumes(sortedResumes);
      setCacheInfo(response.cache_info);
    } catch (error) {
      console.error('Failed to parse resumes:', error);
      alert(`An error occurred while searching for resumes: ${error instanceof Error ? error.message : 'Please check the console.'}`);
    } finally {
      setIsLoading(false);
      setIsForceAnalyze(false);
    }
  };

  const handleViewDetails = (resume: Resume) => {
    setSelectedResume(resume);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedResume(null);
  };

  const handleClearCurrentCache = async () => {
    if (!cacheInfo?.cache_key) {
      alert('No current cache to clear. Please perform a search first.');
      return;
    }

    if (confirm('Are you sure you want to clear the current search cache? This will remove the cache for the current folder and query combination.')) {
      try {
        const response = await ApiService.clearCache({
          type: 'current',
          cache_key: cacheInfo.cache_key
        });
        
        if (response.success) {
          alert(response.message);
          console.log('✅ Current cache cleared successfully');
        } else {
          alert(`Failed to clear cache: ${response.error}`);
        }
      } catch (error) {
        console.error('❌ Error clearing current cache:', error);
        alert('An error occurred while clearing current cache. Please check the console.');
      }
    }
  };

  const handleClearAllCache = async () => {
    if (confirm('Are you sure you want to clear ALL cache? This will remove all cached data including both GenAI and Vector cache.')) {
      try {
        const response = await ApiService.clearCache({ type: 'all' });
        
        if (response.success) {
          alert(response.message);
          console.log('✅ All cache cleared successfully');
          setCacheInfo(null);
        } else {
          alert(`Failed to clear cache: ${response.error}`);
        }
      } catch (error) {
        console.error('❌ Error clearing all cache:', error);
        alert('An error occurred while clearing all cache. Please check the console.');
      }
    }
  };

  return (
    <>
      {/* Controls Section */}
      <div className="border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 p-6 mb-6 transition-colors duration-200">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Resume Profiler</h2>
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">
          Find the right candidates by analyzing resumes with AI technology.
        </p>

        {/* Two Column Layout for Steps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Step 1: Folder Selection */}
          <FolderSelection
            folderPath={folderPath}
            onFolderPathChange={handleFolderPathChange}
            onProceed={handleProceed}
          />

          {/* Step 2: Search Skills */}
          <SearchSkills
            skills={skills}
            onSkillsChange={setSkills}
            onSearch={() => handleSearch(false)}
            onForceAnalyze={() => handleSearch(true)}
            isEnabled={isStep2Enabled}
            isLoading={isLoading}
          />
        </div>
      </div>

      <div className="space-y-6">
        {/* Cache Status Indicator */}
        {cacheInfo && (
          <CacheStatus
            cacheInfo={cacheInfo}
            onClearCurrentCache={handleClearCurrentCache}
            onClearAllCache={handleClearAllCache}
          />
        )}

        {/* Loading Indicator */}
        <LoadingIndicator isVisible={isLoading} forceAnalyze={isForceAnalyze} />

        {/* Results Section */}
        {!isLoading && (
          <ResumeTable
            resumes={resumes}
            onViewDetails={handleViewDetails}
            hasSearched={hasSearched}
            folderPath={folderPath}
          />
        )}
      </div>

      {/* Resume Details Modal */}
      <ResumeDetailsModal
        resume={selectedResume}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </>
  );
};

export default Profiler;
