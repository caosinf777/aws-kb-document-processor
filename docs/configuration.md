# Guía de Configuración

## Configuración por Defecto

El procesador usa valores predeterminados sensatos que funcionan para la mayoría de los casos.

## Personalizar Tamaños de Chunks

Edita el diccionario `CHUNK_SIZES` en `config.py`:

```python
CHUNK_SIZES = {
    "api_reference": 512,      # Más pequeño para contenido preciso
    "user_guide": 1024,        # Más grande para contexto
    "tutorial": 1500,          # Aún más grande para paso a paso
    "troubleshooting": 800,    # Medio para pares de Q&A
    "default": 800             # Tamaño por defecto
}
Añadir Servicios AWS

Agrega servicios a la lista AWS_SERVICES:

AWS_SERVICES = [
    'bedrock', 'lambda', 'tu-servicio-aqui'
]


Directorio de Salida Personalizado

Establece un directorio de salida personalizado:

from pathlib import Path
Config.OUTPUT_BASE = Path("/ruta/personalizada")


Configuración de Procesamiento

Otras configuraciones que puedes ajustar:

CHUNK_OVERLAP: Superposición entre chunks (por defecto: 100)
MAX_FILE_SIZE_MB: Tamaño máximo de archivo a procesar (por defecto: 100MB)
