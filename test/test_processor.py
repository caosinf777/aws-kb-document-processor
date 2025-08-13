"""Tests para el procesador de documentos"""

import pytest
import os
from pathlib import Path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor

def test_processor_initialization():
    """Test processor initialization"""
    processor = DocumentProcessor()
    assert processor is not None
    assert processor.config is not None

def test_text_extraction():
    """Test text extraction from sample file"""
    processor = DocumentProcessor()
    sample_file = Path(os.path.join(os.path.dirname(__file__), "fixtures", "sample.txt"))
    
    if sample_file.exists():
        text, metadata = processor.extract_text(sample_file)
        assert text is not None
        assert metadata is not None
        assert 'filename' in metadata
    else:
        pytest.skip("Sample file not found")