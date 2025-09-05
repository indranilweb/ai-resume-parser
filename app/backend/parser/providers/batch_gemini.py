import json, time
from typing import List
import google.generativeai as genai

from ..config import GEMINI_MODEL, BATCH_DELAY_SECONDS, MAX_RESUMES_PER_BATCH
from ..prompt import construct_batch_prompt
from ..cache import generate_cache_key, get_cached_result, save_to_cache, clear_cache


def _process_resume_batch(batch_data: dict, required_skills: List[str], batch_num: int, total_batches: int) -> List[dict]:
    """Process a single batch of resumes through Gemini API."""
    print(f"\n🚀 Processing batch {batch_num}/{total_batches} ({len(batch_data)} resumes)...")
    try:
        prompt = construct_batch_prompt(batch_data, required_skills)
        model = genai.GenerativeModel(GEMINI_MODEL)
        generation_config = genai.types.GenerationConfig(temperature=0.2, response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        batch_results = json.loads(response.text)
        print(f"✅ Batch {batch_num}/{total_batches} completed: {len(batch_results)} candidates found")
        return batch_results
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in batch {batch_num}: {e}")
        print(f"Raw response: {getattr(response,'text','')[:500]}...")
        return []
    except Exception as e:
        print(f"❌ Error processing batch {batch_num}: {e}")
        return []


def _split_into_batches(items: dict, batch_size: int) -> List[dict]:
    items_list = list(items.items())
    return [dict(items_list[i:i+batch_size]) for i in range(0, len(items_list), batch_size)]


def parse_resumes_batch(resumes_data: dict, required_skills: List[str], force_analyze: bool=False):
    """Gemini implementation: Sends resume text to Gemini API for batch parsing and filtering."""
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

    cache_key = generate_cache_key(resumes_data, required_skills)
    cache_info['cache_key'] = cache_key
    print(f"🔑 Generated cache key: {cache_key[:12]}...")

    cached_result = None
    if not force_analyze:
        cached_result = get_cached_result(cache_key)
    else:
        print("🔥 Force analyze requested - skipping cache check")

    if cached_result is not None and not force_analyze:
        cache_info['gemini_cache_hit'] = True
        print("🎯 CACHE HIT: Found cached result! Skipping Gemini API call.")
        print(f"✅ Returning {len(cached_result)} cached candidate(s)")
        return cached_result, cache_info

    if force_analyze:
        clear_cache(cache_key)
    print("❌ CACHE MISS: No cached result found.")

    start_time = time.time()
    total_resumes = len(resumes_data)

    if total_resumes <= MAX_RESUMES_PER_BATCH:
        print(f"📝 Processing {total_resumes} resumes in single batch (Gemini)...")
        cache_info['total_batches'] = 1
        cache_info['batches_processed'] = 1
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            generation_config = genai.types.GenerationConfig(temperature=0.2, response_mime_type="application/json")
            response = model.generate_content(construct_batch_prompt(resumes_data, required_skills), generation_config=generation_config)
            parsed_data = json.loads(response.text)
            cache_info['processing_time'] = round(time.time() - start_time, 2)
            save_to_cache(cache_key, parsed_data)
            print("💾 CACHE SAVE: Result saved to cache for future use.")
            print(f"✅ Gemini API returned {len(parsed_data)} candidate(s) in {cache_info['processing_time']}s")
            return parsed_data, cache_info
        except json.JSONDecodeError:
            print("\n🚨 Error: Failed to decode JSON from the Gemini API response.")
            print(f"Raw Gemini Response:\n---\n{getattr(response,'text','')}\n---")
            return [], cache_info
        except Exception as e:
            print(f"\n🚨 An error occurred while communicating with the Gemini API: {e}")
            if 'response' in locals():
                print(f"Raw Gemini Response:\n---\n{getattr(response,'text','')}\n---")
            return [], cache_info
    else:
        print(f"📊 Large dataset detected ({total_resumes} resumes). Using Gemini batch processing...")
        batches = _split_into_batches(resumes_data, MAX_RESUMES_PER_BATCH)
        cache_info['total_batches'] = len(batches)
        print(f"🔄 Processing {total_resumes} resumes in {len(batches)} batches of max {MAX_RESUMES_PER_BATCH} resumes each...")

        all_results, successful_batches = [], 0
        for batch_num, batch_data in enumerate(batches, 1):
            batch_results = _process_resume_batch(batch_data, required_skills, batch_num, len(batches))
            if batch_results:
                all_results.extend(batch_results)
                successful_batches += 1
            if batch_num < len(batches):
                time.sleep(BATCH_DELAY_SECONDS)

        cache_info['batches_processed'] = successful_batches
        cache_info['processing_time'] = round(time.time() - start_time, 2)

        if all_results:
            save_to_cache(cache_key, all_results)
            print("💾 CACHE SAVE: Combined batch results saved to cache for future use.")
            print(f"✅ Gemini batch processing completed: {len(all_results)} total candidates found in {cache_info['processing_time']}s")
            print(f"📊 Successfully processed {successful_batches}/{len(batches)} batches")
        else:
            print(f"❌ No results from any Gemini batch. Processed {successful_batches}/{len(batches)} batches successfully.")
        return all_results, cache_info

__all__ = ['parse_resumes_batch']
