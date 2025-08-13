#!/usr/bin/env python3
"""Ejemplo de configuración avanzada"""

import os
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.process_docs import DocumentProcessor
from src.config import Config

def main():
    # Personalizar configuración antes de inicializar
    Config.CHUNK_SIZES['custom'] = 600
    Config.AWS_SERVICES.append('custom-service')
    Config.OUTPUT_BASE = Path.home() / "custom_output"
    
    # Inicializar procesador con configuración personalizada
    processor = DocumentProcessor()
    
    # Procesar con configuración personalizada
    doc_path = Path("advanced_document.pdf")
    if doc_path.exists():
        processor.process_document(doc_path)

if __name__ == "__main__":
    main()