# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

import os
import shutil
import subprocess
import platform
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
                "used_cache": cache_info.get("genai_cache_hit", False) or cache_info.get("vector_cache_hit", False)
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
            clear_cache()  # Clear all GenAI cache
            print("🗑️ All GenAI cache cleared via API")
            
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

@app.post("/open-email")
async def open_email_with_attachments(request: Request):
    """Open default email client with resume attachments."""
    try:
        request_data = await request.json()
        selected_files = request_data.get("selectedFiles", [])
        folder_path = request_data.get("folderPath", "")
        
        if not selected_files:
            return {"success": False, "error": "No files selected"}
        
        # Build file paths
        file_paths = []
        for filename in selected_files:
            if folder_path:
                full_path = os.path.join(folder_path, filename)
            else:
                full_path = filename
            
            if os.path.exists(full_path):
                file_paths.append(full_path)
            else:
                print(f"⚠️ File not found: {full_path}")
        
        if not file_paths:
            return {"success": False, "error": "No valid files found"}
        
        # Create mailto URL with file attachments
        system = platform.system().lower()
        
        if system == "windows":
            # On Windows, we'll use the default email client via subprocess
            # Create a PowerShell script to open Outlook or default mail client
            powershell_script = '''
Add-Type -AssemblyName Microsoft.Office.Interop.Outlook
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItem(0)
$mail.Subject = "Selected Resume Files"
$mail.Body = "Please find the attached resume files for your review."
'''
            
            # Add each file as attachment in PowerShell
            for file_path in file_paths:
                # Escape the path for PowerShell
                escaped_path = file_path.replace("'", "''")
                powershell_script += f"\n$mail.Attachments.Add('{escaped_path}')"
            
            powershell_script += "\n$mail.Display()"
            
            # Write PowerShell script to temp file and execute
            temp_script_path = os.path.join(os.getenv('TEMP', '.'), 'email_attachments.ps1')
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(powershell_script)
            
            try:
                subprocess.run([
                    'powershell.exe', 
                    '-ExecutionPolicy', 'Bypass',
                    '-File', temp_script_path
                ], check=True)
                
                # Clean up temp file
                os.remove(temp_script_path)
                
                print(f"✅ Email opened with {len(file_paths)} attachments")
                return {"success": True, "message": f"Email opened with {len(file_paths)} attachments"}
                
            except subprocess.CalledProcessError as e:
                # Fallback: try to open with default mail handler using file association
                mailto_url = "mailto:?subject=Selected Resume Files&body=Please find the attached resume files for your review."
                subprocess.run(['start', mailto_url], shell=True)
                
                return {"success": True, "message": "Email client opened (manual attachment required)", "files": file_paths}
                
        else:
            # For macOS and Linux, use the default mailto handler
            mailto_url = "mailto:?subject=Selected Resume Files&body=Please find the attached resume files for your review."
            
            if system == "darwin":  # macOS
                subprocess.run(['open', mailto_url])
            else:  # Linux
                subprocess.run(['xdg-open', mailto_url])
            
            return {"success": True, "message": "Email client opened (manual attachment required)", "files": file_paths}
            
    except Exception as e:
        print(f"❌ Error opening email: {e}")
        return {"success": False, "error": str(e)}
