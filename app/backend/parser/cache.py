import os, json, hashlib
from typing import List
from .config import CACHE_DIR
from .config import get_embedding_model


def generate_cache_key(resumes_data: dict, required_skills: List[str]) -> str:
    """Generate a unique cache key based on resume content and skills."""
    # Create a combined string from resume filenames, content hashes, and skills
    parts = []
    for filename, content in sorted(resumes_data.items()):
        h = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        parts.append(f"{filename}:{h}")
    skills_str = ','.join(sorted(s.strip().lower() for s in required_skills))
    combined = '|'.join(parts) + f"|skills:{skills_str}"
    # Add vector search indicator to cache key
    vector_indicator = 'vector_enabled' if get_embedding_model() else 'vector_disabled'
    combined += f"|{vector_indicator}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


def get_cached_result(cache_key: str):
    """Retrieve cached result if it exists."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            print(f"📂 Cache file found: {cache_key[:12]}...json")
            return result
        except Exception as e:
            print(f"⚠️ Warning: Could not read cache file: {e}")
    return None


def save_to_cache(cache_key: str, result):
    """Save result to cache."""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Cache file created: {cache_key[:12]}...json")
    except Exception as e:
        print(f"⚠️ Warning: Could not save to cache: {e}")


def clear_cache(cache_key: str=None):
    """Clear cache files. If cache_key is provided, clear specific cache, otherwise clear all."""
    try:
        if cache_key:
            cf = os.path.join(CACHE_DIR, f"{cache_key}.json")
            if os.path.exists(cf):
                os.remove(cf)
                print(f"🗑️ Cleared specific cache: {cache_key[:12]}...json")
        else:
            for file in os.listdir(CACHE_DIR):
                if file.endswith('.json'):
                    os.remove(os.path.join(CACHE_DIR, file))
            print("🗑️ Cleared all cache files")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear cache: {e}")

__all__ = ['generate_cache_key','get_cached_result','save_to_cache','clear_cache']
