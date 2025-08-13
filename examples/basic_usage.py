#!/usr/bin/env python3
"""Ejemplo básico de uso"""

import os
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor

def main():
    # Inicializar procesador
    processor = DocumentProcessor()
    
    # Procesar un solo documento
    doc_path = Path("example_document.pdf")
    if doc_path.exists():
        success = processor.process_document(doc_path)
        if success:
            print("¡Documento procesado exitosamente!")
    
    # Procesar un directorio
    dir_path = Path("documents/")
    if dir_path.exists():
        processor.process_directory(dir_path)

if __name__ == "__main__":
    main()