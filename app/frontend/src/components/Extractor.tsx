import React, { useState } from 'react';
import { Download, FolderTree, Wrench, Award, MapPin, CheckCircle, XCircle } from 'lucide-react';
import MultiSelectDropdown from './MultiSelectDropdown';
import LoadingIndicator from './LoadingIndicator';
import { ApiService } from '../services/api';
import { ScanProfilesResponse } from '../types';

const Extractor: React.FC = () => {
  const [skillFamily, setSkillFamily] = useState<string>('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedGrades, setSelectedGrades] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [responseMessage, setResponseMessage] = useState<string>('');
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const skillOptions = ['.NET', '.NET Core', 'Angular', 'Python', 'AWS'];
  const gradeOptions = ['P', 'PAT', 'PA', 'A', 'SA', 'M', 'SM'];
  const locationOptions = ['Pune', 'Kolkata', 'Chennai', 'Hyderabad', 'Bangalore'];

  const handleDownload = async () => {
    const criteria = {
      skill_family: skillFamily,
      skill: selectedSkills?.join(', '),
      grade: selectedGrades?.join(', '),
      locations: selectedLocations?.join(', '),
    };
    console.log('Download clicked:', criteria);
    
    setIsLoading(true);
    setResponseMessage('');
    setIsSuccess(false);
    
    try {
      const response: ScanProfilesResponse = await ApiService.scanProfiles(criteria);
      console.log('Download completed:', response);
      
      if (response.result.is_success) {
        setIsSuccess(true);
        setResponseMessage(`Success: ${response.result.status_message}. Downloaded ${response.result.total_profiles} profiles.`);
      } else {
        setIsSuccess(false);
        setResponseMessage(response.result.status_message);
      }
    } catch (error) {
      console.error('Download failed:', error);
      setIsSuccess(false);
      setResponseMessage(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 p-6 transition-colors duration-200">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Resume Extractor</h2>
      <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">
        Extract specific information from resumes based on your criteria.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skill Family */}
        <div className="space-y-4">
          <label htmlFor="skillFamily" className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
            <span className="flex items-center space-x-3">
              <FolderTree className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Skill Family</span>
            </span>
          </label>
          <div className="relative">
            <input
              type="text"
              id="skillFamily"
              value={skillFamily}
              onChange={(e) => setSkillFamily(e.target.value)}
              placeholder="e.g., Software Development, Marketing"
              className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-md text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm transition-colors duration-200"
            />
          </div>
        </div>

        {/* Skill */}
        <MultiSelectDropdown
          options={skillOptions}
          selectedOptions={selectedSkills}
          onSelectionChange={setSelectedSkills}
          placeholder="Select skills..."
          label="Skill"
          icon={<Wrench className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
        />

        {/* Grade */}
        <MultiSelectDropdown
          options={gradeOptions}
          selectedOptions={selectedGrades}
          onSelectionChange={setSelectedGrades}
          placeholder="Select grades..."
          label="Grade"
          icon={<Award className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
        />

        {/* Location */}
        <MultiSelectDropdown
          options={locationOptions}
          selectedOptions={selectedLocations}
          onSelectionChange={setSelectedLocations}
          placeholder="Select locations..."
          label="Location"
          icon={<MapPin className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
        />
      </div>

      {/* Download Button */}
      <div className="mt-6">
        <button
          onClick={handleDownload}
          disabled={isLoading}
          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          <span>{isLoading ? 'Downloading...' : 'Download'}</span>
        </button>
      </div>

      {/* Loading Indicator */}
      {isLoading && (
        <LoadingIndicator 
          isVisible={isLoading} 
          message="Scanning profiles based on your criteria..." 
        />
      )}

      {/* Response Message */}
      {responseMessage && !isLoading && (
        <div className={`mt-4 p-3 rounded-md text-sm flex items-start space-x-2 ${
          isSuccess 
            ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200' 
            : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200'
        }`}>
          {isSuccess ? (
            <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          )}
          <span>{responseMessage}</span>
        </div>
      )}
    </div>
  );
};

export default Extractor;
