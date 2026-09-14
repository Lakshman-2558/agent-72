"""Google Gemini AI Provider implementing IAIProvider interface."""

from typing import Any, Dict, Optional
import google.generativeai as genai

from agent72.core.config import settings
from agent72.core.logging import get_logger
from agent72.domain.interfaces.ai_provider import IAIProvider

logger = get_logger(__name__)

CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-pro-latest",
]


class GeminiAIProvider(IAIProvider):
    """
    Google Gemini AI Provider for Agent 72 strategic decision-support reasoning.
    """

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None) -> None:
        raw_name = model_name or settings.AI_MODEL_NAME
        # If raw_name is 1.5 or 2.5 which are deprecated in this environment, use 3.6-flash
        if "1.5" in raw_name or "2.5" in raw_name or raw_name == "mock-strategic-v1":
            self.model_name = "gemini-3.6-flash"
        else:
            self.model_name = raw_name

        self.api_key = api_key or settings.AI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            logger.info(f"Configured GeminiAIProvider with active model: {self.model_name}")
        else:
            logger.warning("GeminiAIProvider initialized without AI_API_KEY.")

    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 8192,
    ) -> str:
        """Generates completion using Google Gemini generative AI API."""
        if not self.api_key:
            return "Gemini API key is not configured in .env (AI_API_KEY)."

        full_prompt = prompt
        if system_instruction:
            full_prompt = f"### SYSTEM INSTRUCTION\n{system_instruction}\n\n### USER QUERY & CONTEXT\n{prompt}"

        # Try active model, then fallback candidates
        models_to_try = [self.model_name] + [m for m in CANDIDATE_MODELS if m != self.model_name]

        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )
                response = model.generate_content(full_prompt)
                if response and response.text:
                    self.model_name = m_name
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini model {m_name} failed: {e}. Trying fallback...")

        return "Gemini API error: unable to generate completion with available models."

    def health_check(self) -> Dict[str, Any]:
        """Performs quick connectivity verification."""
        return {
            "status": "configured" if self.api_key else "missing_key",
            "provider": "gemini",
            "model": self.model_name,
        }
