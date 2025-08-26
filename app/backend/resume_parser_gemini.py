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

# --- Configuration and Setup ---
GEMINI_KEY = config.GEMINI_KEY
GEMINI_MODEL = config.GEMINI_MODEL
CACHE_DIR = "cache_dir"
VECTOR_DB_DIR = "vector_db"

# Vector search configuration
ENABLE_VECTOR_SEARCH = True  # Set to False to disable vector search
SIMILARITY_THRESHOLD = 0.3   # Minimum similarity score (0-1)
MAX_VECTOR_RESULTS = None    # Maximum resumes to pass to Gemini (None = no limit)

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
        "processing_time": None
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
    
    import time
    start_time = time.time()
    
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
            "filtered_resumes": 0
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

        print(f"\n📂 Found {len(resume_files)} resume(s). Reading content...")
        
        all_resumes_data = {}
        for filename in resume_files:
            file_path = os.path.join(resume_dir, filename)
            resume_text = get_resume_content(file_path)
            if resume_text and resume_text.strip():
                all_resumes_data[filename] = resume_text
                print(f"  ✅ Successfully read '{filename}'")
            else:
                print(f"  ❌ Could not read content from '{filename}'. Skipping.")

        if not all_resumes_data:
            print("\n❌ Could not read any resume content. Exiting.")
            return [], cache_info

        cache_info["total_resumes"] = len(all_resumes_data)

        # Perform semantic search to filter resumes before Gemini API call
        print(f"\n🔍 --- Semantic Filtering Phase ---")
        filtered_resumes, vector_cache_hit = semantic_search_resumes(required_skills, all_resumes_data, force_analyze=force_analyze)
        cache_info["vector_cache_hit"] = vector_cache_hit
        cache_info["filtered_resumes"] = len(filtered_resumes)
        
        if not filtered_resumes:
            print("\n❌ --- No candidates found through semantic search. ---")
            return [], cache_info
        
        if len(filtered_resumes) < len(all_resumes_data):
            print(f"📊 Semantic search reduced API load: {len(all_resumes_data)} → {len(filtered_resumes)} resumes")

        # The single API call happens here with filtered resumes
        print(f"\n🚀 --- Gemini API Processing Phase ---")
        matched_candidates, gemini_cache_info = parse_resumes_batch(filtered_resumes, required_skills, force_analyze)
        
        # Merge cache info (preserve vector_cache_hit)
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
