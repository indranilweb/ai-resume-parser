import json, time
from typing import List
from openai import AzureOpenAI

from ..config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    BATCH_DELAY_SECONDS,
    MAX_RESUMES_PER_BATCH,
)
from ..prompt import construct_batch_prompt
from ..cache import generate_cache_key, get_cached_result, save_to_cache, clear_cache


def _get_client():
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )


def _process_resume_batch(batch_data: dict, required_skills: List[str], batch_num: int, total_batches: int) -> List[dict]:
    print(f"\n🚀 Processing batch {batch_num}/{total_batches} ({len(batch_data)} resumes) via Azure OpenAI...")
    try:
        prompt = construct_batch_prompt(batch_data, required_skills)
        client = _get_client()
        # Using Chat Completions API
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts structured JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        raw_text = response.choices[0].message.content
        batch_results = json.loads(raw_text)
        if isinstance(batch_results, dict):
            # If the model wrapped in an object, try to find a list
            for v in batch_results.values():
                if isinstance(v, list):
                    batch_results = v
                    break
        print(f"✅ Batch {batch_num}/{total_batches} completed: {len(batch_results)} candidates found")
        return batch_results
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in Azure batch {batch_num}: {e}")
        print(f"Raw response (first 400 chars): {raw_text[:400] if 'raw_text' in locals() else ''}")
        return []
    except Exception as e:
        print(f"❌ Error processing Azure batch {batch_num}: {e}")
        return []


def _split_into_batches(items: dict, batch_size: int) -> List[dict]:
    items_list = list(items.items())
    return [dict(items_list[i:i+batch_size]) for i in range(0, len(items_list), batch_size)]


def parse_resumes_batch(resumes_data: dict, required_skills: List[str], force_analyze: bool=False):
    """Azure OpenAI implementation mirroring Gemini interface for provider switching."""
    cache_info = {
        "genai_cache_hit": False,  # kept for backward compatibility with existing keys
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
        cache_info['genai_cache_hit'] = True
        print("🎯 CACHE HIT: Found cached result! Skipping Azure OpenAI call.")
        print(f"✅ Returning {len(cached_result)} cached candidate(s)")
        return cached_result, cache_info

    if force_analyze:
        clear_cache(cache_key)
    print("❌ CACHE MISS: No cached result found.")

    start_time = time.time()
    total_resumes = len(resumes_data)

    if total_resumes <= MAX_RESUMES_PER_BATCH:
        print(f"📝 Processing {total_resumes} resumes in single batch (Azure OpenAI)...")
        cache_info['total_batches'] = 1
        cache_info['batches_processed'] = 1
        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured JSON."},
                    {"role": "user", "content": construct_batch_prompt(resumes_data, required_skills)},
                ],
            )
            raw_text = response.choices[0].message.content
            parsed_data = json.loads(raw_text)
            if isinstance(parsed_data, dict):
                # Try to unwrap to array if embedded
                for v in parsed_data.values():
                    if isinstance(v, list):
                        parsed_data = v
                        break
            cache_info['processing_time'] = round(time.time() - start_time, 2)
            save_to_cache(cache_key, parsed_data)
            print("💾 CACHE SAVE: Result saved to cache for future use.")
            print(f"✅ Azure OpenAI returned {len(parsed_data)} candidate(s) in {cache_info['processing_time']}s")
            return parsed_data, cache_info
        except json.JSONDecodeError:
            print("\n🚨 Error: Failed to decode JSON from the Azure OpenAI response.")
            print(f"Raw Azure Response:\n---\n{raw_text if 'raw_text' in locals() else ''}\n---")
            return [], cache_info
        except Exception as e:
            print(f"\n🚨 An error occurred while communicating with Azure OpenAI: {e}")
            if 'raw_text' in locals():
                print(f"Raw Azure Response:\n---\n{raw_text}\n---")
            return [], cache_info
    else:
        print(f"📊 Large dataset detected ({total_resumes} resumes). Using Azure batch processing...")
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
            print("💾 CACHE SAVE: Combined Azure batch results saved to cache for future use.")
            print(f"✅ Azure batch processing completed: {len(all_results)} total candidates found in {cache_info['processing_time']}s")
            print(f"📊 Successfully processed {successful_batches}/{len(batches)} batches")
        else:
            print(f"❌ No results from any Azure batch. Processed {successful_batches}/{len(batches)} batches successfully.")
        return all_results, cache_info

__all__ = ['parse_resumes_batch']
