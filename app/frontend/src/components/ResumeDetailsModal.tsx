import React from 'react';
import { X, User, Phone, FileText, Clock, TrendingUp, Building } from 'lucide-react';
import { Resume } from '../types';
import { getScoreColor, filterValidCompanies } from '../utils/resume';

interface ResumeDetailsModalProps {
  resume: Resume | null;
  isOpen: boolean;
  onClose: () => void;
}

const ResumeDetailsModal: React.FC<ResumeDetailsModalProps> = ({ 
  resume, 
  isOpen, 
  onClose 
}) => {
  if (!isOpen || !resume) return null;

  const score = resume.match_score || 0;
  const validCompanies = filterValidCompanies(resume.last_3_companies);

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg shadow-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto modal-scroll transition-colors duration-200">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Resume Details</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-100 focus:outline-none p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-900 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-6">
          {/* Header Section */}
          <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-6 mb-6 transition-colors duration-200">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{resume.name || 'Unknown'}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
                  <span className="flex items-center">
                    <Phone className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                    {resume.contact_number || 'Not provided'}
                  </span>
                  <span className="flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                    {resume.source_file || 'Unknown file'}
                  </span>
                  <span className="flex items-center">
                    <Clock className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                    {resume.years_of_experience || 0} years experience
                  </span>
                </div>
              </div>
              <div className="text-center">
                <div className={`text-4xl font-bold mb-1 ${getScoreColor(score)}`}>{score}%</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Match Score</div>
              </div>
            </div>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Score Breakdown */}
              <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 transition-colors duration-200">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                  Score Breakdown
                </h4>
                <div className="bg-white dark:bg-gray-800 rounded-md p-3 transition-colors duration-200">
                  <p className="text-gray-900 dark:text-gray-100 text-sm leading-relaxed">
                    {resume.score_breakdown || 'No detailed breakdown available.'}
                  </p>
                </div>
                <div className="mt-3 text-xs text-gray-600 dark:text-gray-400 border-t border-gray-300 dark:border-gray-700 pt-3">
                  <strong>Scoring Criteria:</strong> Skills Match (40%), Experience Level (30%), Industry/Domain Relevance (20%), Role Seniority (10%)
                </div>
              </div>

              {/* Key Skills */}
              <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 transition-colors duration-200">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                  <User className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                  Key Technical Skills
                </h4>
                <div className="flex flex-wrap">
                  {resume.top_5_technical_skills && resume.top_5_technical_skills.length > 0 ? (
                    resume.top_5_technical_skills.map((skill, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium skill-badge mr-2 mb-2"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-500 dark:text-gray-400 text-sm">No skills information available</span>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Professional Summary */}
              <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 transition-colors duration-200">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                  <User className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                  Professional Summary
                </h4>
                <div className="bg-white dark:bg-gray-800 rounded-md p-3 transition-colors duration-200">
                  <p className="text-gray-900 dark:text-gray-100 text-sm leading-relaxed">
                    {resume.summary || 'No summary available.'}
                  </p>
                </div>
              </div>

              {/* Past Organizations */}
              <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 transition-colors duration-200">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                  <Building className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400" />
                  Past Organizations
                </h4>
                <ul className="space-y-2">
                  {validCompanies.length > 0 ? (
                    validCompanies.map((company, index) => (
                      <li key={index} className="text-gray-900 dark:text-gray-100 text-sm mb-2 flex items-center">
                        <div className="w-1.5 h-1.5 bg-blue-600 dark:bg-blue-400 rounded-full mr-3"></div>
                        {company}
                      </li>
                    ))
                  ) : (
                    <li className="text-gray-500 dark:text-gray-400 text-sm">No company information available</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeDetailsModal;
