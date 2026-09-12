"""FastAPI Dependency Injection providers."""

from fastapi import Depends
from sqlalchemy.orm import Session
from agent72.infrastructure.database.session import get_db
from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.infrastructure.repositories.sqlalchemy_plan_repository import SQLAlchemyPlanRepository
from agent72.infrastructure.repositories.sqlalchemy_organization_repository import SQLAlchemyOrganizationRepository
from agent72.infrastructure.repositories.sqlalchemy_evidence_repository import SQLAlchemyEvidenceRepository
from agent72.infrastructure.ai import get_ai_provider
from agent72.application.services.plan_service import StrategicPlanService
from agent72.application.services.health_service import HealthService
from agent72.application.services.organization_service import OrganizationService
from agent72.application.services.evidence_service import EvidenceService


def get_repository(db: Session = Depends(get_db)) -> IPlanRepository:
    """Dependency providing IPlanRepository instance."""
    return SQLAlchemyPlanRepository(session=db)


def get_organization_repository(db: Session = Depends(get_db)) -> IOrganizationRepository:
    """Dependency providing IOrganizationRepository instance."""
    return SQLAlchemyOrganizationRepository(session=db)


def get_evidence_repository(db: Session = Depends(get_db)) -> IEvidenceRepository:
    """Dependency providing IEvidenceRepository instance."""
    return SQLAlchemyEvidenceRepository(session=db)


def get_ai() -> IAIProvider:
    """Dependency providing IAIProvider instance."""
    return get_ai_provider()


def get_plan_service(
    repo: IPlanRepository = Depends(get_repository),
    ai: IAIProvider = Depends(get_ai),
) -> StrategicPlanService:
    """Dependency providing StrategicPlanService instance."""
    return StrategicPlanService(repository=repo, ai_provider=ai)


def get_health_service(
    db: Session = Depends(get_db),
    ai: IAIProvider = Depends(get_ai),
) -> HealthService:
    """Dependency providing HealthService instance."""
    return HealthService(db=db, ai_provider=ai)


from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.infrastructure.repositories.sqlalchemy_analysis_repository import SQLAlchemyAnalysisRepository
from agent72.application.services.analysis_service import CurrentPositionAnalysisService


def get_organization_service(
    repo: IOrganizationRepository = Depends(get_organization_repository),
) -> OrganizationService:
    """Dependency providing OrganizationService instance."""
    return OrganizationService(repository=repo)


def get_evidence_service(
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
) -> EvidenceService:
    """Dependency providing EvidenceService instance."""
    return EvidenceService(evidence_repository=evidence_repo, organization_repository=org_repo)


def get_analysis_repository(db: Session = Depends(get_db)) -> IAnalysisRepository:
    """Dependency providing IAnalysisRepository instance."""
    return SQLAlchemyAnalysisRepository(session=db)


def get_analysis_service(
    analysis_repo: IAnalysisRepository = Depends(get_analysis_repository),
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
    plan_repo: IPlanRepository = Depends(get_repository),
) -> CurrentPositionAnalysisService:
    """Dependency providing CurrentPositionAnalysisService instance."""
    return CurrentPositionAnalysisService(
        analysis_repository=analysis_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
        plan_repository=plan_repo,
    )


from agent72.domain.interfaces.trajectory_repository import ITrajectoryRepository
from agent72.infrastructure.repositories.sqlalchemy_trajectory_repository import SQLAlchemyTrajectoryRepository
from agent72.application.services.trajectory_service import TrajectoryAnalysisService


def get_trajectory_repository(db: Session = Depends(get_db)) -> ITrajectoryRepository:
    """Dependency providing ITrajectoryRepository instance."""
    return SQLAlchemyTrajectoryRepository(session=db)


def get_trajectory_service(
    trajectory_repo: ITrajectoryRepository = Depends(get_trajectory_repository),
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
    analysis_repo: IAnalysisRepository = Depends(get_analysis_repository),
) -> TrajectoryAnalysisService:
    """Dependency providing TrajectoryAnalysisService instance."""
    return TrajectoryAnalysisService(
        trajectory_repository=trajectory_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
        analysis_repository=analysis_repo,
    )


from agent72.domain.interfaces.strategic_intelligence_repository import IStrategicIntelligenceRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_intelligence_repository import SQLAlchemyStrategicIntelligenceRepository
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService


def get_strategic_intelligence_repository(db: Session = Depends(get_db)) -> IStrategicIntelligenceRepository:
    """Dependency providing IStrategicIntelligenceRepository instance."""
    return SQLAlchemyStrategicIntelligenceRepository(session=db)


def get_strategic_intelligence_service(
    strat_repo: IStrategicIntelligenceRepository = Depends(get_strategic_intelligence_repository),
    analysis_repo: IAnalysisRepository = Depends(get_analysis_repository),
    trajectory_repo: ITrajectoryRepository = Depends(get_trajectory_repository),
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
    ai: IAIProvider = Depends(get_ai),
) -> StrategicIntelligenceService:
    """Dependency providing StrategicIntelligenceService instance."""
    return StrategicIntelligenceService(
        strategic_intelligence_repository=strat_repo,
        analysis_repository=analysis_repo,
        trajectory_repository=trajectory_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
        ai_provider=ai,
    )


from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_options_repository import SQLAlchemyStrategicOptionsRepository
from agent72.application.services.strategic_options_service import StrategicOptionsService


def get_strategic_options_repository(db: Session = Depends(get_db)) -> IStrategicOptionsRepository:
    """Dependency providing IStrategicOptionsRepository instance."""
    return SQLAlchemyStrategicOptionsRepository(session=db)


def get_strategic_options_service(
    options_repo: IStrategicOptionsRepository = Depends(get_strategic_options_repository),
    intel_repo: IStrategicIntelligenceRepository = Depends(get_strategic_intelligence_repository),
    ai: IAIProvider = Depends(get_ai),
) -> StrategicOptionsService:
    """Dependency providing StrategicOptionsService instance."""
    return StrategicOptionsService(
        strategic_options_repository=options_repo,
        strategic_intelligence_repository=intel_repo,
        ai_provider=ai,
    )


from agent72.application.services.strategic_plan_service import StrategicPlanExecutionService


def get_strategic_plan_execution_service(
    plan_repo: IPlanRepository = Depends(get_repository),
    options_repo: IStrategicOptionsRepository = Depends(get_strategic_options_repository),
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
    ai: IAIProvider = Depends(get_ai),
) -> StrategicPlanExecutionService:
    """Dependency providing StrategicPlanExecutionService instance for Phase 8."""
    return StrategicPlanExecutionService(
        plan_repository=plan_repo,
        options_repository=options_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
        ai_provider=ai,
    )


from agent72.application.services.agent_query_service import AgentQueryService


def get_agent_query_service(
    org_repo: IOrganizationRepository = Depends(get_organization_repository),
    analysis_repo: IAnalysisRepository = Depends(get_analysis_repository),
    trajectory_repo: ITrajectoryRepository = Depends(get_trajectory_repository),
    intel_repo: IStrategicIntelligenceRepository = Depends(get_strategic_intelligence_repository),
    options_repo: IStrategicOptionsRepository = Depends(get_strategic_options_repository),
    plan_repo: IPlanRepository = Depends(get_repository),
    evidence_repo: IEvidenceRepository = Depends(get_evidence_repository),
    ai: IAIProvider = Depends(get_ai),
) -> AgentQueryService:
    """Dependency providing AgentQueryService instance for grounded query answering."""
    return AgentQueryService(
        organization_repository=org_repo,
        analysis_repository=analysis_repo,
        trajectory_repository=trajectory_repo,
        intelligence_repository=intel_repo,
        options_repository=options_repo,
        plan_repository=plan_repo,
        evidence_repository=evidence_repo,
        ai_provider=ai,
    )



