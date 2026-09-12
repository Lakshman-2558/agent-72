"""Abstract Repository Protocol for Institutional Trajectory Analyses."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.trajectory import TrajectoryAnalysis


class ITrajectoryRepository(ABC):
    """Abstract persistence interface for immutable/versioned institutional trajectory analyses."""

    @abstractmethod
    def create_trajectory_analysis(self, analysis: TrajectoryAnalysis) -> TrajectoryAnalysis:
        """Persist a completed trajectory analysis snapshot."""
        pass

    @abstractmethod
    def get_trajectory_analysis_by_id(self, analysis_id: str) -> Optional[TrajectoryAnalysis]:
        """Retrieve a specific trajectory analysis snapshot by unique ID."""
        pass

    @abstractmethod
    def list_trajectory_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[TrajectoryAnalysis]:
        """List historical trajectory analyses with filtering and pagination."""
        pass

    @abstractmethod
    def count_trajectory_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        """Count matching trajectory analyses for pagination."""
        pass
