import os, time
from typing import List, Tuple
from .progress import ProgressTracker
from .file_readers import read_resumes_parallel
from .vector_search import semantic_search_resumes
from .batch import parse_resumes_batch
from .config import ENABLE_MEMORY_OPTIMIZATION, AI_PROVIDER

class ResumeParser:
    def main(self, dir_path: str, query_string: str, force_analyze: bool=False):
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
        required_skills = [s.strip() for s in skills_input.split(',') if s.strip()]

        supported_ext = ('.txt','.pdf','.docx','.doc')
        resume_files = [f for f in os.listdir(resume_dir) if f.lower().endswith(supported_ext)]

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
        
        cache_info['total_resumes'] = len(all_resumes_data)

        # Memory usage reporting and optimization for large datasets
        if len(all_resumes_data) > 100:
            total_chars = sum(len(c) for c in all_resumes_data.values())
            avg_size = total_chars / len(all_resumes_data)
            print(f"📊 Dataset stats: {len(all_resumes_data)} resumes, avg size: {avg_size:.0f} chars, total: {total_chars:,} chars")
            
            # Memory optimization for very large datasets
            if ENABLE_MEMORY_OPTIMIZATION and len(all_resumes_data) > 500:
                print("🔧 Large dataset detected - enabling memory optimization (placeholder)")
                # For extremely large datasets, we could implement streaming processing
                # This is a placeholder for future memory optimization techniques

        # Perform semantic search to filter resumes before AI model API call
        print(f"\n🔍 --- Semantic Filtering Phase ---")
        filtered_resumes, vector_cache_hit = semantic_search_resumes(required_skills, all_resumes_data, force_analyze=force_analyze)
        cache_info['vector_cache_hit'] = vector_cache_hit
        cache_info['filtered_resumes'] = len(filtered_resumes)

        if not filtered_resumes:
            print("\n❌ --- No candidates found through semantic search. ---")
            return [], cache_info
        
        if len(filtered_resumes) < len(all_resumes_data):
            reduction_pct = ((len(all_resumes_data) - len(filtered_resumes)) / len(all_resumes_data)) * 100
            print(f"📊 Semantic search reduced API load: {len(all_resumes_data)} → {len(filtered_resumes)} resumes ({reduction_pct:.1f}% reduction)")

        # The batch AI provider processing happens here with filtered resumes
        print(f"\n🚀 --- {AI_PROVIDER.upper()} API Processing Phase ---")
        matched_candidates, gemini_cache_info = parse_resumes_batch(filtered_resumes, required_skills, force_analyze)

        # Merge cache info (preserve vector_cache_hit and add batch info)
        vector_cache_hit_backup = cache_info['vector_cache_hit']
        cache_info.update(gemini_cache_info)
        cache_info['vector_cache_hit'] = vector_cache_hit_backup

        if matched_candidates:
            print(f"\n\n🎉 --- Found {len(matched_candidates)} Matched Candidate(s) ---")
            # Pretty-print the final JSON output
            # print(json.dumps(matched_candidates, indent=4))
            print("Matched candidate files:")
            for c in matched_candidates:
                print(f"  - {c.get('source_file','Unknown')}")

            # Performance summary for large datasets
            if len(all_resumes_data) > 50:
                total_time = time.time() - start_reading
                throughput = len(all_resumes_data) / total_time
                print(f"\n📈 Performance Summary:")
                print(f"   • Total processing time: {total_time:.2f}s")
                print(f"   • Throughput: {throughput:.1f} resumes/second")
                if cache_info.get('batches_processed',0) > 0:
                    print(f"   • Batches processed: {cache_info['batches_processed']}/{cache_info.get('total_batches',0)}")

            return matched_candidates, cache_info
        else:
            print("\n❌ --- No candidates matched the required skills from the filtered resumes. ---")
            return [], cache_info

__all__ = ['ResumeParser']
