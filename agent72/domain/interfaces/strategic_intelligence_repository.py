"""Abstract Repository Protocol for Institutional Strategic Intelligence Analyses."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.strategic_intelligence import StrategicIntelligenceAnalysis


class IStrategicIntelligenceRepository(ABC):
    """Abstract persistence interface for immutable institutional strategic intelligence snapshots."""

    @abstractmethod
    def create_strategic_intelligence_analysis(
        self, analysis: StrategicIntelligenceAnalysis
    ) -> StrategicIntelligenceAnalysis:
        """Persist a completed strategic intelligence snapshot."""
        pass

    @abstractmethod
    def get_strategic_intelligence_analysis_by_id(
        self, analysis_id: str
    ) -> Optional[StrategicIntelligenceAnalysis]:
        """Retrieve a specific strategic intelligence snapshot by unique ID."""
        pass

    @abstractmethod
    def list_strategic_intelligence_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[StrategicIntelligenceAnalysis]:
        """List historical strategic intelligence analyses with filtering and pagination."""
        pass

    @abstractmethod
    def count_strategic_intelligence_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        """Count matching strategic intelligence analyses for pagination."""
        pass
