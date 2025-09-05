import React, { useState } from 'react';
import { Download, FolderTree, Wrench, Award, MapPin } from 'lucide-react';

const Extractor: React.FC = () => {
  const [skillFamily, setSkillFamily] = useState<string>('');
  const [skill, setSkill] = useState<string>('');
  const [grade, setGrade] = useState<string>('');
  const [location, setLocation] = useState<string>('');

  const handleDownload = () => {
    // Placeholder for API call
    console.log('Download clicked:', { skillFamily, skill, grade, location });
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
        <div className="space-y-4">
          <label htmlFor="skill" className="block text-sm font-medium text-gray-100 mb-3">
            <span className="flex items-center space-x-3">
              <Wrench className="w-4 h-4 text-blue-400" />
              <span>Skill</span>
            </span>
          </label>
          <div className="relative">
            <input
              type="text"
              id="skill"
              value={skill}
              onChange={(e) => setSkill(e.target.value)}
              placeholder="e.g., React, Python, SEO"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm"
            />
          </div>
        </div>

        {/* Grade */}
        <div className="space-y-4">
          <label htmlFor="grade" className="block text-sm font-medium text-gray-100 mb-3">
            <span className="flex items-center space-x-3">
              <Award className="w-4 h-4 text-blue-400" />
              <span>Grade</span>
            </span>
          </label>
          <div className="relative">
            <input
              type="text"
              id="grade"
              value={grade}
              onChange={(e) => setGrade(e.target.value)}
              placeholder="e.g., Senior, Junior, Mid-level"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm"
            />
          </div>
        </div>

        {/* Location */}
        <div className="space-y-4">
          <label htmlFor="location" className="block text-sm font-medium text-gray-100 mb-3">
            <span className="flex items-center space-x-3">
              <MapPin className="w-4 h-4 text-blue-400" />
              <span>Location</span>
            </span>
          </label>
          <div className="relative">
            <input
              type="text"
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., New York, Remote, Bangalore"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm"
            />
          </div>
        </div>
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
