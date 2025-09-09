import { ParseResumeResponse, ClearCacheRequest, ClearCacheResponse } from '../types';

const EXTRACTOR_API_BASE_URL = 'http://localhost:5296';
const PROFILER_API_BASE_URL = 'http://localhost:8000';

export class ApiService {
  static async scanProfiles(
    criteria: Record<string, any>,
  ): Promise<any> {
    const response = await fetch(`${EXTRACTOR_API_BASE_URL}/api/ProfileScan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(criteria),
    });

    if (response.ok) {
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      if (data.summary) {
        console.log('📊 Result:', data.summary);
      }

      return data;
    } else {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.error || 'Failed to fetch results. Please try again.';
      throw new Error(errorMessage);
    }
  }

  static async parseResumes(
    dirPath: string, 
    query: string, 
    forceAnalyze: boolean = false
  ): Promise<ParseResumeResponse> {
    const response = await fetch(`${PROFILER_API_BASE_URL}/parse-resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dirPath,
        query,
        forceAnalyze,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      // Log performance info for large datasets
      if (data.summary && data.summary.total_resumes_processed > 50) {
        console.log('📊 Performance Summary:', data.summary);
      }

      return data;
    } else {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.error || 'Failed to fetch results. Please try again.';
      throw new Error(errorMessage);
    }
  }

  static async clearCache(request: ClearCacheRequest): Promise<ClearCacheResponse> {
    const response = await fetch(`${PROFILER_API_BASE_URL}/clear-cache`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}
