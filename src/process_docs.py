#!/usr/bin/env python3
"""
📚 AWS Knowledge Base Document Processor
Procesador automático de documentos para Bedrock Knowledge Base
Author: THAÄROS System
Version: 1.0.0
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import warnings
warnings.filterwarnings('ignore')

# ============================================
# INSTALADOR DE DEPENDENCIAS
# ============================================

def install_dependencies():
    """Instala todas las dependencias necesarias"""
    print("🔧 Instalando dependencias necesarias...")
    
    dependencies = [
        'boto3',
        'PyPDF2',
        'pdfplumber',
        'python-docx',
        'markdown',
        'beautifulsoup4',
        'tqdm',
        'colorama',
        'pandas',
        'openpyxl',
        'langchain',
        'tiktoken',
        'python-magic',
        'chardet'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', dep])
            print(f"  ✅ {dep} instalado")
        except:
            print(f"  ❌ Error instalando {dep}")
    
    print("\n✅ Dependencias instaladas!\n")

# Instalar dependencias si es necesario
try:
    import PyPDF2
    import pdfplumber
    import docx
    import markdown
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    from colorama import Fore, Style, init
    import pandas as pd
    import tiktoken
    import magic
    import chardet
    init(autoreset=True)
except ImportError:
    install_dependencies()
    # Reimportar después de instalar
    import PyPDF2
    import pdfplumber
    import docx
    import markdown
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    from colorama import Fore, Style, init
    import pandas as pd
    import tiktoken
    import magic
    import chardet
    init(autoreset=True)

# Importar módulos internos
from .config import Config
from .processors import DocumentTypeProcessor
from .utils import clean_text, table_to_markdown, detect_encoding
from .aws_integration import S3UploadGenerator, BedrockMetadataGenerator

# ============================================
# PROCESADOR DE DOCUMENTOS
# ============================================

class DocumentProcessor:
    """Procesador principal de documentos"""
    
    def __init__(self):
        self.config = Config()
        self.stats = {
            'processed': 0,
            'failed': 0,
            'total_size': 0,
            'total_chunks': 0
        }
        self.setup_directories()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def setup_directories(self):
        """Crea estructura de directorios"""
        print(f"{Fore.CYAN}📁 Creando estructura de directorios...{Style.RESET_ALL}")
        
        for folder, description in self.config.STRUCTURE.items():
            path = self.config.OUTPUT_BASE / folder
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {folder}/ - {description}")
        
        # Crear subdirectorios por servicio
        for service in self.config.AWS_SERVICES:
            service_path = self.config.OUTPUT_BASE / "02_structured" / service
            service_path.mkdir(exist_ok=True)
        
        print(f"\n{Fore.GREEN}✅ Estructura creada en: {self.config.OUTPUT_BASE}{Style.RESET_ALL}\n")
    
    def extract_text(self, file_path: Path) -> Tuple[str, Dict]:
        """Extrae texto de cualquier tipo de documento"""
        file_type = DocumentTypeProcessor.detect_file_type(file_path)
        text = ""
        metadata = {
            'filename': file_path.name,
            'file_type': file_type,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'extraction_date': datetime.now().isoformat()
        }
        
        try:
            if file_type == 'pdf':
                text, pdf_meta = DocumentTypeProcessor.extract_from_pdf(file_path)
                metadata.update(pdf_meta)
                
            elif file_type == 'docx':
                text = DocumentTypeProcessor.extract_from_docx(file_path)
                
            elif file_type in ['txt', 'md']:
                with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
                    text = f.read()
                    
            elif file_type == 'html':
                with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text = soup.get_text()
                    
            elif file_type in ['xlsx', 'csv']:
                text = DocumentTypeProcessor.extract_from_spreadsheet(file_path)
                
            else:
                print(f"  ⚠️  Tipo de archivo no soportado: {file_type}")
                return "", metadata
                
        except Exception as e:
            print(f"  ❌ Error extrayendo texto de {file_path.name}: {e}")
            return "", metadata
        
        # Limpiar y normalizar texto
        text = clean_text(text)
        metadata['text_length'] = len(text)
        metadata['token_count'] = len(self.tokenizer.encode(text, disallowed_special=()))
        
        return text, metadata
    
    def identify_aws_service(self, text: str, filename: str) -> str:
        """Identifica el servicio AWS del documento"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        for service in self.config.AWS_SERVICES:
            if service in filename_lower or service in text_lower[:1000]:
                return service
        
        return 'general'
    
    def identify_doc_type(self, text: str, filename: str) -> str:
        """Identifica el tipo de documento"""
        patterns = {
            'api_reference': ['api reference', 'api documentation', 'method', 'endpoint'],
            'user_guide': ['user guide', 'getting started', 'how to', 'tutorial'],
            'troubleshooting': ['troubleshooting', 'error', 'problem', 'issue', 'solution'],
            'best_practices': ['best practice', 'recommendation', 'optimization'],
            'tutorial': ['tutorial', 'example', 'walkthrough', 'step-by-step']
        }
        
        text_lower = text.lower()[:2000]  # Check first 2000 chars
        
        for doc_type, keywords in patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return doc_type
        
        return 'general'
    
    def chunk_text(self, text: str, doc_type: str) -> List[Dict]:
        """Divide texto en chunks optimizados"""
        chunk_size = self.config.CHUNK_SIZES.get(doc_type, self.config.CHUNK_SIZES['default'])
        overlap = self.config.CHUNK_OVERLAP
        
        # Tokenizar
        tokens = self.tokenizer.encode(text, disallowed_special=())
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Crear metadata para cada chunk
            chunk_data = {
                'text': chunk_text,
                'chunk_index': len(chunks),
                'token_count': len(chunk_tokens),
                'start_position': i,
                'end_position': min(i + chunk_size, len(tokens))
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def create_metadata_json(self, doc_metadata: Dict, chunks: List[Dict]) -> Dict:
        """Crea metadata JSON completo para el documento"""
        return BedrockMetadataGenerator.create_metadata_json(doc_metadata, chunks)
    
    def process_document(self, file_path: Path) -> bool:
        """Procesa un documento completo"""
        print(f"\n{Fore.YELLOW}📄 Procesando: {file_path.name}{Style.RESET_ALL}")
        print(f"   Tamaño: {file_path.stat().st_size / (1024*1024):.2f} MB")
        
        # Verificar tamaño
        if file_path.stat().st_size > self.config.MAX_FILE_SIZE_MB * 1024 * 1024:
            print(f"   ⚠️  Archivo muy grande (>{self.config.MAX_FILE_SIZE_MB}MB)")
            # Continuar de todos modos
        
        # Extraer texto y metadata
        text, metadata = self.extract_text(file_path)
        
        if not text:
            print(f"   ❌ No se pudo extraer texto")
            self.stats['failed'] += 1
            return False
        
        print(f"   ✅ Texto extraído: {len(text)} caracteres, {metadata.get('token_count', 0)} tokens")
        
        # Identificar servicio y tipo
        service = self.identify_aws_service(text, file_path.name)
        doc_type = self.identify_doc_type(text, file_path.name)
        
        metadata['aws_service'] = service
        metadata['doc_type'] = doc_type
        
        print(f"   📁 Servicio: {service} | Tipo: {doc_type}")
        
        # Crear chunks
        chunks = self.chunk_text(text, doc_type)
        print(f"   ✂️  Dividido en {len(chunks)} chunks")
        
        # Guardar archivos procesados
        base_name = file_path.stem
        safe_name = re.sub(r'', '_', base_name)
        
        # 1. Guardar texto completo procesado
        processed_path = self.config.OUTPUT_BASE / "01_processed" / f"{safe_name}_processed.txt"
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 2. Guardar en carpeta de servicio
        service_path = self.config.OUTPUT_BASE / "02_structured" / service / f"{safe_name}.txt"
        with open(service_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 3. Guardar chunks
        chunks_dir = self.config.OUTPUT_BASE / "04_chunks" / safe_name
        chunks_dir.mkdir(exist_ok=True)
        
        for i, chunk in enumerate(chunks):
            chunk_path = chunks_dir / f"chunk_{i:04d}.txt"
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk['text'])
        
        # 4. Guardar metadata
        full_metadata = self.create_metadata_json(metadata, chunks)
        metadata_path = self.config.OUTPUT_BASE / "03_metadata" / f"{safe_name}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2)
        
        # 5. Crear versión lista para S3
        s3_ready_dir = self.config.OUTPUT_BASE / "05_ready_to_upload" / service
        s3_ready_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear archivo consolidado con metadata embebida
        s3_doc = {
            'content': text,
            'metadata': metadata,
            'chunks': [{'index': c['chunk_index'], 'text': c['text']} for c in chunks]
        }
        
        s3_path = s3_ready_dir / f"{safe_name}.json"
        with open(s3_path, 'w', encoding='utf-8') as f:
            json.dump(s3_doc, f, indent=2)
        
        # Actualizar estadísticas
        self.stats['processed'] += 1
        self.stats['total_size'] += file_path.stat().st_size
        self.stats['total_chunks'] += len(chunks)
        
        print(f"   {Fore.GREEN}✅ Procesamiento completado{Style.RESET_ALL}")
        return True
    
    def process_directory(self, directory_path: Path):
        """Procesa todos los documentos en un directorio"""
        # Encontrar todos los archivos
        supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.html', '.xlsx', '.csv']
        files = []
        
        for ext in supported_extensions:
            files.extend(directory_path.glob(f'**/*{ext}'))
        
        if not files:
            print(f"{Fore.RED}❌ No se encontraron archivos soportados en {directory_path}{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📚 Encontrados {len(files)} documentos para procesar{Style.RESET_ALL}")
        
        # Procesar cada archivo con barra de progreso
        with tqdm(total=len(files), desc="Procesando documentos", unit="doc") as pbar:
            for file_path in files:
                try:
                    self.process_document(file_path)
                except Exception as e:
                    print(f"\n   ❌ Error procesando {file_path.name}: {e}")
                    self.stats['failed'] += 1
                finally:
                    pbar.update(1)
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Genera reporte de procesamiento"""
        report_path = self.config.OUTPUT_BASE / "logs" / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                **self.stats,
                'total_size_mb': self.stats['total_size'] / (1024 * 1024),
                'success_rate': (self.stats['processed'] / (self.stats['processed'] + self.stats['failed']) * 100) if (self.stats['processed'] + self.stats['failed']) > 0 else 0
            },
            'output_location': str(self.config.OUTPUT_BASE),
            'next_steps': [
                f"1. Revisar documentos procesados en: {self.config.OUTPUT_BASE / '01_processed'}",
                f"2. Verificar metadata en: {self.config.OUTPUT_BASE / '03_metadata'}",
                f"3. Subir a S3 desde: {self.config.OUTPUT_BASE / '05_ready_to_upload'}",
                "4. Configurar Bedrock Knowledge Base con los documentos procesados"
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Imprimir resumen
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📊 RESUMEN DE PROCESAMIENTO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"✅ Documentos procesados: {self.stats['processed']}")
        print(f"❌ Documentos fallidos: {self.stats['failed']}")
        print(f"📦 Tamaño total procesado: {self.stats['total_size'] / (1024*1024):.2f} MB")
        print(f"✂️  Total de chunks creados: {self.stats['total_chunks']}")
        print(f"📁 Salida guardada en: {self.config.OUTPUT_BASE}")
        print(f"📋 Reporte completo: {report_path}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # Script para subir a S3
        S3UploadGenerator.generate_s3_upload_script(self.config.OUTPUT_BASE)
        print(f"\n📜 Script de subida a S3 creado: {self.config.OUTPUT_BASE / 'upload_to_s3.sh'}")

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='📚 Procesador de Documentos para AWS Bedrock Knowledge Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s /path/to/document.pdf           # Procesar un archivo
  %(prog)s /path/to/documents/folder       # Procesar carpeta
  %(prog)s ~/Downloads/aws-docs            # Procesar directorio
        """
    )
    
    parser.add_argument(
        'path',
        type=str,
        help='Ruta al archivo o directorio a procesar'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Directorio de salida personalizado (default: ~/Documents/AWS_Knowledge_Base)'
    )
    
    args = parser.parse_args()
    
    # Banner
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║     📚 AWS Knowledge Base Document Processor v1.0        ║
║              Powered by THAÄROS System                   ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Validar path
    path = Path(args.path).expanduser().resolve()
    
    if not path.exists():
        print(f"{Fore.RED}❌ Error: La ruta no existe: {path}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Configurar output personalizado si se proporciona
    if args.output:
        Config.OUTPUT_BASE = Path(args.output).expanduser().resolve()
    
    # Crear procesador
    processor = DocumentProcessor()
    
    # Procesar
    if path.is_file():
        success = processor.process_document(path)
        if success:
            processor.generate_report()
    elif path.is_dir():
        processor.process_directory(path)
    else:
        print(f"{Fore.RED}❌ Error: La ruta no es un archivo ni directorio válido{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.GREEN}✨ Procesamiento completado exitosamente!{Style.RESET_ALL}")
    print(f"\n📌 Próximos pasos:")
    print(f"   1. Revisar documentos en: {Config.OUTPUT_BASE}")
    print(f"   2. Ejecutar script de subida: {Config.OUTPUT_BASE}/upload_to_s3.sh")
    print(f"   3. Configurar Bedrock Knowledge Base con el bucket S3")

if __name__ == "__main__":
    main()