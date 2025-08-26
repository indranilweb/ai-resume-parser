import React from 'react';
import { User, Phone, Clock, Building, Code, TrendingUp, ExternalLink } from 'lucide-react';
import { Resume } from '../types';
import { getScoreBadgeClass, filterValidCompanies } from '../utils/resume';

interface ResumeTableProps {
  resumes: Resume[];
  onViewDetails: (resume: Resume) => void;
}

const ResumeTable: React.FC<ResumeTableProps> = ({ resumes, onViewDetails }) => {
  if (resumes.length === 0) {
    return (
      <div className="text-center border border-gray-700 rounded-lg bg-gray-800 py-12 px-6">
        <div className="flex flex-col items-center space-y-3">
          <Code className="text-gray-400 w-10 h-10" />
          <h3 className="text-lg font-medium text-gray-100">No matching resumes found</h3>
          <p className="text-gray-400">Try different skills or select another folder.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-gray-700 rounded-lg bg-gray-800 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-900 border-b border-gray-700">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center">
                  <User className="w-3 h-3 mr-2" />
                  Name
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center">
                  <Phone className="w-3 h-3 mr-2" />
                  Contact
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center">
                  <Clock className="w-3 h-3 mr-2" />
                  Exp
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center">
                  <Building className="w-3 h-3 mr-2" />
                  Companies
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center">
                  <Code className="w-3 h-3 mr-2" />
                  Key Skills
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-center">
                  <TrendingUp className="w-3 h-3 mr-2" />
                  Score
                </div>
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-center">
                  <ExternalLink className="w-3 h-3 mr-2" />
                  Details
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {resumes.map((resume, index) => (
              <ResumeTableRow 
                key={`${resume.source_file}-${index}`}
                resume={resume} 
                onViewDetails={onViewDetails} 
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

interface ResumeTableRowProps {
  resume: Resume;
  onViewDetails: (resume: Resume) => void;
}

const ResumeTableRow: React.FC<ResumeTableRowProps> = ({ resume, onViewDetails }) => {
  const score = resume.match_score || 0;
  const validCompanies = filterValidCompanies(resume.last_3_companies);

  return (
    <tr className="hover:bg-gray-50 hover:bg-opacity-5 transition-colors duration-150">
      <td className="px-4 py-3">
        <div className="font-medium text-gray-100 text-sm">{resume.name || '—'}</div>
      </td>
      <td className="px-4 py-3">
        <span className="text-gray-400 text-sm font-mono">{resume.contact_number || '—'}</span>
      </td>
      <td className="px-4 py-3">
        <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-600 bg-opacity-20 text-blue-400">
          {resume.years_of_experience || '—'} years
        </span>
      </td>
      <td className="px-4 py-3">
        <ul className="company-list space-y-1 text-xs">
          {validCompanies.length > 0 ? (
            validCompanies.map((company, index) => (
              <li key={index} className="text-gray-100">{company}</li>
            ))
          ) : (
            <li className="text-gray-400">—</li>
          )}
        </ul>
      </td>
      <td className="px-4 py-3">
        <div className="flex flex-wrap">
          {resume.top_5_technical_skills && resume.top_5_technical_skills.length > 0 ? (
            resume.top_5_technical_skills.map((skill, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium skill-badge mr-2 mb-1"
              >
                {skill}
              </span>
            ))
          ) : (
            <span className="text-gray-400 text-xs">—</span>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-center">
        <div className="flex flex-col items-center space-y-1">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${getScoreBadgeClass(score)}`}>
            {score}%
          </span>
        </div>
      </td>
      <td className="px-4 py-3 text-center">
        <div className="relative flex justify-center">
          <button 
            onClick={() => onViewDetails(resume)}
            className="details-btn flex items-center px-2 py-1 text-gray-400 hover:text-blue-400 hover:bg-gray-900 rounded transition-colors cursor-pointer"
          >
            <ExternalLink className="w-3 h-3 mr-2" />
            <span className="text-xs">View</span>
          </button>
        </div>
      </td>
    </tr>
  );
};

export default ResumeTable;
