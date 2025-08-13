"""Utilidades para el procesador de documentos"""

import hashlib
import re
import chardet
from pathlib import Path
from typing import List

def detect_encoding(file_path: Path) -> str:
    """Detecta encoding del archivo"""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
            return result['encoding'] or 'utf-8'
    except:
        return 'utf-8'

def clean_text(text: str) -> str:
    """Limpia y normaliza el texto"""
    # Eliminar caracteres no imprimibles
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Eliminar headers/footers comunes de AWS
    patterns = [
        r'Copyright © \d{4}.*?Amazon\.com.*?All rights reserved\.',
        r'AWS.*?User Guide',
        r'Table of Contents',
        r'Page \d+ of \d+',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def table_to_markdown(table_data: List[List]) -> str:
    """Convierte tabla a formato markdown"""
    if not table_data or not table_data[0]:
        return ""
    
    # Headers
    headers = table_data[0]
    markdown = "| " + " | ".join(str(h) for h in headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Rows
    for row in table_data[1:]:
        if row:  # Skip empty rows
            markdown += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return markdown

def calculate_file_hash(file_path: Path) -> str:
    """Calcula hash SHA256 del archivo"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"