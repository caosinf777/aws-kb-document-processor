"""Configuración del procesador de documentos para AWS Knowledge Base"""

from pathlib import Path

class Config:
    """Configuración del procesador"""
    
    # Directorios
    OUTPUT_BASE = Path.home() / "Documents" / "AWS_Knowledge_Base"
    
    # Estructura de salida
    STRUCTURE = {
        "01_processed": "Documentos procesados y optimizados",
        "02_structured": "Documentos estructurados por servicio",
        "03_metadata": "Metadata y configuración",
        "04_chunks": "Documentos fragmentados para embeddings",
        "05_ready_to_upload": "Listos para S3",
        "logs": "Logs de procesamiento"
    }
    
    # Configuración de chunking
    CHUNK_SIZES = {
        "api_reference": 512,
        "user_guide": 1024,
        "tutorial": 1500,
        "troubleshooting": 800,
        "default": 800
    }
    
    CHUNK_OVERLAP = 100
    MAX_FILE_SIZE_MB = 100
    
    # Servicios AWS conocidos
    AWS_SERVICES = [
        'bedrock', 'lambda', 'apigateway', 'dynamodb', 's3', 
        'ec2', 'ecs', 'eks', 'waf', 'cloudfront', 'route53',
        'sagemaker', 'cognito', 'amplify', 'appsync'
    ]