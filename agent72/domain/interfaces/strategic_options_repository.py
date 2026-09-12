"""Abstract Repository Protocol for Institutional Strategic Options Analyses (Phase 7)."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.strategic_options import StrategicOptionsAnalysis


class IStrategicOptionsRepository(ABC):
    """Abstract persistence interface for immutable institutional strategic options snapshots."""

    @abstractmethod
    def create_analysis(
        self, analysis: StrategicOptionsAnalysis
    ) -> StrategicOptionsAnalysis:
        """Persist a completed strategic options analysis snapshot."""
        pass

    @abstractmethod
    def get_analysis_by_id(
        self, analysis_id: str
    ) -> Optional[StrategicOptionsAnalysis]:
        """Retrieve a specific strategic options snapshot by unique ID."""
        pass

    @abstractmethod
    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[StrategicOptionsAnalysis]:
        """List historical strategic options analyses with filtering and pagination."""
        pass

    @abstractmethod
    def count_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        """Count matching strategic options analyses for pagination."""
        pass
