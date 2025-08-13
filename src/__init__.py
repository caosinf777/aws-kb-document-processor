"""AWS KB Document Processor - Transform documents for Amazon Bedrock Knowledge Base"""

__version__ = "1.0.0"
__author__ = "THAÄROS System"
__email__ = "contact@example.com"

from .process_docs import DocumentProcessor
from .config import Config

__all__ = ['DocumentProcessor', 'Config']