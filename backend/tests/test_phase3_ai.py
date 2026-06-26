"""
Unit tests for Phase 3 AI orchestration.
Groq is mocked so no actual API calls are made.
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Import the class directly so it is loaded and easier to patch
from backend.app.ai.services.groq_llm_service import GroqLLMService

# ── Router Agent ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_router_agent_symptom_check():
    """Router correctly classifies symptom-related messages."""
    mock_response = json.dumps({
        "intent": "symptom_check",
        "confidence": 0.92,
        "reason": "User describes physical symptoms."
    })
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from backend.app.ai.agents.router_agent import RouterAgent
        agent = RouterAgent()
        result = await agent.run("I have a fever and headache")

    assert result.intent == "symptom_check"
    assert result.confidence > 0.5


@pytest.mark.asyncio
async def test_router_agent_general_question():
    """Router correctly classifies general medical questions."""
    mock_response = json.dumps({
        "intent": "general_medical_question",
        "confidence": 0.88,
        "reason": "User asking an informational medical question."
    })
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from backend.app.ai.agents.router_agent import RouterAgent
        agent = RouterAgent()
        result = await agent.run("What is diabetes?")

    assert result.intent == "general_medical_question"


@pytest.mark.asyncio
async def test_router_agent_defaults_on_bad_json():
    """Router gracefully handles unparseable responses."""
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value="not json at all",
    ):
        from backend.app.ai.agents.router_agent import RouterAgent
        agent = RouterAgent()
        result = await agent.run("Hello")

    assert result.intent == "chat"
    assert result.confidence == 0.5


# ── Emergency Detection Agent ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_emergency_agent_critical():
    """Emergency agent returns CRITICAL for chest pain messages."""
    mock_response = json.dumps({
        "level": "CRITICAL",
        "reason": "Chest pain may indicate a heart attack.",
        "recommended_action": "Call 911 immediately."
    })
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from backend.app.ai.agents.emergency_detection_agent import EmergencyDetectionAgent
        agent = EmergencyDetectionAgent()
        result = await agent.run("I have severe chest pain and can't breathe")

    assert result.level == "CRITICAL"
    assert "911" in result.recommended_action


@pytest.mark.asyncio
async def test_emergency_agent_low():
    """Emergency agent returns LOW for non-urgent messages."""
    mock_response = json.dumps({
        "level": "LOW",
        "reason": "Minor cold symptoms.",
        "recommended_action": "Rest and stay hydrated."
    })
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from backend.app.ai.agents.emergency_detection_agent import EmergencyDetectionAgent
        agent = EmergencyDetectionAgent()
        result = await agent.run("I have a mild cold")

    assert result.level == "LOW"


@pytest.mark.asyncio
async def test_emergency_agent_defaults_on_bad_json():
    """Emergency agent defaults to LOW on parse failure."""
    with patch.object(
        GroqLLMService, "generate",
        new_callable=AsyncMock,
        return_value="bad response",
    ):
        from backend.app.ai.agents.emergency_detection_agent import EmergencyDetectionAgent
        agent = EmergencyDetectionAgent()
        result = await agent.run("Something wrong")

    assert result.level == "LOW"


# ── Medical AI Service ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_medical_ai_service_returns_response():
    """MedicalAIService.process_request returns a valid MedicalResponse."""
    from backend.app.ai.schemas import MedicalResponse

    mock_result = MedicalResponse(
        intent="general_medical_question",
        response="Diabetes is a chronic disease...",
        agents_used=["Router Agent", "Medical Knowledge Agent", "Response Composer Agent"],
        emergency_level=None,
    )
    with patch(
        "backend.app.ai.services.medical_ai_service._crew.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from backend.app.ai.services.medical_ai_service import MedicalAIService
        service = MedicalAIService()
        result = await service.process_request("What is diabetes?", "user-123")

    assert result.intent == "general_medical_question"
    assert "Router Agent" in result.agents_used


# ── API Endpoint ──────────────────────────────────────────────────────────────

def test_ai_chat_endpoint_unauthenticated():
    """POST /api/ai/chat returns 401 without token."""
    # Note: If httpx fails, the testclient is skipped or fails.
    # We will just verify it if possible.
    try:
        from fastapi.testclient import TestClient
        from backend.main import app as fastapi_app
    except Exception:
        pytest.skip("TestClient dependencies not found")

    client = TestClient(fastapi_app)
    resp = client.post("/api/ai/chat", json={"message": "Hello"})
    assert resp.status_code == 401


def test_ai_chat_endpoint_authenticated():
    """POST /api/ai/chat returns 200 with mocked auth and mocked AI service."""
    try:
        from fastapi.testclient import TestClient
        from backend.main import app as fastapi_app
    except Exception:
        pytest.skip("TestClient dependencies not found")
        
    from backend.app.ai.schemas import MedicalResponse

    mock_result = MedicalResponse(
        intent="chat",
        response="Hello! How can I help you today?",
        agents_used=["Router Agent", "Response Composer Agent"],
        emergency_level=None,
    )

    with (
        patch("backend.app.api.ai_chat.get_current_user", return_value={"sub": "user-123", "role": "patient"}),
        patch(
            "backend.app.api.ai_chat.medical_ai_service.process_request",
            new_callable=AsyncMock,
            return_value=mock_result,
        ),
    ):
        client = TestClient(fastapi_app)
        resp = client.post("/api/ai/chat", json={"message": "Hello"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "chat"
    assert "Router Agent" in data["agents_used"]

