"""Provider dispatch layer.

This module exposes a unified parse_resumes_batch() that delegates to the
provider-specific implementation based on configuration. Existing imports
continue to work while allowing easy provider switching via config.
"""

from .config import AI_PROVIDER

_ERR_HELP = "Set AI_PROVIDER to 'gemini' or 'azure' in app/backend/config.py"

if AI_PROVIDER == 'gemini':
    from .providers.batch_gemini import parse_resumes_batch  # type: ignore
elif AI_PROVIDER == 'azure':
    from .providers.batch_azure import parse_resumes_batch  # type: ignore
else:
    def parse_resumes_batch(*_, **__):  # type: ignore
        print(f"❌ Unknown AI_PROVIDER '{AI_PROVIDER}'. {_ERR_HELP}")
        return [], {
            "genai_cache_hit": False,
            "vector_cache_hit": False,
            "cache_key": None,
            "processing_time": None,
            "batches_processed": 0,
            "total_batches": 0
        }

__all__ = ['parse_resumes_batch']
