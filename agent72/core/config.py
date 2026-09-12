"""Application configuration management using Pydantic Settings."""

from typing import List, Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application details
    PROJECT_NAME: str = "Agent 72: Strategic Planning Agent"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = (
        "Institutional strategic planning agent supporting evidence-based trajectory "
        "analysis, strategic options, scenario modelling, prioritization, and execution tracking."
    )
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Structured Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Relational Database
    # Default is SQLite for local development; Neon PostgreSQL for production
    DATABASE_URL: str = Field(
        default="sqlite:///./agent72.db",
        description="Database connection URL. SQLite for local/tests, Neon PostgreSQL for production.",
    )
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1)
    DB_POOL_RECYCLE: int = Field(default=1800, ge=60)
    DB_ECHO: bool = False

    # AI Provider Abstraction
    AI_PROVIDER_TYPE: Literal["mock", "openai", "gemini", "anthropic"] = "mock"
    AI_MODEL_NAME: str = "mock-strategic-v1"
    AI_API_KEY: Optional[str] = None

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    # Pagination Defaults & Limits
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 500

    # Configurable Data Freshness Policies (in days)
    DEFAULT_FRESHNESS_THRESHOLD_DAYS: int = 180
    FRESHNESS_THRESHOLDS_DAYS: dict[str, int] = Field(
        default_factory=lambda: {
            "ADMISSIONS_MARKET": 90,
            "RESEARCH_PRODUCTIVITY": 365,
            "FINANCE_RESOURCES": 365,
            "OPERATIONS": 30,
            "ACADEMIC_PERFORMANCE": 180,
            "PLACEMENT_EMPLOYER_DEMAND": 180,
            "FACULTY_CAPABILITY": 180,
            "INFRASTRUCTURE": 365,
            "EXTERNAL_REGULATORY": 180,
            "PEER_COMPETITOR": 180,
        }
    )

    # Phase 4 & Phase 5: Significant Change Threshold
    MIN_SIGNIFICANT_CHANGE_PERCENT: float = Field(
        default=2.0,
        description="Minimum percentage change required between observations to be classified as significant performance signal."
    )

    # Phase 6: Strategic Intelligence Constraint & Risk Thresholds
    INFRASTRUCTURE_CAPACITY_THRESHOLD: float = Field(
        default=85.0,
        description="Infrastructure utilization percentage above which a capacity constraint is flagged."
    )
    STUDENT_FACULTY_RATIO_THRESHOLD: float = Field(
        default=18.0,
        description="Student-to-faculty ratio above which a faculty load/capability constraint is flagged."
    )
    FACULTY_PHD_MIN_THRESHOLD: float = Field(
        default=70.0,
        description="Minimum faculty doctoral qualification percentage below which a capability constraint is flagged."
    )
    MEDIUM_RISK_SCORE_THRESHOLD: float = Field(
        default=0.40,
        description="Minimum score threshold for MEDIUM risk classification."
    )
    HIGH_RISK_SCORE_THRESHOLD: float = Field(
        default=0.70,
        description="Minimum score threshold for HIGH risk classification."
    )
    CRITICAL_RISK_SCORE_THRESHOLD: float = Field(
        default=0.85,
        description="Minimum score threshold for CRITICAL risk classification."
    )

    # Phase 7: Strategic Options Evaluation Weights (must sum to 1.00)
    OPTION_WEIGHT_STRATEGIC_ALIGNMENT: float = Field(
        default=0.20,
        description="Evaluation weight for strategic alignment dimension."
    )
    OPTION_WEIGHT_IMPACT: float = Field(
        default=0.20,
        description="Evaluation weight for expected impact dimension."
    )
    OPTION_WEIGHT_FEASIBILITY: float = Field(
        default=0.15,
        description="Evaluation weight for operational and technical feasibility dimension."
    )
    OPTION_WEIGHT_RESOURCE_EFFICIENCY: float = Field(
        default=0.10,
        description="Evaluation weight for resource efficiency dimension."
    )
    OPTION_WEIGHT_IMPLEMENTATION_RISK: float = Field(
        default=0.10,
        description="Evaluation weight for implementation risk dimension (higher score = lower risk)."
    )
    OPTION_WEIGHT_URGENCY: float = Field(
        default=0.10,
        description="Evaluation weight for organizational urgency dimension."
    )
    OPTION_WEIGHT_EVIDENCE_STRENGTH: float = Field(
        default=0.15,
        description="Evaluation weight for underlying evidence strength dimension."
    )

    # Phase 7: Strategic Options Priority Thresholds (0-100 scale)
    OPTION_PRIORITY_CRITICAL_THRESHOLD: float = Field(
        default=85.0,
        description="Minimum total score for CRITICAL priority option recommendation."
    )
    OPTION_PRIORITY_HIGH_THRESHOLD: float = Field(
        default=70.0,
        description="Minimum total score for HIGH priority option recommendation."
    )
    OPTION_PRIORITY_MEDIUM_THRESHOLD: float = Field(
        default=50.0,
        description="Minimum total score for MEDIUM priority option recommendation."
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """
        Normalize database URL for SQLAlchemy 2.0 compatibility.
        Neon and typical cloud providers provide urls beginning with 'postgres://' or 'postgresql://'.
        SQLAlchemy with psycopg v3 expects 'postgresql+psycopg://'.
        """
        if not v:
            return "sqlite:///./agent72.db"

        trimmed = v.strip()
        if trimmed.startswith("postgres://"):
            return trimmed.replace("postgres://", "postgresql+psycopg://", 1)
        elif trimmed.startswith("postgresql://") and not trimmed.startswith("postgresql+"):
            return trimmed.replace("postgresql://", "postgresql+psycopg://", 1)
        return trimmed

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql")


settings = Settings()
