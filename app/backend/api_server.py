# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

import os
import shutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
# Updated imports after modular refactor
from parser import ResumeParser, clear_cache  # type: ignore
from parser.config import CACHE_DIR, VECTOR_DB_DIR  # type: ignore

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; update with specific domains for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

agent = ResumeParser()  # Initialize AI agent

@app.post("/parse-resume")
async def parse_resume(request: Request):
    request_data = await request.json()
    directory_path = request_data.get("dirPath")
    query_string = request_data.get("query")
    force_analyze = request_data.get("forceAnalyze", False)
    
    print(f"📨 Received request to parse resumes in directory: {directory_path}")
    print(f"🔍 Query: {query_string}")
    print(f"🔥 Force analyze: {force_analyze}")
    
    if not directory_path or not query_string:
        return {"error": "Both 'directory_path' and 'query_string' are required."}
    
    try:
        result, cache_info = agent.main(directory_path, query_string, force_analyze)
        
        # Enhanced response with performance metrics
        response_data = {
            "result": result, 
            "cache_info": cache_info,
            "summary": {
                "total_candidates": len(result),
                "total_resumes_processed": cache_info.get("total_resumes", 0),
                "resumes_after_filtering": cache_info.get("filtered_resumes", 0),
                "processing_time": cache_info.get("processing_time", 0),
                "used_cache": cache_info.get("gemini_cache_hit", False) or cache_info.get("vector_cache_hit", False)
            }
        }
        
        print(f"✅ Request completed: {len(result)} candidates found")
        return response_data
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return {"error": f"An error occurred while processing the request: {str(e)}"}

@app.post("/clear-cache")
async def clear_cache_endpoint(request: Request):
    """Clear cache files."""
    try:
        request_data = await request.json()
        cache_type = request_data.get("type", "all")  # "current" or "all"
        cache_key = request_data.get("cache_key", None)  # For clearing specific current cache
        
        if cache_type == "current" and cache_key:
            # Clear specific cache entry
            clear_cache(cache_key)
            print(f"🗑️ Current cache cleared via API: {cache_key[:12]}...")
            return {"success": True, "message": "Current cache cleared successfully"}
        elif cache_type == "all":
            # Clear all caches
            clear_cache()  # Clear all Gemini cache
            print("🗑️ All Gemini cache cleared via API")
            
            # Clear vector database
            if os.path.exists(VECTOR_DB_DIR):
                for file in os.listdir(VECTOR_DB_DIR):
                    file_path = os.path.join(VECTOR_DB_DIR, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"⚠️ Could not delete {file_path}: {e}")
                print("🗑️ All vector cache cleared via API")
            
            return {"success": True, "message": "All cache cleared successfully"}
        else:
            return {"success": False, "error": "Invalid cache type or missing cache key for current cache"}
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return {"success": False, "error": str(e)}
