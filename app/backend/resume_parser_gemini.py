"""Backward-compatible shim.

The original monolithic implementation has been refactored into the
`parser` package (see `parser/`). This module re-exports the primary
API surface so existing imports continue working:

from resume_parser_gemini import ResumeParser, clear_cache, CACHE_DIR, VECTOR_DB_DIR

Update your imports to:

from parser import ResumeParser

This shim will be removed in a future release.
"""
from parser import ResumeParser, clear_cache  # type: ignore
from parser.config import CACHE_DIR, VECTOR_DB_DIR  # type: ignore

__all__ = [
    'ResumeParser', 'clear_cache', 'CACHE_DIR', 'VECTOR_DB_DIR'
]
