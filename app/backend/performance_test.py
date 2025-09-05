#!/usr/bin/env python3
"""
Performance test script for the AI Resume Parser
Tests the scalability improvements for handling large datasets (1000+ resumes)
"""

import os
import time
import json
from parser import ResumeParser  # type: ignore

def test_performance():
    """Test the performance of the resume parser with different dataset sizes."""
    
    # Test configuration
    test_dir = "../../resumes"  # Adjust path as needed
    test_skills = "Python, JavaScript, React, Node.js, SQL"
    
    print("🚀 AI Resume Parser - Performance Test")
    print("=" * 50)
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory '{test_dir}' not found.")
        print("Please create a test directory with resume files or adjust the path.")
        return
    
    # Count available resume files
    supported_extensions = ('.txt', '.pdf', '.docx', '.doc')
    resume_files = [f for f in os.listdir(test_dir) if f.lower().endswith(supported_extensions)]
    
    if not resume_files:
        print(f"❌ No supported resume files found in '{test_dir}'.")
        return
    
    print(f"📂 Found {len(resume_files)} resume files for testing")
    print(f"🔍 Test query: {test_skills}")
    print()
    
    # Initialize parser
    parser = ResumeParser()
    
    # Test 1: Normal processing (with cache)
    print("🧪 Test 1: Normal Processing (with cache)")
    start_time = time.time()
    
    try:
        results, cache_info = parser.main(test_dir, test_skills, force_analyze=False)
        
        elapsed_time = time.time() - start_time
        
        print(f"✅ Test 1 Results:")
        print(f"   • Processing time: {elapsed_time:.2f}s")
        print(f"   • Candidates found: {len(results)}")
        print(f"   • Total resumes: {cache_info.get('total_resumes', 0)}")
        print(f"   • Filtered resumes: {cache_info.get('filtered_resumes', 0)}")
        print(f"   • Vector cache hit: {cache_info.get('vector_cache_hit', False)}")
        print(f"   • GenAI cache hit: {cache_info.get('genai_cache_hit', False)}")
        
        if cache_info.get('total_batches', 0) > 1:
            print(f"   • Batches processed: {cache_info.get('batches_processed', 0)}/{cache_info.get('total_batches', 0)}")
        
        # Calculate throughput
        if cache_info.get('total_resumes', 0) > 0:
            throughput = cache_info.get('total_resumes', 0) / elapsed_time
            print(f"   • Throughput: {throughput:.1f} resumes/second")
        
        print()
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return
    
    # Test 2: Force analyze (no cache)
    print("🧪 Test 2: Force Analyze (no cache)")
    start_time = time.time()
    
    try:
        results2, cache_info2 = parser.main(test_dir, test_skills, force_analyze=True)
        
        elapsed_time2 = time.time() - start_time
        
        print(f"✅ Test 2 Results:")
        print(f"   • Processing time: {elapsed_time2:.2f}s")
        print(f"   • Candidates found: {len(results2)}")
        print(f"   • Total resumes: {cache_info2.get('total_resumes', 0)}")
        print(f"   • Filtered resumes: {cache_info2.get('filtered_resumes', 0)}")
        
        if cache_info2.get('total_batches', 0) > 1:
            print(f"   • Batches processed: {cache_info2.get('batches_processed', 0)}/{cache_info2.get('total_batches', 0)}")
        
        # Calculate throughput
        if cache_info2.get('total_resumes', 0) > 0:
            throughput2 = cache_info2.get('total_resumes', 0) / elapsed_time2
            print(f"   • Throughput: {throughput2:.1f} resumes/second")
        
        print()
        
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return
    
    # Performance summary
    print("📊 Performance Summary")
    print("-" * 30)
    
    total_resumes = cache_info.get('total_resumes', 0)
    
    print(f"Dataset size: {total_resumes} resumes")
    
    if total_resumes <= 15:
        print("📋 Single batch processing")
    else:
        print("🔄 Multi-batch processing enabled")
    
    # Cache effectiveness
    cache_speedup = 0
    if elapsed_time2 > 0 and elapsed_time > 0:
        cache_speedup = elapsed_time2 / elapsed_time
        print(f"Cache speedup: {cache_speedup:.1f}x faster")
    
    # Scalability assessment
    if total_resumes >= 100:
        print("✅ Successfully processed large dataset (100+ resumes)")
    if total_resumes >= 500:
        print("🎉 Excellent scalability - handled 500+ resumes")
    if total_resumes >= 1000:
        print("🚀 Outstanding performance - processed 1000+ resumes!")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if cache_speedup > 5:
        print("   • Caching is highly effective for your dataset")
    if cache_info2.get('total_batches', 0) > 10:
        print("   • Consider reducing batch size for very large datasets")
    if total_resumes > 1000:
        print("   • Monitor memory usage for datasets larger than 1000 resumes")

if __name__ == "__main__":
    test_performance()
