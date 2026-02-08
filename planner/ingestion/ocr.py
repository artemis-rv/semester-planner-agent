import os
import mimetypes
from typing import Optional, Dict, Any
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from docx import Document
from planner.utils.logger import setup_logger

logger = setup_logger(__name__)

class OCREngine:
    """
    Handles text extraction from various file formats.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def detect_file_type(self, file_path: str) -> str:
        """
        Detects file type based on extension or mime type.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        ext = os.path.splitext(file_path)[1].lower()
        mapping = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mapping.get(ext, 'application/octet-stream')

    def extract_text(self, file_path: str) -> str:
        """
        Main entry point for text extraction.
        Dispatches to specific methods based on file type.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = self.detect_file_type(file_path)
        logger.info(f"Detected file type: {file_type} for {file_path}")

        if 'pdf' in file_type:
            return self._extract_from_pdf(file_path)
        elif 'wordprocessingml' in file_type or file_path.endswith('.docx'):
            return self._extract_from_docx(file_path)
        elif 'image' in file_type:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _extract_from_image(self, image_path: str) -> str:
        """Extracts text from an image using Tesseract."""
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting from image: {e}")
            raise

    def _extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from PDF. Tries text layer first, 
        falls back to OCR if text layer is empty or poor quality.
        """
        text = ""
        try:
            # Try PyMuPDF first (fast, handles text layer)
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()

            # If text is very short or looks like junk, try OCR
            if len(text.strip()) < 100:  # Threshold for "empty" or scanned PDF
                logger.info("PDF text layer is empty or too short. Falling back to OCR.")
                images = convert_from_path(pdf_path)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img)
                return ocr_text.strip()
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            raise

    def _extract_from_docx(self, docx_path: str) -> str:
        """Extracts text from a DOCX file."""
        try:
            doc = Document(docx_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text).strip()
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
            raise

if __name__ == "__main__":
    # Example usage for testing
    import sys
    if len(sys.argv) > 1:
        engine = OCREngine()
        result = engine.extract_text(sys.argv[1])
        logger.info(f"Ocr Extraction Complete. Length: {len(result)}")
