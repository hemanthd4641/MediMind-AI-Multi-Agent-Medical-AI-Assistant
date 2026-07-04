import json
import re
import structlog
from typing import Dict, Any

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.schemas import DocumentClassification

logger = structlog.get_logger(__name__)

CLASSIFIER_PROMPT = """
You are a highly accurate Document Classification AI for a healthcare system.
Analyze the following document metadata and a snippet of its text to determine its type and the correct Pinecone namespace it should be stored in.

Document Types and Namespaces Mapping:
1. Medical Report (e.g., blood test, CBC, MRI scan, lab result, discharge summary)
   -> Namespace: "patient_reports"
2. Prescription (e.g., doctor's prescription, Rx, list of medicines prescribed)
   -> Namespace: "prescriptions"
3. Medical Knowledge (e.g., textbook extract, research paper, general disease information)
   -> Namespace: "medical_knowledge"
4. Clinical Guideline (e.g., WHO guidelines, CDC protocols, treatment pathways)
   -> Namespace: "clinical_guidelines"
5. Drug Information (e.g., pharmacology data, side effects sheet, FDA drug reference)
   -> Namespace: "drug_database"
6. Identity Document (e.g., Aadhaar card, Passport, Driver's License)
   -> Namespace: "identity_documents"
7. Insurance Document (e.g., Health insurance policy, claims, medical bills)
   -> Namespace: "identity_documents"
8. Unknown (If it doesn't fit any category)
   -> Namespace: "future_documents"

File Name: "{file_name}"
Provided Category: "{category}"

Text Snippet (first 1000 chars):
"{text_snippet}"

Return ONLY a valid JSON object matching this schema:
{{
    "document_type": "<one of the 8 types listed above>",
    "namespace": "<the exact mapped namespace>",
    "confidence": <float between 0.0 and 1.0>
}}
"""

class DocumentClassifierService:
    """Classifies uploaded documents into semantic namespaces using Groq."""

    async def classify(self, file_name: str, category: str, text_snippet: str) -> DocumentClassification:
        prompt = CLASSIFIER_PROMPT.format(
            file_name=file_name,
            category=category or "None",
            text_snippet=text_snippet[:1000]
        )
        
        system_prompt = "You are a Document Classification AI. Output ONLY valid JSON."
        
        try:
            res = await groq_llm_service.generate(prompt, system_prompt=system_prompt, agent_name="DocumentClassifier")
            
            match = re.search(r"\{.*\}", res, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(res)
                
            return DocumentClassification(
                document_type=str(data.get("document_type", "Unknown")),
                namespace=str(data.get("namespace", "future_documents")),
                confidence=float(data.get("confidence", 0.5))
            )
        except Exception as e:
            logger.error("Document classification failed, falling back to Unknown/future_documents", error=str(e))
            return DocumentClassification(
                document_type="Unknown",
                namespace="future_documents",
                confidence=0.1
            )

document_classifier_service = DocumentClassifierService()
