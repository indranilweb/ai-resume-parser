# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from resume_parser_gemini import ResumeParser  # Import AI agent class

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
