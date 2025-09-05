# AI Resume Parser

This project is an AI-powered resume parser designed to extract and analyze information from resumes efficiently. **Now optimized to handle large datasets of 1000+ resumes** with advanced batch processing and caching.

## Features

- **🚀 Scalable Processing**: Handles 1000+ resumes efficiently with batch processing
- **🎯 Semantic Search**: Vector-based filtering to reduce API costs and improve accuracy
- **⚡ Smart Caching**: Multi-layer caching system for both vector search and API results
- **📊 Progress Tracking**: Real-time progress indicators for large datasets
- **🔄 Batch Processing**: Automatic batching to handle API limits and rate limiting
- **💾 Multiple Formats**: Supports PDF, DOCX, TXT, and DOC files
- **🔍 Skill Matching**: Advanced skill-based candidate filtering
- **📈 Performance Metrics**: Detailed performance analytics and throughput monitoring

### Core Capabilities
- Extracts key details: name, contact information, skills, experience, and companies
- Provides structured JSON output for easy integration
- Web-based interface with real-time processing updates
- Force analyze option to bypass caching when needed

## Scalability Features

### Large Dataset Handling (1000+ Resumes)
- **Batch Processing**: Automatically processes resumes in optimized batches (configurable, default: 15 per batch)
- **Parallel File Reading**: Multi-threaded file reading for faster I/O (configurable, default: 4 workers)
- **Memory Optimization**: Efficient memory usage patterns for large datasets
- **Progress Tracking**: Real-time progress indicators with ETA calculations
- **Rate Limiting**: Built-in delays between API calls to avoid rate limits

### Performance Configuration
The application includes configurable performance settings in `config.py`:

```python
PERFORMANCE_CONFIG = {
    "MAX_RESUMES_PER_BATCH": 15,     # Max resumes in a single GenAI API call
    "ENABLE_PARALLEL_READING": True, # Enable parallel file reading
    "MAX_WORKERS": 4,                # Number of worker threads for file reading
    "SIMILARITY_THRESHOLD": 0.3,     # Vector search similarity threshold
    "BATCH_DELAY_SECONDS": 1,        # Delay between API batches to avoid rate limiting
    "ENABLE_MEMORY_OPTIMIZATION": True, # Enable memory optimization for large datasets
}
```

### Caching System
- **Vector Cache**: Caches semantic search results to avoid recomputing embeddings
- **GenAI Cache**: Caches API results for identical queries and resume sets
- **Smart Cache Keys**: Uses content hashes to detect changes automatically
- **Selective Cache Clearing**: Clear specific caches or all caches as needed

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/your-username/ai-resume-parser.git
    ```
2. Navigate to the project directory:
    ```
    cd ai-resume-parser
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Place resumes in the `resumes` folder or specify a custom directory.
2. Create Gemini API key at `https://aistudio.google.com/app/apikey`.
3. Update the API key in `config.py` or set in environment variable.
4. Run the frontend and backend server:
    ```
    serve.bat
    ```
5. Access the app at `http://localhost:8080/` in browser.

### Processing Large Datasets

For datasets with 1000+ resumes:

1. **Use Semantic Filtering**: Specify relevant skills to reduce the number of resumes sent to the AI API
2. **Monitor Progress**: Watch the real-time progress indicators and batch processing status
3. **Leverage Caching**: Subsequent runs with the same data will be much faster
4. **Adjust Configuration**: Modify `PERFORMANCE_CONFIG` in `config.py` for your specific needs

### Performance Testing

Run the included performance test to evaluate your setup:

```bash
cd app/backend
python performance_test.py
```

This will test the system with your available resume files and provide performance metrics.

## Performance Benchmarks

Expected performance for different dataset sizes:

- **Small (1-50 resumes)**: 1-5 seconds (single batch)
- **Medium (51-200 resumes)**: 10-30 seconds (2-13 batches)
- **Large (201-500 resumes)**: 30-90 seconds (14-33 batches)
- **Very Large (501-1000+ resumes)**: 90-300 seconds (34+ batches)

*Performance varies based on resume content, skills query complexity, and API response times.*

## Technical Architecture

### Components
- **Backend**: FastAPI server with AI resume parsing logic
- **Frontend**: Modern web interface with real-time updates
- **Vector Search**: Sentence transformers with FAISS for semantic filtering
- **Caching**: Multi-layer file-based caching system
- **Batch Processing**: Intelligent batching with progress tracking

### API Endpoints
- `POST /parse-resume`: Main processing endpoint with batch support
- `POST /clear-cache`: Cache management (current or all)

## Configuration

Key configuration options in `app/backend/config.py`:

- **GEMINI_KEY**: Your Gemini API key
- **GEMINI_MODEL**: AI model to use (default: gemini-2.5-flash)
- **PERFORMANCE_CONFIG**: Scalability and performance settings

## Troubleshooting Large Datasets

1. **Memory Issues**: Reduce `MAX_WORKERS` or `MAX_RESUMES_PER_BATCH`
2. **API Rate Limits**: Increase `BATCH_DELAY_SECONDS`
3. **Slow Processing**: Enable parallel reading and check network connection
4. **Cache Issues**: Use "Clear All Cache" and retry

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
