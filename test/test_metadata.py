"""Tests para la generación de metadata"""

import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor

def test_metadata_generation():
    """Test metadata generation"""
    processor = DocumentProcessor()
    
    doc_metadata = {
        'filename': 'test.pdf',
        'file_type': 'pdf',
        'file_size_mb': 1.5,
        'aws_service': 'bedrock',
        'doc_type': 'user_guide'
    }
    
    chunks = [{'text': 'chunk1', 'chunk_index': 0}]
    
    metadata = processor.create_metadata_json(doc_metadata, chunks)
    
    assert 'document_info' in metadata
    assert 'processing_info' in metadata
    assert 'bedrock_config' in metadata