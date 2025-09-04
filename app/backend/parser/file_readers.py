import os
from typing import Dict, List, Optional
import pypdf
import docx
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import ENABLE_PARALLEL_READING, MAX_WORKERS
from .progress import ProgressTracker


def read_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = "".join((page.extract_text() or "") + "\n" for page in reader.pages)
            return text
    except Exception as e:
        print(f"📄❌ Error reading PDF file '{os.path.basename(file_path)}': {e}")
        return ""


def read_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"📄❌ Error reading DOCX file '{os.path.basename(file_path)}': {e}")
        return ""


def read_txt(file_path: str) -> str:
    """Reads a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"📄❌ Error reading TXT file '{os.path.basename(file_path)}': {e}")
        return ""


def get_resume_content(file_path: str) -> str:
    """
    Reads the content of a resume file by dispatching to the correct reader
    based on the file extension.
    """
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext == '.txt': return read_txt(file_path)
    if ext == '.pdf': return read_pdf(file_path)
    if ext == '.docx': return read_docx(file_path)
    if ext == '.doc':
        print(f"⚠️ Warning: .doc not supported. Convert '{filename}' to .docx or .pdf.")
        return ""
    print(f"⚠️ Warning: Unsupported file type '{ext}' for '{filename}'. Skipping.")
    return ""


def _read_resume_file_safe(file_info: tuple) -> tuple:
    """Safely read a single resume file with error handling."""
    file_path, filename = file_info
    try:
        content = get_resume_content(file_path)
        if content and content.strip():
            return filename, content
        print(f"  ⚠️ Empty content from '{filename}'. Skipping.")
        return filename, None
    except Exception as e:
        print(f"  ❌ Error reading '{filename}': {e}")
        return filename, None


def read_resumes_parallel(resume_files: List[str], resume_dir: str, progress_tracker: Optional[ProgressTracker] = None) -> Dict[str, str]:
    """Read multiple resume files in parallel for better performance."""
    resumes_data: Dict[str, str] = {}
    
    if not ENABLE_PARALLEL_READING or len(resume_files) < 4:
        # Sequential reading for small datasets
        for filename in resume_files:
            file_path = os.path.join(resume_dir, filename)
            content = get_resume_content(file_path)
            if content and content.strip():
                resumes_data[filename] = content
                print(f"  ✅ Successfully read '{filename}'")
                if progress_tracker: 
                    progress_tracker.update()
            else:
                print(f"  ❌ Could not read content from '{filename}'. Skipping.")
        return resumes_data

    # Parallel reading for larger datasets
    print(f"📚 Reading {len(resume_files)} files in parallel (max {MAX_WORKERS} workers)...")

    file_infos = [(os.path.join(resume_dir, f), f) for f in resume_files]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_read_resume_file_safe, fi): fi[1] for fi in file_infos}

        for future in as_completed(futures):
            filename, content = future.result()
            if content:
                resumes_data[filename] = content
                print(f"  ✅ Successfully read '{filename}'")
            if progress_tracker: progress_tracker.update()

    return resumes_data

__all__ = ['get_resume_content','read_resumes_parallel']
