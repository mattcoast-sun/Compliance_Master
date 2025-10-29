"""
Document parsing service using Docling
"""
from docling.document_converter import DocumentConverter
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DocumentParser:
    """Document parser using Docling library"""
    
    def __init__(self):
        """Initialize the document parser"""
        self.converter = DocumentConverter()
    
    def parse_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse a DOCX file and extract text content
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            # Convert the document
            result = self.converter.convert(file_path)
            
            # Extract text content
            extracted_text = result.document.export_to_markdown()
            
            # Extract metadata
            metadata = {
                "filename": Path(file_path).name,
                "num_pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                "format": "docx"
            }
            
            logger.info(f"Successfully parsed document: {file_path}")
            return extracted_text, metadata
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {str(e)}")
            raise
    
    def parse_document(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse any supported document format
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension in ['.docx', '.doc']:
            return self.parse_docx(file_path)
        else:
            # Docling supports multiple formats
            try:
                result = self.converter.convert(file_path)
                extracted_text = result.document.export_to_markdown()
                
                metadata = {
                    "filename": Path(file_path).name,
                    "format": file_extension[1:] if file_extension else "unknown"
                }
                
                return extracted_text, metadata
            except Exception as e:
                logger.error(f"Error parsing document {file_path}: {str(e)}")
                raise

