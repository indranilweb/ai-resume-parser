import os
import config as app_config
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss  # type: ignore

# Directories
CACHE_DIR = "cache_dir"
VECTOR_DB_DIR = "vector_db"

GEMINI_KEY = app_config.GEMINI_KEY
GEMINI_MODEL = app_config.GEMINI_MODEL
PERF_CONFIG = getattr(app_config, 'PERFORMANCE_CONFIG', {})

# Feature flags & performance tuning
ENABLE_VECTOR_SEARCH = True
SIMILARITY_THRESHOLD = PERF_CONFIG.get('SIMILARITY_THRESHOLD', 0.3)
MAX_VECTOR_RESULTS = None
BATCH_SIZE = 20
MAX_RESUMES_PER_BATCH = PERF_CONFIG.get('MAX_RESUMES_PER_BATCH', 15)
ENABLE_PARALLEL_READING = PERF_CONFIG.get('ENABLE_PARALLEL_READING', True)
MAX_WORKERS = PERF_CONFIG.get('MAX_WORKERS', 4)
BATCH_DELAY_SECONDS = PERF_CONFIG.get('BATCH_DELAY_SECONDS', 1)
ENABLE_MEMORY_OPTIMIZATION = PERF_CONFIG.get('ENABLE_MEMORY_OPTIMIZATION', True)

for dir_path in [CACHE_DIR, VECTOR_DB_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Lazy loaded globals
_embedding_model = None


def get_embedding_model():
    # Initialize the sentence transformer model for embeddings
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    if not ENABLE_VECTOR_SEARCH:
        return None
    try:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("🔧 Sentence transformer model loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load sentence transformer model: {e}")
        print("Vector search will be disabled")
        _embedding_model = None
    return _embedding_model

# Initialize the Gemini client
# It automatically picks up the API key from the GEMINI_API_KEY environment variable.
try:
    # IMPORTANT: It is recommended to use environment variables for API keys.
    api_key = GEMINI_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"🚨 Error initializing Gemini client: {e}")

__all__ = [
    'CACHE_DIR','VECTOR_DB_DIR','GEMINI_KEY','GEMINI_MODEL','PERF_CONFIG',
    'ENABLE_VECTOR_SEARCH','SIMILARITY_THRESHOLD','MAX_VECTOR_RESULTS','BATCH_SIZE',
    'MAX_RESUMES_PER_BATCH','ENABLE_PARALLEL_READING','MAX_WORKERS','BATCH_DELAY_SECONDS',
    'ENABLE_MEMORY_OPTIMIZATION','get_embedding_model'
]
