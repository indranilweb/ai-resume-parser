export interface Resume {
  name: string;
  contact_number: string;
  last_3_companies: (string | null)[];
  top_5_technical_skills: string[];
  source_file: string;
  match_score?: number;
  years_of_experience?: number;
  score_breakdown?: string;
  summary?: string;
}

export interface CacheInfo {
  cache_key: string;
  vector_cache_hit: boolean;
  gemini_cache_hit: boolean;
  total_resumes: number;
  filtered_resumes: number;
  processing_time?: number;
  total_batches?: number;
  batches_processed?: number;
}

export interface ParseResumeResponse {
  result: Resume[];
  cache_info: CacheInfo;
}

export interface ClearCacheRequest {
  type: 'current' | 'all';
  cache_key?: string;
}

export interface ClearCacheResponse {
  success: boolean;
  message: string;
  error?: string;
}
