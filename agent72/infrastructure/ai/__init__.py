"""AI Provider infrastructure exports and factory."""

from agent72.core.config import settings
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.infrastructure.ai.mock_provider import MockAIProvider


def get_ai_provider() -> IAIProvider:
    """Factory returning configured AI provider instance."""
    provider_type = settings.AI_PROVIDER_TYPE.lower()
    if provider_type == "gemini":
        try:
            from agent72.infrastructure.ai.gemini_provider import GeminiAIProvider
            return GeminiAIProvider(model_name=settings.AI_MODEL_NAME, api_key=settings.AI_API_KEY)
        except Exception:
            return MockAIProvider(model_name=settings.AI_MODEL_NAME)
    if provider_type == "mock":
        return MockAIProvider(model_name=settings.AI_MODEL_NAME)
    return MockAIProvider(model_name=settings.AI_MODEL_NAME)


__all__ = ["MockAIProvider", "get_ai_provider"]

