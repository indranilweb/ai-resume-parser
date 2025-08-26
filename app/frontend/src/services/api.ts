import { ParseResumeResponse, ClearCacheRequest, ClearCacheResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiService {
  static async parseResumes(
    dirPath: string, 
    query: string, 
    forceAnalyze: boolean = false
  ): Promise<ParseResumeResponse> {
    const response = await fetch(`${API_BASE_URL}/parse-resume`, {
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

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  static async clearCache(request: ClearCacheRequest): Promise<ClearCacheResponse> {
    const response = await fetch(`${API_BASE_URL}/clear-cache`, {
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
