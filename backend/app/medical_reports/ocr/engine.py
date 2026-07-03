import os
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

class OCREngine:
    def __init__(self):
        self.paddle_ocr = None
        self._init_paddle()

    def _init_paddle(self):
        try:
            from paddleocr import PaddleOCR
            # use_angle_cls=True to automatically rotate images if needed
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        except Exception as e:
            logger.error("Failed to initialize PaddleOCR", error=str(e))

    def extract_text(self, file_path: str, mime_type: str) -> str:
        """Extracts text from a given file based on its mime type."""
        logger.info("Starting OCR extraction", file_path=file_path, mime_type=mime_type)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if 'pdf' in mime_type.lower():
            return self._extract_from_pdf(file_path)
        elif any(ext in mime_type.lower() for ext in ['image', 'jpeg', 'png', 'jpg']):
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported mime type: {mime_type}")

    def _extract_from_pdf(self, file_path: str) -> str:
        try:
            import pdfplumber
            extracted_text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
            
            full_text = "\n".join(extracted_text).strip()
            
            # Fallback to image OCR if PDF is just scanned images (no text layer)
            if len(full_text) < 50:
                logger.info("PDF has very little text. Falling back to image-based OCR.")
                return self._extract_pdf_as_images(file_path)
                
            return full_text
        except Exception as e:
            logger.error("PDF Extraction failed", error=str(e))
            raise

    def _extract_pdf_as_images(self, file_path: str) -> str:
        # For simplicity in this project phase without heavy image conversions (like pdf2image), 
        # we will rely on PyMuPDF to render the page to an image in memory, then run PaddleOCR on it.
        try:
            import fitz # PyMuPDF
            import numpy as np
            
            if not self.paddle_ocr:
                return "OCR Engine not initialized."

            extracted_text = []
            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap()
                # Convert to numpy array for paddleocr
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4: # RGBA
                    import cv2
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                
                result = self.paddle_ocr.ocr(img, cls=True)
                page_text = self._parse_paddle_result(result)
                extracted_text.append(page_text)
                
            return "\n".join(extracted_text)
        except Exception as e:
            logger.error("Scanned PDF OCR failed", error=str(e))
            return "Failed to extract text from scanned PDF."

    def _extract_from_image(self, file_path: str) -> str:
        if not self.paddle_ocr:
            raise RuntimeError("PaddleOCR is not available.")
            
        try:
            result = self.paddle_ocr.ocr(file_path, cls=True)
            return self._parse_paddle_result(result)
        except Exception as e:
            logger.error("Image OCR failed", error=str(e))
            raise

    def _parse_paddle_result(self, result) -> str:
        text_lines = []
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                # line format: [[(x1,y1), ...], ('text', confidence)]
                text_content = line[1][0]
                text_lines.append(text_content)
        return "\n".join(text_lines)

ocr_engine = OCREngine()
