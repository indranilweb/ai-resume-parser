import { Resume } from '../types';

export const getScoreColor = (score: number): string => {
  if (score >= 80) return 'text-green-400';
  if (score >= 65) return 'text-blue-400';
  if (score >= 50) return 'text-yellow-400';
  if (score >= 30) return 'text-orange-400';
  return 'text-red-400';
};

export const getScoreBadgeClass = (score: number): string => {
  if (score >= 80) return 'bg-green-600 text-green-100';
  if (score >= 65) return 'bg-blue-600 text-blue-100';
  if (score >= 50) return 'bg-yellow-600 text-yellow-100';
  if (score >= 30) return 'bg-orange-600 text-orange-100';
  return 'bg-red-600 text-red-100';
};

export const getScoreIcon = (score: number): string => {
  if (score >= 80) return 'fas fa-star';
  if (score >= 65) return 'fas fa-thumbs-up';
  if (score >= 50) return 'fas fa-check';
  if (score >= 30) return 'fas fa-exclamation';
  return 'fas fa-times';
};

export const sortResumesByScore = (resumes: Resume[]): Resume[] => {
  return [...resumes].sort((a, b) => {
    const scoreA = a.match_score || 0;
    const scoreB = b.match_score || 0;
    return scoreB - scoreA; // Descending order (highest score first)
  });
};

export const filterValidCompanies = (companies: (string | null)[]): string[] => {
  return companies.filter(company => 
    company && company.toLowerCase() !== 'null'
  ) as string[];
};
