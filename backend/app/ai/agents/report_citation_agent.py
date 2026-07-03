import structlog
from typing import List, Dict, Any
from backend.app.ai.services.vector_store import vector_store

logger = structlog.get_logger(__name__)

class ReportCitationAgent:
    """Retrieves supporting educational info for report parameters from the RAG DB."""

    async def run(self, parameters: List[str]) -> Dict[str, Any]:
        logger.info("ReportCitationAgent started", params_count=len(parameters))
        
        citations = []
        
        for param in parameters:
            try:
                # Search vector store for the parameter
                query = f"What is {param} and why is it important in a medical report?"
                results = vector_store.search(query, top_k=2)
                
                for r in results:
                    citations.append({
                        "parameter": param,
                        "text": r.get("content", ""),
                        "source": r.get("metadata", {}).get("title", "Unknown Source"),
                        "page": r.get("metadata", {}).get("page_number", 1)
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch citations for {param}", error=str(e))
                
        # Filter duplicates or low relevance
        unique_citations = []
        seen = set()
        for c in citations:
            key = f"{c['parameter']}-{c['source']}-{c['page']}"
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)

        # In a real app we might use LLM to summarize the citations or pick best
        return {"citations": unique_citations}
