import tiktoken
from typing import List, Dict, Any

class SemanticChunker:
    """
    Chunks text into smaller segments based on token count, with overlap.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Using cl100k_base which is standard for newer OpenAI models, a good proxy for general tokenization
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_document(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of page dicts (from DocumentLoader) and chunks the text.
        Returns a list of chunk dicts.
        """
        chunks = []
        chunk_index = 0

        for page in pages:
            text = page.get("text", "")
            if not text.strip():
                continue

            page_number = page.get("page_number", 1)
            metadata = page.get("metadata", {})

            tokens = self.tokenizer.encode(text)
            
            i = 0
            while i < len(tokens):
                chunk_tokens = tokens[i : i + self.chunk_size]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": chunk_text.strip(),
                    "page_number": page_number,
                    "token_count": len(chunk_tokens),
                    "metadata": metadata
                })
                chunk_index += 1
                
                # Advance by chunk_size - overlap
                i += (self.chunk_size - self.chunk_overlap)
                
                # If we've advanced but there's less than overlap remaining, we're done with this text
                if i >= len(tokens):
                    break

        return chunks
