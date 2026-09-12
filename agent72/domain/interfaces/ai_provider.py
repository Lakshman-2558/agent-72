"""Abstract AI Provider Interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IAIProvider(ABC):
    """Abstract interface for LLM/AI model interaction."""

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text completion from prompt."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check AI provider connectivity and readiness."""
        pass
