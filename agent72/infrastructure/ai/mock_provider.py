"""Deterministic Mock AI Provider implementing IAIProvider."""

from typing import Any, Dict, Optional
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.core.logging import get_logger

logger = get_logger(__name__)


class MockAIProvider(IAIProvider):
    """
    Mock AI Provider suitable for testing, offline execution, and Phase 1 foundation.
    Can be swapped seamlessly for Gemini, OpenAI, or Anthropic adapters in subsequent phases.
    """

    def __init__(self, model_name: str = "mock-strategic-v1") -> None:
        self.model_name = model_name
        logger.info(f"Initialized MockAIProvider with model: {self.model_name}")

    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        logger.debug(f"MockAIProvider received prompt (length {len(prompt)}): {prompt[:100]}...")
        return (
            f"[MOCK_AI_RESPONSE: model={self.model_name}] "
            f"Strategic synthesis for query based on input evidence. (Length: {len(prompt)} chars)"
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "mock",
            "model": self.model_name,
            "latency_ms": 1.2,
        }
