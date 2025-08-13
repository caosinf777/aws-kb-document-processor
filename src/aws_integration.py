"""Módulo de integración con AWS"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class S3UploadGenerator:
    """Generador de scripts para subir a S3"""
    
    @staticmethod
    def generate_s3_upload_script(output_base_path: Path) -> Path:
        """Genera script para subir a S3"""
        script_path = output_base_path / "upload_to_s3.sh"
        
        script_content = f"""#!/bin/bash
# Script para subir documentos procesados a S3
# Generado: {datetime.now().isoformat()}

# Configuración
BUCKET_NAME="tu-bucket-knowledge-base"  # CAMBIAR
PREFIX="knowledge-base/documents"
SOURCE_DIR="{output_base_path / '05_ready_to_upload'}"

echo "📤 Subiendo documentos a S3..."

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI no está instalado"
    echo "Instalar con: brew install awscli"
    exit 1
fi

# Verificar credenciales
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials no configuradas"
    echo "Configurar con: aws configure"
    exit 1
fi

# Crear bucket si no existe
aws s3 mb s3://$BUCKET_NAME 2>/dev/null

# Subir archivos
aws s3 sync "$SOURCE_DIR" "s3://$BUCKET_NAME/$PREFIX" \\
    --delete \\
    --exclude "*.DS_Store" \\
    --exclude ".*" \\
    --metadata "ProcessedDate=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "✅ Documentos subidos a s3://$BUCKET_NAME/$PREFIX"

# Opcional: Trigger Bedrock Knowledge Base ingestion
# aws bedrock start-ingestion-job \\
#     --knowledge-base-id "your-kb-id" \\
#     --data-source-id "your-ds-id"
"""
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Hacer ejecutable
        script_path.chmod(0o755)
        
        return script_path

class BedrockMetadataGenerator:
    """Generador de metadata para Bedrock Knowledge Base"""
    
    @staticmethod
    def create_metadata_json(doc_metadata: Dict, chunks: List[Dict]) -> Dict:
        """Crea metadata JSON completo para el documento"""
        return {
            'document_info': doc_metadata,
            'processing_info': {
                'processed_date': datetime.now().isoformat(),
                'processor_version': '1.0.0',
                'total_chunks': len(chunks),
                'chunking_strategy': {
                    'method': 'token_based',
                    'chunk_size': doc_metadata.get('chunk_size', 800),
                    'overlap': doc_metadata.get('chunk_overlap', 100)
                }
            },
            'bedrock_config': {
                'embedding_model': 'amazon.titan-embed-text-v2',
                'vector_dimensions': 1024,
                'recommended_search_k': min(len(chunks), 5)
            }
        }