"""Abstract Repository Protocol for Current Position Analyses."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.analysis import CurrentPositionAnalysis


class IAnalysisRepository(ABC):
    """Abstract persistence interface for immutable/versioned institutional position analyses."""

    @abstractmethod
    def create_analysis(self, analysis: CurrentPositionAnalysis) -> CurrentPositionAnalysis:
        """Persist a completed current-position analysis snapshot."""
        pass

    @abstractmethod
    def get_analysis_by_id(self, analysis_id: str) -> Optional[CurrentPositionAnalysis]:
        """Retrieve a specific analysis snapshot by unique ID."""
        pass

    @abstractmethod
    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[CurrentPositionAnalysis]:
        """List historical analyses with filtering and pagination."""
        pass

    @abstractmethod
    def count_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        """Count matching analyses for pagination."""
        pass
