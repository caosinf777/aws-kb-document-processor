"""Tests para la funcionalidad de chunking"""

import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor

def test_chunking_default_size():
    """Test default chunk size"""
    processor = DocumentProcessor()
    text = "This is a test. " * 1000
    chunks = processor.chunk_text(text, "default")
    
    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('chunk_index' in chunk for chunk in chunks)

def test_adaptive_chunking():
    """Test adaptive chunking for different document types"""
    processor = DocumentProcessor()
    text = "API documentation " * 500
    
    api_chunks = processor.chunk_text(text, "api_reference")
    guide_chunks = processor.chunk_text(text, "user_guide")
    
    # API reference should have smaller chunks
    assert len(api_chunks) > len(guide_chunks)