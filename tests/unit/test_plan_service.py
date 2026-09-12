"""Unit tests for StrategicPlanService."""

import pytest
from unittest.mock import MagicMock
from agent72.application.services.plan_service import StrategicPlanService
from agent72.application.dtos.plan_dto import (
    StrategicPlanCreateDTO,
    StrategicPlanUpdateDTO,
    ObjectiveCreateDTO,
)
from agent72.domain.models.plan import StrategicPlan, PlanStatus
from agent72.core.exceptions import EntityNotFoundException, ValidationError


def test_create_plan_invalid_horizon_raises_validation_error():
    mock_repo = MagicMock()
    mock_ai = MagicMock()
    service = StrategicPlanService(repository=mock_repo, ai_provider=mock_ai)

    dto = StrategicPlanCreateDTO(
        title="Invalid Horizon Plan",
        institution_name="Test Institute",
        horizon_start_year=2030,
        horizon_end_year=2025,  # End earlier than start
    )

    with pytest.raises(ValidationError) as excinfo:
        service.create_plan(dto)

    assert "cannot exceed end year" in str(excinfo.value)


def test_get_plan_not_found_raises_entity_not_found():
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    mock_ai = MagicMock()
    service = StrategicPlanService(repository=mock_repo, ai_provider=mock_ai)

    with pytest.raises(EntityNotFoundException):
        service.get_plan("non-existent-id")


def test_create_plan_success():
    mock_repo = MagicMock()
    mock_ai = MagicMock()

    # Mock repository behavior
    def mock_create(plan: StrategicPlan) -> StrategicPlan:
        plan.id = "plan-123"
        return plan

    mock_repo.create.side_effect = mock_create

    service = StrategicPlanService(repository=mock_repo, ai_provider=mock_ai)

    dto = StrategicPlanCreateDTO(
        title="Five-Year Excellence Strategy",
        institution_name="National Engineering Institute",
        horizon_start_year=2026,
        horizon_end_year=2031,
        objectives=[
            ObjectiveCreateDTO(
                title="Double high-impact citations",
                target_metric="Scopus Q1 Publications",
                baseline_value=120.0,
                target_value=240.0,
                weight=2.0,
            )
        ],
    )

    result = service.create_plan(dto)
    assert result.id == "plan-123"
    assert result.title == "Five-Year Excellence Strategy"
    assert len(result.objectives) == 1
    assert result.objectives[0].target_metric == "Scopus Q1 Publications"
    mock_repo.create.assert_called_once()
