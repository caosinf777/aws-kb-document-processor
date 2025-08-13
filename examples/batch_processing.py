#!/usr/bin/env python3
"""Ejemplo de procesamiento por lotes"""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Agregar directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor

def process_batch(file_paths):
    """Procesar múltiples archivos en paralelo"""
    processor = DocumentProcessor()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for path in file_paths:
            future = executor.submit(processor.process_document, path)
            futures.append(future)
        
        # Esperar a que todos terminen
        for future in futures:
            future.result()

def main():
    # Encontrar todos los PDFs
    pdf_files = list(Path("documents/").glob("**/*.pdf"))
    
    print(f"Procesando {len(pdf_files)} archivos...")
    process_batch(pdf_files)
    print("¡Procesamiento por lotes completado!")

if __name__ == "__main__":
    main()