import React, { useState } from 'react';
import { Download, FolderTree, Wrench, Award, MapPin } from 'lucide-react';
import MultiSelectDropdown from './MultiSelectDropdown';

const Extractor: React.FC = () => {
  const [skillFamily, setSkillFamily] = useState<string>('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedGrades, setSelectedGrades] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);

  const skillOptions = ['.NET', '.NET Core', 'Angular', 'Python', 'AWS'];
  const gradeOptions = ['P', 'PAT', 'PA', 'A', 'SA', 'M', 'SM'];
  const locationOptions = ['Pune', 'Kolkata', 'Chennai', 'Hyderabad', 'Bangalore'];

  const handleDownload = () => {
    // Placeholder for API call
    console.log('Download clicked:', { skillFamily, skills: selectedSkills, grades: selectedGrades, locations: selectedLocations });
    // TODO: Implement API call
  };

  return (
    <div className="border border-gray-700 rounded-lg bg-gray-800 p-6">
      <h2 className="text-xl font-semibold text-gray-100 mb-4">Resume Extractor</h2>
      <p className="text-gray-400 text-sm mb-6">
        Extract specific information from resumes based on your criteria.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skill Family */}
        <div className="space-y-4">
          <label htmlFor="skillFamily" className="block text-sm font-medium text-gray-100 mb-3">
            <span className="flex items-center space-x-3">
              <FolderTree className="w-4 h-4 text-blue-400" />
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
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm"
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
          icon={<Wrench className="w-4 h-4 text-blue-400" />}
        />

        {/* Grade */}
        <MultiSelectDropdown
          options={gradeOptions}
          selectedOptions={selectedGrades}
          onSelectionChange={setSelectedGrades}
          placeholder="Select grades..."
          label="Grade"
          icon={<Award className="w-4 h-4 text-blue-400" />}
        />

        {/* Location */}
        <MultiSelectDropdown
          options={locationOptions}
          selectedOptions={selectedLocations}
          onSelectionChange={setSelectedLocations}
          placeholder="Select locations..."
          label="Location"
          icon={<MapPin className="w-4 h-4 text-blue-400" />}
        />
      </div>

      {/* Download Button */}
      <div className="mt-6">
        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          <span>Download</span>
        </button>
      </div>
    </div>
  );
};

export default Extractor;
