"""Memory interface stubs for Phase 3. Persistence will be implemented in a later phase."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List


class BaseMemory(ABC):
    """Abstract base for all memory interfaces."""

    @abstractmethod
    def add(self, key: str, value: Any) -> None:
        ...

    @abstractmethod
    def get(self, key: str) -> Any:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...


class ConversationMemory(BaseMemory):
    """Stores conversation turns for a session. Not persisted yet."""

    def __init__(self) -> None:
        self._history: List[dict] = []

    def add(self, key: str, value: Any) -> None:
        self._history.append({"role": key, "content": value})

    def get(self, key: str) -> List[dict]:
        return [m for m in self._history if m["role"] == key]

    def clear(self) -> None:
        self._history = []


class PatientMemory(BaseMemory):
    """Stores structured patient context. Not persisted yet."""

    def __init__(self) -> None:
        self._data: dict = {}

    def add(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def clear(self) -> None:
        self._data = {}


class MedicalHistoryMemory(BaseMemory):
    """Stores medical history entries. Not persisted yet."""

    def __init__(self) -> None:
        self._entries: List[Any] = []

    def add(self, key: str, value: Any) -> None:
        self._entries.append({"type": key, "data": value})

    def get(self, key: str) -> List[Any]:
        return [e for e in self._entries if e["type"] == key]

    def clear(self) -> None:
        self._entries = []
