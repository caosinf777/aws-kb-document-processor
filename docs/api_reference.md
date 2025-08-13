# Referencia de API

## DocumentProcessor

Clase principal para procesar documentos.

### Métodos

#### `__init__(self)`
Inicializa el procesador de documentos.

#### `process_document(file_path: Path) -> bool`
Procesa un solo documento.

**Parámetros:**
- `file_path`: Ruta al documento

**Retorna:**
- `bool`: True si fue exitoso, False en caso contrario

#### `process_directory(directory_path: Path)`
Procesa todos los documentos en un directorio.

**Parámetros:**
- `directory_path`: Ruta al directorio

#### `chunk_text(text: str, doc_type: str) -> List[Dict]`
Divide texto en chunks.

**Parámetros:**
- `text`: Texto a dividir
- `doc_type`: Tipo de documento para chunking adaptativo

**Retorna:**
- Lista de diccionarios de chunks

#### `extract_text(file_path: Path) -> Tuple[str, Dict]`
Extrae texto de cualquier tipo de documento.

**Parámetros:**
- `file_path`: Ruta al archivo

**Retorna:**
- `Tuple[str, Dict]`: Texto extraído y metadata

#### `generate_report()`
Genera reporte de procesamiento.

## DocumentTypeProcessor

Clase para procesar diferentes tipos de documentos.

### Métodos

#### `detect_file_type(file_path: Path) -> str`
Detecta el tipo de archivo.

#### `extract_from_pdf(file_path: Path) -> Tuple[str, Dict]`
Extrae texto de archivos PDF.

#### `extract_from_docx(file_path: Path) -> str`
Extrae texto de documentos Word.

## BedrockMetadataGenerator

Clase para generar metadata para Bedrock Knowledge Base.

### Métodos

#### `create_metadata_json(doc_metadata: Dict, chunks: List[Dict]) -> Dict`
Crea metadata JSON completo para el documento.