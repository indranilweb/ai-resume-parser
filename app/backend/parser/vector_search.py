import os, hashlib, pickle
from typing import Dict, List, Tuple
import numpy as np
import faiss  # type: ignore
from .config import (VECTOR_DB_DIR, SIMILARITY_THRESHOLD, MAX_VECTOR_RESULTS,
                     ENABLE_VECTOR_SEARCH, get_embedding_model)

# Utilities

def split_text_into_chunks(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """Split text into overlapping chunks for better semantic search."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks if chunks else [text]


def get_vector_db_path(resumes_data: dict) -> str:
    """Generate a unique vector database path based on resume content."""
    parts = []
    for filename, content in sorted(resumes_data.items()):
        h = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        parts.append(f"{filename}:{h}")

    combined = '|'.join(parts)
    db_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
    return os.path.join(VECTOR_DB_DIR, f"resume_db_{db_hash}")


def create_vector_database(resumes_data: dict, force_rebuild: bool=False):
    """Create FAISS vector database from resume content."""
    embed_model = get_embedding_model()
    if not embed_model:
        return None, None, False
    
    db_path = get_vector_db_path(resumes_data)

    # Check if vector DB already exists (unless force rebuild is requested)
    if (not force_rebuild and
        os.path.exists(f"{db_path}.index") and os.path.exists(f"{db_path}_metadata.pkl")):
        try:
            # Load existing vector database
            index = faiss.read_index(f"{db_path}.index")
            with open(f"{db_path}_metadata.pkl", 'rb') as f: 
                metadata = pickle.load(f)
            print(f"📂 Loaded existing vector database: {os.path.basename(db_path)}")
            return index, metadata, True
        except Exception as e:
            print(f"⚠️ Could not load existing vector DB: {e}")

    print("🔥 Force rebuild requested - creating new vector database..." if force_rebuild else "🔧 Creating vector database from resumes...")
    
    # Create new vector database
    texts, metadata = [], []

    for filename, content in resumes_data.items():
        # Split content into chunks for better semantic search
        for i, chunk in enumerate(split_text_into_chunks(content)):
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
    embeddings = embed_model.encode(texts, show_progress_bar=False)

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


def semantic_search_resumes(required_skills: List[str], resumes_data: dict, top_k: int=None, similarity_threshold: float=None, force_analyze: bool=False):
    """Perform semantic search to filter resumes based on required skills."""
    vector_cache_hit = False
    
    embed_model = get_embedding_model()
    if not embed_model:
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

    skills_query = f"Required skills and experience: {', '.join(required_skills)}"
    print(f"🔍 Performing semantic search for: {skills_query}")
    query_embedding = embed_model.encode([skills_query])
    faiss.normalize_L2(query_embedding)

    search_k = min(len(metadata), top_k if top_k else len(metadata))
    scores, indices = index.search(query_embedding.astype(np.float32), search_k)

    resume_scores = {}
    for score, idx in zip(scores[0], indices[0]):
        if score >= similarity_threshold:
            filename = metadata[idx]['filename']
            resume_scores.setdefault(filename, []).append(score)

    filtered_resumes = {}
    for filename, scores_list in resume_scores.items():
        avg_score = sum(scores_list) / len(scores_list)
        if avg_score >= similarity_threshold:
            filtered_resumes[filename] = resumes_data[filename]
            print(f"  ✅ {filename} (similarity: {avg_score:.3f})")

    if filtered_resumes:
        print(f"🎯 Vector search filtered {len(resumes_data)} → {len(filtered_resumes)} resumes")
        return filtered_resumes, vector_cache_hit
    print(f"⚠️ No resumes met similarity threshold ({similarity_threshold}) - returning all resumes")
    return resumes_data, vector_cache_hit


def clear_vector_cache():
    # Placeholder - vector cache cleared externally by deleting files
    pass

__all__ = ['semantic_search_resumes','clear_vector_cache']
