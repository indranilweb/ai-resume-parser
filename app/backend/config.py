import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_bool_env(key: str, default: bool = False) -> bool:
    """Convert string environment variable to boolean."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_int_env(key: str, default: int = 0) -> int:
    """Convert string environment variable to integer."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

def get_float_env(key: str, default: float = 0.0) -> float:
    """Convert string environment variable to float."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# Gemini settings
GEMINI_KEY = os.getenv("GEMINI_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Azure OpenAI settings (only required if AI_PROVIDER == 'azure')
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Performance and Scalability Configuration
PERFORMANCE_CONFIG = {
    "MAX_RESUMES_PER_BATCH": get_int_env("MAX_RESUMES_PER_BATCH", 15),
    "ENABLE_PARALLEL_READING": get_bool_env("ENABLE_PARALLEL_READING", True),
    "MAX_WORKERS": get_int_env("MAX_WORKERS", 4),
    "SIMILARITY_THRESHOLD": get_float_env("SIMILARITY_THRESHOLD", 0.3),
    "BATCH_DELAY_SECONDS": get_int_env("BATCH_DELAY_SECONDS", 1),
    "ENABLE_MEMORY_OPTIMIZATION": get_bool_env("ENABLE_MEMORY_OPTIMIZATION", True),
}

# Vector Search Configuration
ENABLE_VECTOR_SEARCH = get_bool_env("ENABLE_VECTOR_SEARCH", True)
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "models/all-MiniLM-L6-v2")
