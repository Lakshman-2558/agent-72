"""Domain and application exceptions for Agent 72."""

from typing import Any, Dict, Optional


class Agent72Exception(Exception):
    """Base exception class for all Agent 72 domain and application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(Agent72Exception):
    """Raised when an entity is not found in the persistence store."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' not found.",
            status_code=404,
            details={"entity": entity_name, "id": str(entity_id)},
        )


class ValidationError(Agent72Exception):
    """Raised when a business rule or invariant validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=422,
            details=details,
        )


class BusinessRuleViolationError(Agent72Exception):
    """Raised when an operation violates a strategic planning domain rule."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=409,
            details=details,
        )


class DatabaseConnectionError(Agent72Exception):
    """Raised when unable to establish or maintain database connectivity."""

    def __init__(self, message: str = "Database connection error.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=503,
            details=details,
        )


class AIProviderError(Agent72Exception):
    """Raised when the AI provider fails to generate or complete an operation."""

    def __init__(self, message: str = "AI Provider failed to respond.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=502,
            details=details,
        )
