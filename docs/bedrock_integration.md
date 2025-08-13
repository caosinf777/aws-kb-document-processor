# Guía de Integración con Bedrock

## Descripción General

Esta guía explica cómo integrar documentos procesados con Amazon Bedrock Knowledge Base.

## Paso 1: Procesar Documentos

```bash
python -m src.process_docs /ruta/a/documentos


Paso 2: Subir a S3

aws s3 sync ~/Documents/AWS_Knowledge_Base/05_ready_to_upload s3://tu-bucket/


Paso 3: Configurar Knowledge Base

Ve a la Consola de Amazon Bedrock
Crea una nueva Knowledge Base
Selecciona tu bucket S3 como fuente de datos
Elige Titan Embeddings G1 - Text v2
Configura la estrategia de chunking (usa los valores predeterminados)
Inicia el trabajo de ingestión
Paso 4: Probar

Usa la función de prueba en la consola para verificar que tu knowledge base esté funcionando correctamente.

Configuración Avanzada

Metadata personalizada

Puedes personalizar la metadata que se genera para cada documento:

from src.aws_integration import BedrockMetadataGenerator

# Personalizar metadata
custom_metadata = {
    'filename': 'mi-documento.pdf',
    'custom_field': 'valor personalizado',
    'aws_service': 'bedrock'
}

# Generar metadata JSON
metadata_json = BedrockMetadataGenerator.create_metadata_json(custom_metadata, chunks)


Ingestión programática

Puedes automatizar la ingestión usando el AWS SDK:

import boto3

bedrock = boto3.client('bedrock-agent')

response = bedrock.start_ingestion_job(
    knowledgeBaseId='your-kb-id',
    dataSourceId='your-ds-id'
)