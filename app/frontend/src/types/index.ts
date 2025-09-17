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

export interface ParseStats {
  successful_files: string[];
  failed_files: string[];
  total_files: number;
  success_count: number;
  failure_count: number;
}

export interface CacheInfo {
  cache_key: string;
  vector_cache_hit: boolean;
  genai_cache_hit: boolean;
  total_resumes: number;
  filtered_resumes: number;
  processing_time?: number;
  total_batches?: number;
  batches_processed?: number;
  parse_stats?: ParseStats;
}

export interface ParseResumeResponse {
  result: Resume[];
  cache_info: CacheInfo;
}

export interface ScanProfilesResponse {
  message: string;
  result: {
    is_success: boolean;
    profiles: Array<object>;
    status_message: string;
    total_profiles: number;
  };
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
