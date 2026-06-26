import io
from typing import List, Dict, Any

class DocumentLoader:
    """
    Handles extracting text from supported document types (PDF, TXT).
    """

    @staticmethod
    def load_pdf(file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """
        Parses a PDF file from bytes.
        Returns a list of dicts, one for each page:
        {
            "page_number": int,
            "text": str,
            "metadata": dict
        }
        """
        import fitz  # PyMuPDF
        
        pages_data = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text")
            # Minimal cleaning
            text = text.replace("\x00", "").strip()
            
            pages_data.append({
                "page_number": i + 1,
                "text": text,
                "metadata": {
                    "source": file_name,
                    "type": "pdf"
                }
            })
        return pages_data

    @staticmethod
    def load_text(file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """
        Parses a text file. Treats it as a single page document.
        """
        text = file_bytes.decode("utf-8", errors="replace").strip()
        return [{
            "page_number": 1,
            "text": text,
            "metadata": {
                "source": file_name,
                "type": "txt"
            }
        }]

    @classmethod
    def load(cls, file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
        """
        Detects file type and delegates to the appropriate loader.
        """
        if file_name.lower().endswith(".pdf"):
            return cls.load_pdf(file_bytes, file_name)
        elif file_name.lower().endswith(".txt") or file_name.lower().endswith(".md"):
            return cls.load_text(file_bytes, file_name)
        else:
            # Fallback to text parsing
            return cls.load_text(file_bytes, file_name)
