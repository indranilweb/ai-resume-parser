import os
import json
import hashlib
import numpy as np
import pickle
import google.generativeai as genai
import pypdf  # For reading PDF files
import docx   # For reading DOCX files
import config
from sentence_transformers import SentenceTransformer
import faiss
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional

# --- Configuration and Setup ---
GEMINI_KEY = config.GEMINI_KEY
GEMINI_MODEL = config.GEMINI_MODEL
CACHE_DIR = "cache_dir"
VECTOR_DB_DIR = "vector_db"

# Import performance configuration from config
PERF_CONFIG = getattr(config, 'PERFORMANCE_CONFIG', {})

# Vector search configuration
ENABLE_VECTOR_SEARCH = True  # Set to False to disable vector search
SIMILARITY_THRESHOLD = PERF_CONFIG.get('SIMILARITY_THRESHOLD', 0.3)
MAX_VECTOR_RESULTS = None    # Maximum resumes to pass to Gemini (None = no limit)

# Batch processing configuration for handling large datasets
BATCH_SIZE = 20              # Number of resumes to process per batch
MAX_RESUMES_PER_BATCH = PERF_CONFIG.get('MAX_RESUMES_PER_BATCH', 15)
ENABLE_PARALLEL_READING = PERF_CONFIG.get('ENABLE_PARALLEL_READING', True)
MAX_WORKERS = PERF_CONFIG.get('MAX_WORKERS', 4)
BATCH_DELAY_SECONDS = PERF_CONFIG.get('BATCH_DELAY_SECONDS', 1)
ENABLE_MEMORY_OPTIMIZATION = PERF_CONFIG.get('ENABLE_MEMORY_OPTIMIZATION', True)

# Ensure directories exist
for dir_path in [CACHE_DIR, VECTOR_DB_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Initialize the sentence transformer model for embeddings
embedding_model = None
if ENABLE_VECTOR_SEARCH:
    try:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("🔧 Sentence transformer model loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load sentence transformer model: {e}")
        print("Vector search will be disabled")
else:
    print("🔧 Vector search disabled by configuration")

# Initialize the Gemini client
# It automatically picks up the API key from the GEMINI_API_KEY environment variable.
try:
    # IMPORTANT: It is recommended to use environment variables for API keys.
    # For this example, the key is placed directly.
    api_key = GEMINI_KEY # os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable or paste it here.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"🚨 Error initializing Gemini client: {e}")
    exit()

# --- Progress Tracking Functions ---

class ProgressTracker:
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, increment: int = 1):
        with self.lock:
            self.current_item += increment
            progress = (self.current_item / self.total_items) * 100
            elapsed = time.time() - self.start_time
            
            if self.current_item > 0:
                eta = (elapsed / self.current_item) * (self.total_items - self.current_item)
                print(f"🔄 {self.operation_name}: {self.current_item}/{self.total_items} ({progress:.1f}%) - ETA: {eta:.1f}s")
            else:
                print(f"🔄 {self.operation_name}: {self.current_item}/{self.total_items} ({progress:.1f}%)")
    
    def complete(self):
        elapsed = time.time() - self.start_time
        print(f"✅ {self.operation_name} completed in {elapsed:.2f}s")

# --- Enhanced File Reading Functions ---

def read_resume_file_safe(file_info: tuple) -> tuple:
    """Safely read a single resume file with error handling."""
    file_path, filename = file_info
    try:
        content = get_resume_content(file_path)
        if content and content.strip():
            return filename, content
        else:
            print(f"  ⚠️ Empty content from '{filename}'. Skipping.")
            return filename, None
    except Exception as e:
        print(f"  ❌ Error reading '{filename}': {e}")
        return filename, None

def read_resumes_parallel(resume_files: List[str], resume_dir: str, progress_tracker: Optional[ProgressTracker] = None) -> Dict[str, str]:
    """Read multiple resume files in parallel for better performance."""
    resumes_data = {}
    
    if not ENABLE_PARALLEL_READING or len(resume_files) < 4:
        # Sequential reading for small datasets
        for filename in resume_files:
            file_path = os.path.join(resume_dir, filename)
            content = get_resume_content(file_path)
            if content and content.strip():
                resumes_data[filename] = content
                print(f"  ✅ Successfully read '{filename}'")
                if progress_tracker:
                    progress_tracker.update()
            else:
                print(f"  ❌ Could not read content from '{filename}'. Skipping.")
        return resumes_data
    
    # Parallel reading for larger datasets
    print(f"📚 Reading {len(resume_files)} files in parallel (max {MAX_WORKERS} workers)...")
    
    file_infos = [(os.path.join(resume_dir, filename), filename) for filename in resume_files]
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(read_resume_file_safe, file_info): file_info[1] 
                         for file_info in file_infos}
        
        for future in as_completed(future_to_file):
            filename, content = future.result()
            if content:
                resumes_data[filename] = content
                print(f"  ✅ Successfully read '{filename}'")
            if progress_tracker:
                progress_tracker.update()
    
    return resumes_data

# --- Batch Processing Functions ---

def split_into_batches(items: dict, batch_size: int) -> List[dict]:
    """Split a dictionary into smaller batches."""
    items_list = list(items.items())
    batches = []
    
    for i in range(0, len(items_list), batch_size):
        batch_items = dict(items_list[i:i + batch_size])
        batches.append(batch_items)
    
    return batches

def process_resume_batch(batch_data: dict, required_skills: List[str], batch_num: int, total_batches: int) -> List[dict]:
    """Process a single batch of resumes through Gemini API."""
    print(f"\n🚀 Processing batch {batch_num}/{total_batches} ({len(batch_data)} resumes)...")
    
    try:
        prompt = construct_batch_prompt(batch_data, required_skills)
        
        # Select the model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Configure the generation to output JSON
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
        
        # Call the API
        response = model.generate_content(prompt, generation_config=generation_config)
        response_content = response.text
        
        # Parse JSON response
        batch_results = json.loads(response_content)
        
        print(f"✅ Batch {batch_num}/{total_batches} completed: {len(batch_results)} candidates found")
        return batch_results
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in batch {batch_num}: {e}")
        print(f"Raw response: {response.text[:500]}...")
        return []
    except Exception as e:
        print(f"❌ Error processing batch {batch_num}: {e}")
        return []

# --- Text Extraction Functions (Unchanged) ---

def read_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"📄❌ Error reading PDF file '{os.path.basename(file_path)}': {e}")
        return ""

def read_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"📄❌ Error reading DOCX file '{os.path.basename(file_path)}': {e}")
        return ""

def read_txt(file_path: str) -> str:
    """Reads a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"📄❌ Error reading TXT file '{os.path.basename(file_path)}': {e}")
        return ""

def get_resume_content(file_path: str) -> str:
    """
    Reads the content of a resume file by dispatching to the correct reader
    based on the file extension.
    """
    filename = os.path.basename(file_path)
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    if extension == '.txt':
        return read_txt(file_path)
    elif extension == '.pdf':
        return read_pdf(file_path)
    elif extension == '.docx':
        return read_docx(file_path)
    elif extension == '.doc':
        print(f"⚠️ Warning: .doc files are not directly supported. Please convert '{filename}' to .docx or .pdf.")
        return ""
    else:
        print(f"⚠️ Warning: Unsupported file type '{extension}' for file '{filename}'. Skipping.")
        return ""

# --- Vector Database Functions ---

def get_vector_db_path(resumes_data: dict) -> str:
    """Generate a unique vector database path based on resume content."""
    content_parts = []
    for filename, content in sorted(resumes_data.items()):
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        content_parts.append(f"{filename}:{content_hash}")
    
    combined = "|".join(content_parts)
    db_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
    return os.path.join(VECTOR_DB_DIR, f"resume_db_{db_hash}")

def create_vector_database(resumes_data: dict, force_rebuild: bool = False) -> tuple:
    """Create FAISS vector database from resume content."""
    if not embedding_model:
        return None, None, False
    
    db_path = get_vector_db_path(resumes_data)
    
    # Check if vector DB already exists (unless force rebuild is requested)
    if not force_rebuild and os.path.exists(f"{db_path}.index") and os.path.exists(f"{db_path}_metadata.pkl"):
        try:
            # Load existing vector database
            index = faiss.read_index(f"{db_path}.index")
            with open(f"{db_path}_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            print(f"📂 Loaded existing vector database: {os.path.basename(db_path)}")
            return index, metadata, True  # True indicates cache hit
        except Exception as e:
            print(f"⚠️ Could not load existing vector DB: {e}")
    
    if force_rebuild:
        print("🔥 Force rebuild requested - creating new vector database...")
    else:
        print("🔧 Creating vector database from resumes...")
    
    # Create new vector database
    texts = []
    metadata = []
    
    for filename, content in resumes_data.items():
        # Split content into chunks for better semantic search
        chunks = split_text_into_chunks(content, chunk_size=512, overlap=50)
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadata.append({
                'filename': filename,
                'chunk_id': i,
                'content': chunk
            })
    
    if not texts:
        print("❌ No text content to vectorize")
        return None, None, False
    
    # Generate embeddings
    print(f"🔧 Generating embeddings for {len(texts)} text chunks...")
    embeddings = embedding_model.encode(texts, show_progress_bar=False)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype(np.float32))
    
    # Save vector database
    try:
        faiss.write_index(index, f"{db_path}.index")
        with open(f"{db_path}_metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)
        print(f"💾 Vector database saved: {os.path.basename(db_path)}")
    except Exception as e:
        print(f"⚠️ Could not save vector DB: {e}")
    
    return index, metadata, False  # False indicates new database created

def split_text_into_chunks(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """Split text into overlapping chunks for better semantic search."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks if chunks else [text]

def semantic_search_resumes(required_skills: list, resumes_data: dict, top_k: int = None, similarity_threshold: float = None, force_analyze: bool = False) -> tuple[dict, bool]:
    """Perform semantic search to filter resumes based on required skills."""
    vector_cache_hit = False
    
    if not embedding_model:
        print("⚠️ Vector search disabled - returning all resumes")
        return resumes_data, vector_cache_hit
    
    if not required_skills or not resumes_data:
        return resumes_data, vector_cache_hit
    
    # Use global configuration if not specified
    if top_k is None:
        top_k = MAX_VECTOR_RESULTS
    if similarity_threshold is None:
        similarity_threshold = SIMILARITY_THRESHOLD
    
    # Create or load vector database
    index, metadata, vector_cache_hit = create_vector_database(resumes_data, force_analyze)
    if not index or not metadata:
        print("❌ Could not create vector database - returning all resumes")
        return resumes_data, False
    
    # Create query from required skills
    skills_query = f"Required skills and experience: {', '.join(required_skills)}"
    
    print(f"🔍 Performing semantic search for: {skills_query}")
    
    # Generate query embedding
    query_embedding = embedding_model.encode([skills_query])
    faiss.normalize_L2(query_embedding)
    
    # Search for similar chunks
    search_k = min(len(metadata), top_k if top_k else len(metadata))
    scores, indices = index.search(query_embedding.astype(np.float32), search_k)
    
    # Aggregate scores per resume file
    resume_scores = {}
    for score, idx in zip(scores[0], indices[0]):
        if score >= similarity_threshold:
            filename = metadata[idx]['filename']
            if filename not in resume_scores:
                resume_scores[filename] = []
            resume_scores[filename].append(score)
    
    # Calculate average score per resume
    filtered_resumes = {}
    for filename, scores_list in resume_scores.items():
        avg_score = sum(scores_list) / len(scores_list)
        if avg_score >= similarity_threshold:
            filtered_resumes[filename] = resumes_data[filename]
            print(f"  ✅ {filename} (similarity: {avg_score:.3f})")
    
    if filtered_resumes:
        print(f"🎯 Vector search filtered {len(resumes_data)} → {len(filtered_resumes)} resumes")
        return filtered_resumes, vector_cache_hit
    else:
        print(f"⚠️ No resumes met similarity threshold ({similarity_threshold}) - returning all resumes")
        return resumes_data, vector_cache_hit

# --- Cache Management Functions ---

def generate_cache_key(resumes_data: dict, required_skills: list[str]) -> str:
    """Generate a unique cache key based on resume content and skills."""
    # Create a combined string from resume filenames, content hashes, and skills
    content_parts = []
    for filename, content in sorted(resumes_data.items()):
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        content_parts.append(f"{filename}:{content_hash}")
    
    skills_str = ",".join(sorted([skill.strip().lower() for skill in required_skills]))
    combined = "|".join(content_parts) + f"|skills:{skills_str}"
    
    # Add vector search indicator to cache key
    vector_indicator = "vector_enabled" if embedding_model else "vector_disabled"
    combined += f"|{vector_indicator}"
    
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def get_cached_result(cache_key: str) -> list[dict]:
    """Retrieve cached result if it exists."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            print(f"📂 Cache file found: {cache_key[:12]}...json")
            return result
        except Exception as e:
            print(f"⚠️  Warning: Could not read cache file: {e}")
    return None

def clear_cache(cache_key: str = None) -> None:
    """Clear cache files. If cache_key is provided, clear specific cache, otherwise clear all."""
    try:
        if cache_key:
            cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"🗑️ Cleared specific cache: {cache_key[:12]}...json")
        else:
            for file in os.listdir(CACHE_DIR):
                if file.endswith('.json'):
                    os.remove(os.path.join(CACHE_DIR, file))
            print("🗑️ Cleared all cache files")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear cache: {e}")

def save_to_cache(cache_key: str, result: list[dict]) -> None:
    """Save result to cache."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Cache file created: {cache_key[:12]}...json")
    except Exception as e:
        print(f"⚠️  Warning: Could not save to cache: {e}")

# --- Gemini API Interaction (Modified for Batch Processing) ---

def construct_batch_prompt(resumes_data: dict, required_skills: list[str]) -> str:
    """
    Constructs a detailed prompt for the Gemini API to process multiple resumes,
    filter them by skills, and extract data for the matched ones.
    """
    skills_string = ", ".join(required_skills)

    # Combine all resume texts into one block, with clear separators
    combined_resume_text = ""
    for filename, text in resumes_data.items():
        combined_resume_text += f"--- START OF RESUME: {filename} ---\n"
        combined_resume_text += text + "\n"
        combined_resume_text += f"--- END OF RESUME: {filename} ---\n\n"

    # The prompt is carefully structured to guide the model.
    # It first asks the model to filter and then extract.
    prompt = f"""
    You are an expert HR recruitment assistant. Your task is to analyze a batch of resumes, identify candidates who match a specific set of skills, and then extract key information for ONLY the matched candidates in a strict JSON format.

    The required technical skills we are looking for are: {skills_string}.

    Below is a collection of resumes. Each resume is clearly marked with its source filename.
    --- BATCH OF RESUMES START ---
    {combined_resume_text}
    --- BATCH OF RESUMES END ---

    **Your Instructions:**

    1.  **Analyze and Filter:** Carefully read every resume provided in the batch above. Identify which resumes are a strong match for the required skills: "{skills_string}". A strong match means the resume explicitly mentions several of these skills.

    2.  **Extract Information for Matched Resumes ONLY:** For each resume that you identified as a strong match, extract the following information and format it as a JSON object. Adhere strictly to the data types and formats specified:
        * "source_file": (String) The original filename of the resume (provided in the start/end markers).
        * "name": (String) The full name of the candidate.
        * "contact_number": (String) The primary phone number.
        * "last_3_companies": (Array of Strings) A list of the last 3 companies the candidate worked for, starting with the most recent. Crucially, include only official company names. Exclude project names, client names, or internal divisions within a company. If fewer than 3 companies are clearly stated, include only all available.
        * "top_5_technical_skills": (Array of Strings) A list of up to 5 technical skills explicitly mentioned in the resume that are most directly relevant to the {skills_string} and/or are highly prominent in the candidate's experience.
        * "years_of_experience": (Number) The total calculated professional work experience in years. Calculate this based on the start and end dates of all full-time work experiences listed. Round it to the nearest whole number
        * "match_score": (Number) An intelligent match score from 0-100 based on how well the candidate matches the required skills "{skills_string}". Consider: skill relevance (40%), years of experience (20%), company quality/reputation (15%), project complexity (15%), and educational background (10%). Provide only the numeric score.
        * "score_breakdown": (String) A brief explanation (max 50 words) of why this score was assigned, highlighting the key strengths that contributed to the score.
        * "summary": (String) A concise summary of the candidate's professional background and expertise, and most significant achievements. This must be no more than 200 words.

    **Output Format:**
    Your output MUST be a single, valid JSON array `[]` containing one JSON object for each matched candidate. If no candidates match the required skills, you MUST return an empty array `[]`.
    Do not include any explanations, introductory text, markdown formatting like ```json, or any text outside of the final JSON array.
    If a piece of information cannot be found, use `null` as the value for that key.
    """
    print("📝 Constructed a batch prompt for the Gemini API.")
    return prompt

def parse_resumes_batch(resumes_data: dict, required_skills: list[str], force_analyze: bool = False) -> tuple[list[dict], dict]:
    """Sends the combined resume text to the Gemini API for batch parsing and filtering."""
    cache_info = {
        "gemini_cache_hit": False,
        "vector_cache_hit": False,
        "cache_key": None,
        "processing_time": None,
        "batches_processed": 0,
        "total_batches": 0
    }
    
    if not resumes_data:
        print("❌ No resume content to process.")
        return [], cache_info

    # Check cache first (unless force analyze is requested)
    cache_key = generate_cache_key(resumes_data, required_skills)
    cache_info["cache_key"] = cache_key
    print(f"🔑 Generated cache key: {cache_key[:12]}...")
    
    cached_result = None
    if not force_analyze:
        cached_result = get_cached_result(cache_key)
    else:
        print("🔥 Force analyze requested - skipping cache check")
    
    if cached_result is not None and not force_analyze:
        cache_info["gemini_cache_hit"] = True
        print("🎯 CACHE HIT: Found cached result! Skipping Gemini API call.")
        print(f"✅ Returning {len(cached_result)} cached candidate(s)")
        return cached_result, cache_info

    if force_analyze:
        clear_cache(cache_key)
    
    print("❌ CACHE MISS: No cached result found.")
    
    start_time = time.time()
    
    # Determine if we need batch processing
    total_resumes = len(resumes_data)
    
    if total_resumes <= MAX_RESUMES_PER_BATCH:
        # Process all resumes in a single batch (original behavior)
        print(f"📝 Processing {total_resumes} resumes in single batch...")
        cache_info["total_batches"] = 1
        cache_info["batches_processed"] = 1
        
        prompt = construct_batch_prompt(resumes_data, required_skills)
        print("🚀 GEMINI API: Connecting to process the batch... (This may take a moment)")

        try:
            # Select the model, Gemini 1.5 Flash is good for this task.
            model = genai.GenerativeModel(GEMINI_MODEL)

            # Configure the generation to output JSON
            generation_config = genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )

            # Call the API with the single, combined prompt
            response = model.generate_content(prompt, generation_config=generation_config)
            
            # The response text should be a valid JSON string (a list of objects)
            response_content = response.text
            parsed_data = json.loads(response_content)
            
            processing_time = round(time.time() - start_time, 2)
            cache_info["processing_time"] = processing_time
            
            # Save to cache
            save_to_cache(cache_key, parsed_data)
            print("💾 CACHE SAVE: Result saved to cache for future use.")
            print(f"✅ Gemini API returned {len(parsed_data)} candidate(s) in {processing_time}s")
            
            return parsed_data, cache_info
        except json.JSONDecodeError:
            print("\n🚨 Error: Failed to decode JSON from the API response.")
            print(f"Raw Gemini Response:\n---\n{response.text}\n---")
            return [], cache_info
        except Exception as e:
            print(f"\n🚨 An error occurred while communicating with the Gemini API: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Raw Gemini Response:\n---\n{response.text}\n---")
            return [], cache_info
    
    else:
        # Process resumes in batches for large datasets
        print(f"📊 Large dataset detected ({total_resumes} resumes). Using batch processing...")
        
        # Split resumes into batches
        batches = split_into_batches(resumes_data, MAX_RESUMES_PER_BATCH)
        cache_info["total_batches"] = len(batches)
        
        print(f"🔄 Processing {total_resumes} resumes in {len(batches)} batches of max {MAX_RESUMES_PER_BATCH} resumes each...")
        
        all_results = []
        successful_batches = 0
        
        for batch_num, batch_data in enumerate(batches, 1):
            try:
                batch_results = process_resume_batch(batch_data, required_skills, batch_num, len(batches))
                all_results.extend(batch_results)
                successful_batches += 1
                
                # Add a small delay between batches to avoid rate limiting
                if batch_num < len(batches):
                    time.sleep(BATCH_DELAY_SECONDS)
                    
            except Exception as e:
                print(f"❌ Failed to process batch {batch_num}: {e}")
                continue
        
        cache_info["batches_processed"] = successful_batches
        processing_time = round(time.time() - start_time, 2)
        cache_info["processing_time"] = processing_time
        
        if all_results:
            # Save combined results to cache
            save_to_cache(cache_key, all_results)
            print("💾 CACHE SAVE: Combined batch results saved to cache for future use.")
            print(f"✅ Batch processing completed: {len(all_results)} total candidates found in {processing_time}s")
            print(f"📊 Successfully processed {successful_batches}/{len(batches)} batches")
        else:
            print(f"❌ No results from any batch. Processed {successful_batches}/{len(batches)} batches successfully.")
        
        return all_results, cache_info

# --- Main Application Logic (Modified for Batch Processing) ---
class ResumeParser:
    def main(self, dir_path: str, query_string: str, force_analyze: bool = False) -> tuple[list[dict], dict]:
        """Main function to run the resume parser application."""
        cache_info = {
            "gemini_cache_hit": False,
            "vector_cache_hit": False,
            "cache_key": None,
            "processing_time": None,
            "total_resumes": 0,
            "filtered_resumes": 0,
            "batches_processed": 0,
            "total_batches": 0
        }
        
        print("🤖 --- AI-Powered Resume Parser (Vector + Batch Mode) ---")
        if force_analyze:
            print("🔥 FORCE ANALYZE MODE - Bypassing all caches")
        
        resume_dir = dir_path.strip()
        if not os.path.isdir(resume_dir):
            print(f"❌ Error: Directory '{resume_dir}' not found.")
            return [], cache_info
            
        skills_input = query_string.strip()
        if not skills_input:
            print("❌ Error: You must specify at least one skill.")
            return [], cache_info
        required_skills = [skill.strip() for skill in skills_input.split(',')]

        supported_extensions = ('.txt', '.pdf', '.docx', '.doc')
        resume_files = [f for f in os.listdir(resume_dir) if f.lower().endswith(supported_extensions)]

        if not resume_files:
            print(f"❌ No supported resumes (.txt, .pdf, .docx) found in '{resume_dir}'.")
            return [], cache_info

        total_files = len(resume_files)
        print(f"\n📂 Found {total_files} resume(s). Reading content...")
        
        # Initialize progress tracker for file reading
        file_progress = ProgressTracker(total_files, "Reading files")
        
        # Use enhanced parallel file reading
        start_reading = time.time()
        all_resumes_data = read_resumes_parallel(resume_files, resume_dir, file_progress)
        file_progress.complete()
        
        reading_time = time.time() - start_reading
        print(f"📚 File reading completed in {reading_time:.2f}s")

        if not all_resumes_data:
            print("\n❌ Could not read any resume content. Exiting.")
            return [], cache_info

        cache_info["total_resumes"] = len(all_resumes_data)
        
        # Memory usage reporting and optimization for large datasets
        if len(all_resumes_data) > 100:
            total_chars = sum(len(content) for content in all_resumes_data.values())
            avg_size = total_chars / len(all_resumes_data)
            print(f"📊 Dataset stats: {len(all_resumes_data)} resumes, avg size: {avg_size:.0f} chars, total: {total_chars:,} chars")
            
            # Memory optimization for very large datasets
            if ENABLE_MEMORY_OPTIMIZATION and len(all_resumes_data) > 500:
                print("🔧 Large dataset detected - enabling memory optimization")
                # For extremely large datasets, we could implement streaming processing
                # This is a placeholder for future memory optimization techniques

        # Perform semantic search to filter resumes before Gemini API call
        print(f"\n🔍 --- Semantic Filtering Phase ---")
        filtered_resumes, vector_cache_hit = semantic_search_resumes(required_skills, all_resumes_data, force_analyze=force_analyze)
        cache_info["vector_cache_hit"] = vector_cache_hit
        cache_info["filtered_resumes"] = len(filtered_resumes)
        
        if not filtered_resumes:
            print("\n❌ --- No candidates found through semantic search. ---")
            return [], cache_info
        
        if len(filtered_resumes) < len(all_resumes_data):
            reduction_pct = ((len(all_resumes_data) - len(filtered_resumes)) / len(all_resumes_data)) * 100
            print(f"📊 Semantic search reduced API load: {len(all_resumes_data)} → {len(filtered_resumes)} resumes ({reduction_pct:.1f}% reduction)")

        # The batch API processing happens here with filtered resumes
        print(f"\n🚀 --- Gemini API Processing Phase ---")
        matched_candidates, gemini_cache_info = parse_resumes_batch(filtered_resumes, required_skills, force_analyze)
        
        # Merge cache info (preserve vector_cache_hit and add batch info)
        vector_cache_hit_backup = cache_info["vector_cache_hit"]
        cache_info.update(gemini_cache_info)
        cache_info["vector_cache_hit"] = vector_cache_hit_backup

        if matched_candidates:
            print(f"\n\n🎉 --- Found {len(matched_candidates)} Matched Candidate(s) ---")
            # Pretty-print the final JSON output
            # print(json.dumps(matched_candidates, indent=4))
            print("Matched candidate files:")
            for candidate in matched_candidates:
                print(f"  - {candidate.get('source_file', 'Unknown')}")
            
            # Performance summary for large datasets
            if len(all_resumes_data) > 50:
                total_time = time.time() - start_reading
                throughput = len(all_resumes_data) / total_time
                print(f"\n📈 Performance Summary:")
                print(f"   • Total processing time: {total_time:.2f}s")
                print(f"   • Throughput: {throughput:.1f} resumes/second")
                if cache_info.get("batches_processed", 0) > 0:
                    print(f"   • Batches processed: {cache_info['batches_processed']}/{cache_info.get('total_batches', 0)}")
            
            return matched_candidates, cache_info
        else:
            print("\n❌ --- No candidates matched the required skills from the filtered resumes. ---")
            return [], cache_info

# Example of how to run the class
if __name__ == '__main__':
    # Create a 'resumes' directory in the same folder as this script
    # and add your .pdf, .docx, or .txt resume files there.
    
    # Create an instance of the parser
    parser = ResumeParser()
    
    # Specify the directory containing resumes
    resume_directory = "resumes" 
    
    # Specify the skills you're looking for
    required_skills_query = "Python, data analysis, machine learning, SQL"
    
    # Run the main process
    # This will print the results to the console
    result, cache_info = parser.main(resume_directory, required_skills_query)
    print(f"\nCache Info: {cache_info}")
