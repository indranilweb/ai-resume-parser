import os
import config as app_config
from sentence_transformers import SentenceTransformer
import faiss  # type: ignore

# Directories
CACHE_DIR = "cache_dir"
VECTOR_DB_DIR = "vector_db"

AI_PROVIDER = getattr(app_config, 'AI_PROVIDER', 'gemini').lower()

# Gemini specific (only loaded if provider is gemini)
GEMINI_KEY = getattr(app_config, 'GEMINI_KEY', None)
GEMINI_MODEL = getattr(app_config, 'GEMINI_MODEL', None)

# Azure OpenAI specific
AZURE_OPENAI_API_KEY = getattr(app_config, 'AZURE_OPENAI_API_KEY', os.getenv('AZURE_OPENAI_API_KEY'))
AZURE_OPENAI_ENDPOINT = getattr(app_config, 'AZURE_OPENAI_ENDPOINT', os.getenv('AZURE_OPENAI_ENDPOINT'))
AZURE_OPENAI_DEPLOYMENT = getattr(app_config, 'AZURE_OPENAI_DEPLOYMENT', os.getenv('AZURE_OPENAI_DEPLOYMENT'))
AZURE_OPENAI_API_VERSION = getattr(app_config, 'AZURE_OPENAI_API_VERSION', os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'))
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
        # Try to load from local model directory first (for offline deployment)
        local_model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'all-MiniLM-L6-v2')
        if os.path.exists(local_model_path):
            _embedding_model = SentenceTransformer(local_model_path)
            print(f"🔧 Sentence transformer model loaded from local path: {local_model_path}")
        else:
            # Fallback to downloading from Hugging Face (requires internet)
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("🔧 Sentence transformer model loaded from Hugging Face")
    except Exception as e:
        print(f"⚠️ Warning: Could not load sentence transformer model: {e}")
        print("Vector search will be disabled")
        _embedding_model = None
    return _embedding_model

if AI_PROVIDER == 'gemini':
    try:
        import google.generativeai as genai  # local import to isolate provider dependency
        if not GEMINI_KEY:
            raise ValueError("GEMINI_KEY not configured.")
        genai.configure(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"🚨 Error initializing Gemini client: {e}")
elif AI_PROVIDER == 'azure':
    # Lazy validation only; client created inside provider module when needed
    missing = [n for n,v in {
        'AZURE_OPENAI_API_KEY': AZURE_OPENAI_API_KEY,
        'AZURE_OPENAI_ENDPOINT': AZURE_OPENAI_ENDPOINT,
        'AZURE_OPENAI_DEPLOYMENT': AZURE_OPENAI_DEPLOYMENT
    }.items() if not v]
    if missing:
        print(f"⚠️ Azure OpenAI config missing: {', '.join(missing)}")
else:
    print(f"⚠️ Unknown AI_PROVIDER '{AI_PROVIDER}'. Defaulting to gemini dispatch error mode.")

__all__ = [
    'CACHE_DIR','VECTOR_DB_DIR','AI_PROVIDER','GEMINI_KEY','GEMINI_MODEL',
    'AZURE_OPENAI_API_KEY','AZURE_OPENAI_ENDPOINT','AZURE_OPENAI_DEPLOYMENT','AZURE_OPENAI_API_VERSION','PERF_CONFIG',
    'ENABLE_VECTOR_SEARCH','SIMILARITY_THRESHOLD','MAX_VECTOR_RESULTS','BATCH_SIZE',
    'MAX_RESUMES_PER_BATCH','ENABLE_PARALLEL_READING','MAX_WORKERS','BATCH_DELAY_SECONDS',
    'ENABLE_MEMORY_OPTIMIZATION','get_embedding_model'
]
