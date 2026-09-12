"""Abstract Repository Protocol for Strategic Plans."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.plan import StrategicPlan, ExecutionReview
from agent72.domain.models.strategic_plan_execution import (
    StrategicPlan as ExecutionStrategicPlan,
    ExecutionReview as Phase8ExecutionReview,
    PlanStatus as ExecutionPlanStatus,
)



class IPlanRepository(ABC):
    """Abstract interface defining persistence operations for Strategic Plans."""

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[StrategicPlan]:
        """Retrieve a strategic plan by its unique ID."""
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 50) -> List[StrategicPlan]:
        """List strategic plans with pagination."""
        pass

    @abstractmethod
    def create(self, plan: StrategicPlan) -> StrategicPlan:
        """Persist a new strategic plan."""
        pass

    @abstractmethod
    def update(self, plan: StrategicPlan) -> StrategicPlan:
        """Update an existing strategic plan."""
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> bool:
        """Delete a strategic plan by ID."""
        pass

    @abstractmethod
    def add_execution_review(self, plan_id: str, review: ExecutionReview) -> ExecutionReview:
        """Add an execution review to a strategic plan."""
        pass

    # Phase 8 Execution Framework Extensions
    def create_execution_plan(self, plan: ExecutionStrategicPlan) -> ExecutionStrategicPlan:
        """Persist a Phase 8 execution plan with objectives, targets, and initiatives."""
        raise NotImplementedError

    def get_execution_plan(self, plan_id: str) -> Optional[ExecutionStrategicPlan]:
        """Retrieve a Phase 8 execution plan by ID."""
        raise NotImplementedError

    def list_execution_plans(
        self,
        institution_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ExecutionStrategicPlan]:
        """List Phase 8 execution plans."""
        raise NotImplementedError

    def add_phase8_execution_review(
        self, plan_id: str, review: Phase8ExecutionReview
    ) -> Phase8ExecutionReview:
        """Add an automated deterministic execution review to a strategic plan."""
        raise NotImplementedError

    def update_execution_plan_status(
        self, plan_id: str, status: ExecutionPlanStatus, notes: Optional[str] = None
    ) -> Optional[ExecutionStrategicPlan]:
        """Update the lifecycle status of an execution plan."""
        raise NotImplementedError

