# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

import os
import shutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from resume_parser_gemini import ResumeParser, clear_cache, CACHE_DIR, VECTOR_DB_DIR  # Import AI agent class

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
    print(f"Received request to parse resumes in directory: {directory_path} with query: {query_string}, force: {force_analyze}")
    if not directory_path or not query_string:
        return {"error": "Both 'directory_path' and 'query_string' are required."}
    
    result, cache_info = agent.main(directory_path, query_string, force_analyze)
    return {"result": result, "cache_info": cache_info}

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
