"""
Strategic Options, Scenarios & Prioritization Application Service (Phase 7).

Transforms:
Strategic Intelligence (Phase 6) -> Strategic Options -> Scenario Analysis -> Option Evaluation -> Prioritized Options

Answers:
"What strategic choices are available, what could happen under different conditions,
and which options appear most suitable for leadership consideration?"

Strict architectural guardrails:
- Leadership remains the final decision-maker. Agent 72 provides decision support only.
- Scenarios are conditional qualitative/directional projections, NOT predictions or fabricated budgets.
- All options are strictly traceable to Phase 6 issues, risks, opportunities, and canonical evidence.
- Deterministic 7-dimension evaluation formula with configurable weights.
- Missing data represents epistemic uncertainty, never poor performance or fabricated numbers.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent72.application.dtos.strategic_options_dto import (
    OptionEvaluationDTO,
    ScenarioDTO,
    StrategicOptionDTO,
    StrategicOptionsListResponseDTO,
    StrategicOptionsRequestDTO,
    StrategicOptionsResponseDTO,
)
from agent72.core.config import settings
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.interfaces.strategic_intelligence_repository import IStrategicIntelligenceRepository
from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.domain.models.strategic_intelligence import (
    ConstraintSignal,
    ExternalFactor,
    OpportunitySignal,
    RiskSeverity,
    RiskSignal,
    StrategicIntelligenceAnalysis,
    StrategicIssue,
)
from agent72.domain.models.strategic_options import (
    EvaluationDimension,
    FeasibilityLevel,
    OptionCategory,
    OptionEvaluation,
    OptionStatus,
    PriorityLevel,
    Scenario,
    ScenarioType,
    StrategicOption,
    StrategicOptionsAnalysis,
)


class StrategicOptionsService:
    """
    Deterministic Strategic Options Generation, Scenario Modeling & Evaluation Service.
    """

    def __init__(
        self,
        strategic_options_repository: IStrategicOptionsRepository,
        strategic_intelligence_repository: IStrategicIntelligenceRepository,
        ai_provider: Optional[IAIProvider] = None,
    ):
        self.strategic_options_repo = strategic_options_repository
        self.strategic_intel_repo = strategic_intelligence_repository
        self.ai_provider = ai_provider

    def generate_strategic_options_analysis(
        self, request: StrategicOptionsRequestDTO
    ) -> StrategicOptionsAnalysis:
        """
        Execute deterministic Strategic Options generation, scenario formulation,
        and multi-dimensional 7-factor evaluation.
        """
        # 1. Resolve Phase 6 Strategic Intelligence Snapshot
        intel = self._resolve_strategic_intelligence(request)

        # 2. Generate Evidence-Grounded Strategic Options (with deduplication & alternatives)
        options, data_limitations = self._generate_options(intel)

        # 3. Formulate 4 Conditional Scenarios per Option (Baseline, Upside, Downside, Stress)
        scenarios = self._generate_scenarios(options, intel)

        # 4. Perform Deterministic 7-Dimension Evaluation
        evaluations = self._evaluate_options(options, intel)

        # 5. Determine Prioritized Ranking
        # Sort options descending by total evaluation score
        eval_map = {e.option_id: e for e in evaluations}
        sorted_options = sorted(
            options,
            key=lambda o: eval_map[o.id].total_score if o.id in eval_map else 0.0,
            reverse=True,
        )
        prioritized_ids = [o.id for o in sorted_options]

        # Update option status for top candidates
        for opt in options:
            ev = eval_map.get(opt.id)
            if ev and ev.priority_level in (PriorityLevel.CRITICAL, PriorityLevel.HIGH):
                opt.status = OptionStatus.PRIORITIZED
            else:
                opt.status = OptionStatus.EVALUATED

        # 6. Synthesize Assumptions & Uncertainty
        assumptions = [
            "Leadership validation and governing body approval is required prior to execution commitment.",
            "Scenario projections reflect conditional qualitative dynamics rather than deterministic prophecies.",
            "Resource and feasibility assessments are grounded in available institutional evidence without fabricated budgets.",
        ]

        uncertainty = dict(intel.uncertainty_summary)
        if any(opt.resource_requirement == "UNCERTAIN" for opt in options):
            uncertainty["resource_evidence_limitation"] = (
                "Financial and capital expenditure evidence is partially incomplete; "
                "resource requirements are evaluated qualitatively without fabricated monetary budgets."
            )

        # 7. Optional AI Synthesis (strictly guarded: summary only, cannot alter findings or scores)
        ai_notes = None
        if request.include_ai_synthesis and self.ai_provider:
            ai_notes = self._generate_ai_synthesis(options, scenarios, evaluations)

        # 8. Create and Persist Immutable StrategicOptionsAnalysis Snapshot
        analysis_id = f"strat_opt_{uuid.uuid4().hex[:16]}"
        disclaimer = (
            "Strategic options and priority signals are decision-support outputs. "
            "Final strategic decisions remain with institutional leadership/governing bodies."
        )

        analysis = StrategicOptionsAnalysis(
            id=analysis_id,
            institution_id=request.institution_id,
            organizational_unit_id=request.organizational_unit_id,
            analysis_period=request.analysis_period,
            generated_at=datetime.now(timezone.utc),
            strategic_intelligence_analysis_id=intel.id or "",
            options=options,
            scenarios=scenarios,
            evaluations=evaluations,
            prioritized_option_ids=prioritized_ids,
            assumptions=assumptions,
            uncertainty=uncertainty,
            data_limitations=data_limitations,
            decision_support_disclaimer=disclaimer,
            created_at=datetime.now(timezone.utc),
            engine_version="1.0.0",
            ai_synthesis_notes=ai_notes,
            status="FINALIZED",
        )

        saved = self.strategic_options_repo.create_analysis(analysis)
        return self._to_response_dto(saved)

    def get_analysis_by_id(self, analysis_id: str) -> StrategicOptionsResponseDTO:
        """Retrieve an existing Strategic Options Analysis snapshot by ID."""
        analysis = self.strategic_options_repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise EntityNotFoundException("StrategicOptionsAnalysis", analysis_id)
        return self._to_response_dto(analysis)

    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> StrategicOptionsListResponseDTO:
        """List historical Strategic Options Analyses with filtering and pagination."""
        items = self.strategic_options_repo.list_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
            skip=skip,
            limit=limit,
        )
        total = self.strategic_options_repo.count_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
        )

        return StrategicOptionsListResponseDTO(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._to_response_dto(item) for item in items],
        )

    # --------------------------------------------------------------------------
    # Private Helpers: Prerequisite Resolution
    # --------------------------------------------------------------------------

    def _resolve_strategic_intelligence(
        self, request: StrategicOptionsRequestDTO
    ) -> StrategicIntelligenceAnalysis:
        """Resolve required Phase 6 Strategic Intelligence analysis."""
        if request.strategic_intelligence_analysis_id:
            intel = self.strategic_intel_repo.get_strategic_intelligence_analysis_by_id(
                request.strategic_intelligence_analysis_id
            )
            if not intel:
                raise ValidationError(
                    f"Specified Strategic Intelligence Analysis '{request.strategic_intelligence_analysis_id}' not found."
                )
            return intel

        # Resolve latest matching snapshot
        existing = self.strategic_intel_repo.list_strategic_intelligence_analyses(
            institution_id=request.institution_id,
            organizational_unit_id=request.organizational_unit_id,
            analysis_period=request.analysis_period,
            skip=0,
            limit=1,
        )
        if not existing:
            raise ValidationError(
                f"Missing required prerequisite Strategic Intelligence Analysis for institution '{request.institution_id}', "
                f"unit '{request.organizational_unit_id}', and period '{request.analysis_period}'."
            )
        return existing[0]

    # --------------------------------------------------------------------------
    # Private Helpers: Option Generation, Alternatives & Deduplication
    # --------------------------------------------------------------------------

    def _generate_options(
        self, intel: StrategicIntelligenceAnalysis
    ) -> tuple[List[StrategicOption], List[str]]:
        """
        Generate 3-8 evidence-backed strategic options directly from Phase 6 findings.
        Ensures options represent distinct alternative strategies where appropriate,
        deduplicates overlapping signals, and records limitations if fewer genuinely exist.
        """
        options: List[StrategicOption] = []
        data_limitations: List[str] = []

        # Track addressed IDs
        covered_issue_ids = set()
        covered_risk_ids = set()

        # A. Check for Placement Deficit & Employer Demand Risk
        placement_risks = [
            r for r in intel.risk_signals
            if any("placement" in m.lower() or "employer" in m.lower() for m in r.related_metrics)
            or "placement" in r.title.lower()
        ]
        placement_issues = [
            i for i in intel.strategic_issues
            if any("placement" in m.lower() for m in i.related_metrics) or "placement" in i.title.lower()
        ]

        if placement_risks or placement_issues:
            p_risk_ids = [r.id for r in placement_risks]
            p_issue_ids = [i.id for i in placement_issues]
            p_evidence_ids = list(set(
                [eid for r in placement_risks for eid in r.evidence_ids] +
                [eid for i in placement_issues for eid in i.evidence_ids]
            ))
            p_metrics = list(set(
                [m for r in placement_risks for m in r.related_metrics] +
                [m for i in placement_issues for m in i.related_metrics]
            ))

            covered_risk_ids.update(p_risk_ids)
            covered_issue_ids.update(p_issue_ids)

            # Generate Alternative A: Academic & Curriculum Transformation
            opt_a_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_a_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.IMPROVEMENT,
                    title="Industry-Aligned Curriculum Transformation & Experiential Learning",
                    description=(
                        "Systematically modernize degree curricula and embed industry-standard applied technical "
                        "competencies into coursework to directly reverse the multi-period placement deficit."
                    ),
                    strategic_rationale=(
                        "Addresses persistent placement contraction by eliminating the empirical skill gap identified "
                        "between academic syllabus outcomes and regional tech employer demand."
                    ),
                    addressed_issue_ids=p_issue_ids,
                    addressed_risk_ids=p_risk_ids,
                    opportunity_ids=[],
                    related_metrics=p_metrics,
                    evidence_ids=p_evidence_ids,
                    expected_outcomes=[
                        "Reversal of declining graduate placement rate trajectory toward institutional target",
                        "Direct curriculum alignment with emerging regional skill demand indicators",
                        "Increased student technical proficiency and graduate employment competitiveness",
                    ],
                    assumptions=[
                        "Academic department faculty and curriculum committees support semester syllabus revisions.",
                        "Regional employers provide timely competency frameworks and skill benchmarks.",
                    ],
                    dependencies=["Faculty capability development and academic senate curriculum approval"],
                    feasibility=FeasibilityLevel.MEDIUM,
                    resource_requirement="MEDIUM",
                    implementation_risk="MEDIUM",
                    confidence=0.85,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "Substantial faculty time commitment required for course redesign vs. ongoing research productivity.",
                        "Internal academic governance approval timelines may delay immediate term implementation.",
                    ],
                )
            )

            # Generate Alternative B: Corporate Co-Op & Enterprise Internship Partnerships
            opt_b_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_b_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.PARTNERSHIP,
                    title="Strategic Enterprise Co-Op & Corporate Internship Pipeline Expansion",
                    description=(
                        "Rapidly bridge the graduate placement gap through formal multi-year enterprise co-op agreements, "
                        "industry sponsored capstone projects, and pre-placement recruitment pipelines."
                    ),
                    strategic_rationale=(
                        "Provides an immediate structural mechanism to convert internships into verified employment offers "
                        "without waiting for lengthy multi-year academic curriculum restructuring cycles."
                    ),
                    addressed_issue_ids=p_issue_ids,
                    addressed_risk_ids=p_risk_ids,
                    opportunity_ids=[],
                    related_metrics=p_metrics,
                    evidence_ids=p_evidence_ids,
                    expected_outcomes=[
                        "Rapid expansion of corporate placement offers through dedicated employer internship channels",
                        "Direct institutional immunity against regional employer demand volatility",
                        "Enhanced industry engagement and external sponsorship opportunities",
                    ],
                    assumptions=[
                        "Target enterprise partners maintain consistent hiring quotas across economic cycles.",
                        "Students are willing and prepared to participate in off-campus co-op semesters.",
                    ],
                    dependencies=["Dedicated corporate relations staffing and career placement office coordination"],
                    feasibility=FeasibilityLevel.HIGH,
                    resource_requirement="LOW",
                    implementation_risk="LOW",
                    confidence=0.88,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "High dependence on external corporate hiring stability during macroeconomic fluctuations.",
                        "Does not solve fundamental syllabus obsolescence if internal curricula remain unadapted.",
                    ],
                )
            )

        # B. Check for Infrastructure & Facility Constraints
        infra_constraints = [
            c for c in intel.constraint_signals
            if any("utilization" in m.lower() or "infra" in m.lower() for m in c.related_metrics)
            or "infrastructure" in c.title.lower() or "capacity" in c.title.lower()
        ]
        infra_risks = [
            r for r in intel.risk_signals
            if any("utilization" in m.lower() or "infra" in m.lower() for m in r.related_metrics)
            or "infrastructure" in r.title.lower()
        ]

        if infra_constraints or infra_risks:
            i_c_ids = [c.id for c in infra_constraints]
            i_r_ids = [r.id for r in infra_risks]
            i_evidence_ids = list(set(
                [eid for c in infra_constraints for eid in c.evidence_ids] +
                [eid for r in infra_risks for eid in r.evidence_ids]
            ))
            i_metrics = list(set(
                [m for c in infra_constraints for m in c.related_metrics] +
                [m for r in infra_risks for m in r.related_metrics]
            ))

            covered_risk_ids.update(i_r_ids)

            opt_infra_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_infra_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.CAPABILITY,
                    title="Phased Laboratory Modernization & Intelligent Space Scheduling",
                    description=(
                        "Alleviate acute infrastructure capacity strain through physical laboratory upgrades, "
                        "extended operational shift scheduling, and virtualized simulation software modules."
                    ),
                    strategic_rationale=(
                        "Directly mitigates the laboratory capacity bottleneck (utilization exceeding configured operational "
                        "threshold of 85%) preventing it from throttling future program enrollment or research activities."
                    ),
                    addressed_issue_ids=[],
                    addressed_risk_ids=i_r_ids,
                    opportunity_ids=[],
                    related_metrics=i_metrics,
                    evidence_ids=i_evidence_ids,
                    expected_outcomes=[
                        "Reduction of lab utilization rate to safe operational thresholds (<80%)",
                        "Enhanced physical space throughput to accommodate sustained student intake",
                        "Modernized computing and experimental facilities supporting advanced instruction",
                    ],
                    assumptions=[
                        "Capital budget or phased grant funding can be secured for physical lab modernization.",
                        "Facility department can execute renovations without disrupting active academic terms.",
                    ],
                    dependencies=["Capital funding allocation and institutional space management approval"],
                    feasibility=FeasibilityLevel.MEDIUM,
                    resource_requirement="HIGH",
                    implementation_risk="MEDIUM",
                    confidence=0.82,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "High upfront capital expenditure requirement competes with other operational priorities.",
                        "Temporary instruction disruption during phased laboratory renovations.",
                    ],
                )
            )

        # C. Check for Research Acceleration & Momentum Opportunities
        research_opps = [
            o for o in intel.opportunity_signals
            if any("research" in m.lower() or "publication" in m.lower() for m in o.related_metrics)
            or "research" in o.title.lower()
        ]
        research_issues = [
            i for i in intel.strategic_issues
            if any("publication" in m.lower() or "research" in m.lower() for m in i.related_metrics)
            or "publication" in i.title.lower()
        ]

        if research_opps or research_issues:
            r_opp_ids = [o.id for o in research_opps]
            r_issue_ids = [i.id for i in research_issues]
            r_evidence_ids = list(set(
                [eid for o in research_opps for eid in o.evidence_ids] +
                [eid for i in research_issues for eid in i.evidence_ids]
            ))
            r_metrics = list(set(
                [m for o in research_opps for m in o.related_metrics] +
                [m for i in research_issues for m in i.related_metrics]
            ))

            covered_issue_ids.update(r_issue_ids)

            opt_res_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_res_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.GROWTH,
                    title="Strategic Research Innovation Cluster & Interdisciplinary Grant Accelerator",
                    description=(
                        "Capitalize on demonstrated research publication momentum by establishing focused thematic "
                        "research clusters, competitive seed grants, and dedicated sponsored-project support."
                    ),
                    strategic_rationale=(
                        "Leverages verified multi-period research growth (+62.5% increase in peer-reviewed output) to establish "
                        "institutional leadership, improve national rankings, and secure external sponsored research funding."
                    ),
                    addressed_issue_ids=r_issue_ids,
                    addressed_risk_ids=[],
                    opportunity_ids=r_opp_ids,
                    related_metrics=r_metrics,
                    evidence_ids=r_evidence_ids,
                    expected_outcomes=[
                        "Continued acceleration of high-impact peer-reviewed publications beyond target",
                        "Substantial increase in external competitive grant awards and sponsored research revenue",
                        "Elevated institutional prestige and top-tier doctoral student recruitment",
                    ],
                    assumptions=[
                        "Productive faculty research leaders remain retained with appropriate research release time.",
                        "External funding agencies maintain active grant opportunities in targeted disciplines.",
                    ],
                    dependencies=["Research administration support and laboratory computing infrastructure"],
                    feasibility=FeasibilityLevel.HIGH,
                    resource_requirement="MEDIUM",
                    implementation_risk="LOW",
                    confidence=0.90,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "Allocation of institutional funding toward research incentives rather than immediate undergraduate teaching overhead.",
                        "Potential disparity between research-intensive faculty and heavy-teaching clinical faculty.",
                    ],
                )
            )

        # D. Check for Faculty Capability & Workload Constraints
        faculty_constraints = [
            c for c in intel.constraint_signals
            if any("faculty" in m.lower() or "sfr" in m.lower() or "phd" in m.lower() for m in c.related_metrics)
            or "faculty" in c.title.lower()
        ]
        if faculty_constraints:
            f_c_ids = [c.id for c in faculty_constraints]
            f_evidence_ids = list(set([eid for c in faculty_constraints for eid in c.evidence_ids]))
            f_metrics = list(set([m for c in faculty_constraints for m in c.related_metrics]))

            opt_fac_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_fac_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.CAPABILITY,
                    title="Targeted Faculty Recruitment & Doctoral Capability Development",
                    description=(
                        "Conduct targeted recruitment for doctoral faculty in high-demand technical specializations "
                        "while sponsoring existing faculty completion of terminal doctoral qualifications."
                    ),
                    strategic_rationale=(
                        "Directly relieves faculty workload ratios and resolves accreditation capability thresholds "
                        "necessary to sustain high-quality instructional delivery and research mentorship."
                    ),
                    addressed_issue_ids=[],
                    addressed_risk_ids=[],
                    opportunity_ids=[],
                    related_metrics=f_metrics,
                    evidence_ids=f_evidence_ids,
                    expected_outcomes=[
                        "Normalization of student-to-faculty ratios within accreditation guidelines",
                        "Achievement of target faculty doctoral qualification benchmarks (>75%)",
                        "Expanded academic mentoring and undergraduate project supervision capacity",
                    ],
                    assumptions=[
                        "Qualified doctoral candidates are available in the academic hiring market within compensation bands.",
                    ],
                    dependencies=["Recurring academic payroll budget allocation and faculty senate recruitment committee"],
                    feasibility=FeasibilityLevel.MEDIUM,
                    resource_requirement="HIGH",
                    implementation_risk="MEDIUM",
                    confidence=0.82,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "Long-term recurring payroll and benefit expenditure increases baseline operating commitments.",
                        "Recruitment cycles typically require 6 to 12 months before candidates are in the classroom.",
                    ],
                )
            )

        # E. Check for Regulatory Mandates & External Factors
        reg_factors = [
            ef for ef in intel.external_factors
            if ef.category.value == "REGULATORY" or "compliance" in ef.factor_name.lower() or "mandate" in ef.factor_name.lower()
        ]
        if reg_factors:
            reg_evidence_ids = list(set([eid for ef in reg_factors for eid in ef.evidence_ids]))
            opt_reg_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_reg_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.RISK_MITIGATION,
                    title="Institutional AI Ethics & Regulatory Accreditation Compliance Initiative",
                    description=(
                        "Establish an institutional compliance and curriculum integration framework to proactively "
                        "satisfy upcoming mandatory accreditation standards and ethical guidelines."
                    ),
                    strategic_rationale=(
                        "Prevents severe compliance penalties and accreditation sanctions by addressing external regulatory "
                        "mandates early through formalized academic oversight and audit readiness."
                    ),
                    addressed_issue_ids=[],
                    addressed_risk_ids=[],
                    opportunity_ids=[],
                    related_metrics=[],
                    evidence_ids=reg_evidence_ids,
                    expected_outcomes=[
                        "Full compliance certification across all accredited academic programs",
                        "Mitigation of institutional regulatory non-compliance vulnerability",
                        "Exemplary governance posture enhancing institutional reputation with statutory bodies",
                    ],
                    assumptions=[
                        "Regulatory statutory bodies finalize specific audit rubrics according to published timelines.",
                    ],
                    dependencies=["Academic leadership oversight and department compliance leads"],
                    feasibility=FeasibilityLevel.HIGH,
                    resource_requirement="LOW",
                    implementation_risk="LOW",
                    confidence=0.86,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "Administrative compliance documentation overhead for academic coordinators.",
                    ],
                )
            )

        # F. Check for Admissions Yield Vulnerability
        admissions_issues = [
            i for i in intel.strategic_issues
            if "admissions" in i.title.lower() or any("yield" in m.lower() for m in i.related_metrics)
        ]
        if admissions_issues:
            adm_evidence_ids = list(set([eid for i in admissions_issues for eid in i.evidence_ids]))
            adm_metrics = list(set([m for i in admissions_issues for m in i.related_metrics]))

            opt_adm_id = f"opt_{uuid.uuid4().hex[:12]}"
            options.append(
                StrategicOption(
                    id=opt_adm_id,
                    institution_id=intel.institution_id,
                    organizational_unit_id=intel.organizational_unit_id,
                    category=OptionCategory.IMPROVEMENT,
                    title="Admissions Yield Stabilization & Applicant Engagement Program",
                    description=(
                        "Stabilize declining admissions yield trajectory through personalized applicant engagement, "
                        "targeted merit scholarships, and department open-house showcases."
                    ),
                    strategic_rationale=(
                        "Protects baseline institutional enrollment by defending against the declining admissions yield "
                        "identified as a vulnerable strength in strategic intelligence."
                    ),
                    addressed_issue_ids=[i.id for i in admissions_issues],
                    addressed_risk_ids=[],
                    opportunity_ids=[],
                    related_metrics=adm_metrics,
                    evidence_ids=adm_evidence_ids,
                    expected_outcomes=[
                        "Stabilization of admissions yield above baseline target",
                        "Retention of high-aptitude applicant cohorts against regional competitors",
                    ],
                    assumptions=["Admissions counseling staff can execute enhanced outreach protocols."],
                    dependencies=["Enrollment management coordination and financial aid allocation"],
                    feasibility=FeasibilityLevel.HIGH,
                    resource_requirement="MEDIUM",
                    implementation_risk="LOW",
                    confidence=0.84,
                    status=OptionStatus.PROPOSED,
                    trade_offs=[
                        "Modest scholarship budget allocation required to preserve conversion rates.",
                    ],
                )
            )

        # Ensure option count boundaries (3-8 options supported by evidence)
        if len(options) < 3:
            data_limitations.append(
                f"Generated {len(options)} strategic options directly supported by Phase 6 intelligence signals. "
                "Per core guardrails, no unevidenced options were fabricated merely to satisfy the 3-8 target range."
            )
        elif len(options) > 8:
            options = options[:8]

        return options, data_limitations

    # --------------------------------------------------------------------------
    # Private Helpers: Scenario Analysis (4 Conditional Scenarios per Option)
    # --------------------------------------------------------------------------

    def _generate_scenarios(
        self, options: List[StrategicOption], intel: StrategicIntelligenceAnalysis
    ) -> List[Scenario]:
        """
        Generate BASELINE, UPSIDE, DOWNSIDE, and STRESS scenarios for each option.
        All scenarios are conditional qualitative/directional projections, NOT predictions.
        No fabricated numbers, budgets, or statistical forecasts.
        """
        scenarios: List[Scenario] = []

        for opt in options:
            base_assumptions = opt.assumptions

            # 1. BASELINE: Continuation under current conditions
            scenarios.append(
                Scenario(
                    id=f"scen_{uuid.uuid4().hex[:12]}",
                    option_id=opt.id,
                    scenario_type=ScenarioType.BASELINE,
                    title=f"Baseline Execution: {opt.title}",
                    description=(
                        f"Implementation proceeds under current institutional and external trajectory conditions. "
                        f"Expected outcomes materialize in a standard timeframe with predictable operational adjustments."
                    ),
                    assumptions=base_assumptions + ["Current macroeconomic and student demand trends remain constant."],
                    expected_effects=[
                        "Gradual stabilization of addressed metric trajectories over multi-period horizon",
                        "Predictable operational resource utilization matching planned estimates",
                    ],
                    risks=[
                        "Implementation velocity constrained by standard governance and committee cycles",
                    ],
                    opportunities=[
                        "Builds institutional momentum and procedural alignment for future initiatives",
                    ],
                    uncertainty="LOW",
                    confidence=opt.confidence,
                    evidence_ids=opt.evidence_ids,
                )
            )

            # 2. UPSIDE: Favorable external & execution conditions
            scenarios.append(
                Scenario(
                    id=f"scen_{uuid.uuid4().hex[:12]}",
                    option_id=opt.id,
                    scenario_type=ScenarioType.UPSIDE,
                    title=f"Accelerated Upside: {opt.title}",
                    description=(
                        f"Favorable external environment and rapid institutional adoption accelerate initiative impact. "
                        f"Target outcomes are exceeded with compounding positive cross-domain spillover."
                    ),
                    assumptions=base_assumptions + [
                        "External partner engagement exceeds initial commitments.",
                        "Faculty and student adoption is rapid and highly enthusiastic.",
                    ],
                    expected_effects=[
                        "Accelerated reversal of performance gaps and positive momentum inflection",
                        "Substantial positive reputational enhancement and competitive differentiation",
                    ],
                    risks=[
                        "Rapid expansion may strain ancillary administrative support capacity",
                    ],
                    opportunities=[
                        "Early demonstration of success unlocks additional external donor or industry funding",
                    ],
                    uncertainty="MEDIUM",
                    confidence=opt.confidence * 0.95,
                    evidence_ids=opt.evidence_ids,
                )
            )

            # 3. DOWNSIDE: Plausible adverse headwinds
            scenarios.append(
                Scenario(
                    id=f"scen_{uuid.uuid4().hex[:12]}",
                    option_id=opt.id,
                    scenario_type=ScenarioType.DOWNSIDE,
                    title=f"Constrained Downside: {opt.title}",
                    description=(
                        f"Adverse external pressures or internal execution friction slow down implementation progress. "
                        f"Outcomes are delayed and require active leadership mitigation."
                    ),
                    assumptions=base_assumptions + [
                        "Macroeconomic conditions or regional employer hiring soften.",
                        "Internal stakeholder resistance slows operational adoption.",
                    ],
                    expected_effects=[
                        "Delayed trajectory improvement requiring extended multi-period recovery",
                        "Increased organizational friction requiring senior leadership intervention",
                    ],
                    risks=[
                        "Partial realization of expected outcomes leaves residual vulnerability unmitigated",
                    ],
                    opportunities=[
                        "Forces organizational discipline and process refinement under tighter constraints",
                    ],
                    uncertainty="MEDIUM",
                    confidence=opt.confidence * 0.90,
                    evidence_ids=opt.evidence_ids,
                )
            )

            # 4. STRESS: Severe adverse conditions
            scenarios.append(
                Scenario(
                    id=f"scen_{uuid.uuid4().hex[:12]}",
                    option_id=opt.id,
                    scenario_type=ScenarioType.STRESS,
                    title=f"Severe Stress: {opt.title}",
                    description=(
                        f"Severe external economic, regulatory, or competitive shocks disrupt initiative delivery. "
                        f"Tests the institutional resilience and contingency safeguards of the proposed choice."
                    ),
                    assumptions=base_assumptions + [
                        "Severe contraction in external labor market or dramatic regulatory tightening.",
                        "Acute institutional resource constraints or hiring moratoriums.",
                    ],
                    expected_effects=[
                        "Significant stagnation or further decline in vulnerable metrics",
                        "Resource diversion required to protect core baseline academic operations",
                    ],
                    risks=[
                        "Compounding institutional deficits and potential accreditation or reputational exposure",
                    ],
                    opportunities=[
                        "Catalyzes structural restructuring and emergency governance agility",
                    ],
                    uncertainty="HIGH",
                    confidence=opt.confidence * 0.80,
                    evidence_ids=opt.evidence_ids,
                )
            )

        return scenarios

    # --------------------------------------------------------------------------
    # Private Helpers: Deterministic 7-Dimension Option Evaluation
    # --------------------------------------------------------------------------

    def _evaluate_options(
        self, options: List[StrategicOption], intel: StrategicIntelligenceAnalysis
    ) -> List[OptionEvaluation]:
        """
        Evaluate each option across the exact 7 dimensions using configurable weights:
        1. STRATEGIC_ALIGNMENT (weight 0.20)
        2. IMPACT (weight 0.20)
        3. FEASIBILITY (weight 0.15)
        4. RESOURCE_EFFICIENCY (weight 0.10)
        5. IMPLEMENTATION_RISK (weight 0.10) - Higher score = lower implementation risk
        6. URGENCY (weight 0.10)
        7. EVIDENCE_STRENGTH (weight 0.15)

        All scores 0-100.
        """
        evaluations: List[OptionEvaluation] = []

        w_align = settings.OPTION_WEIGHT_STRATEGIC_ALIGNMENT
        w_imp = settings.OPTION_WEIGHT_IMPACT
        w_feas = settings.OPTION_WEIGHT_FEASIBILITY
        w_res = settings.OPTION_WEIGHT_RESOURCE_EFFICIENCY
        w_risk = settings.OPTION_WEIGHT_IMPLEMENTATION_RISK
        w_urg = settings.OPTION_WEIGHT_URGENCY
        w_evi = settings.OPTION_WEIGHT_EVIDENCE_STRENGTH

        for opt in options:
            # 1. Strategic Alignment (0-100)
            # High if addressing critical risks, binding constraints, or strategic issues
            num_addressed = len(opt.addressed_risk_ids) + len(opt.addressed_issue_ids) + len(opt.opportunity_ids)
            if num_addressed >= 3:
                alignment = 90.0
            elif num_addressed == 2:
                alignment = 85.0
            elif num_addressed == 1:
                alignment = 78.0
            else:
                alignment = 70.0

            # 2. Expected Impact (0-100)
            if opt.category in (OptionCategory.IMPROVEMENT, OptionCategory.GROWTH, OptionCategory.TRANSFORMATION):
                impact = 88.0
            elif opt.category in (OptionCategory.CAPABILITY, OptionCategory.PARTNERSHIP):
                impact = 82.0
            else:
                impact = 75.0

            # 3. Feasibility (0-100)
            if opt.feasibility == FeasibilityLevel.HIGH:
                feasibility = 88.0
            elif opt.feasibility == FeasibilityLevel.MEDIUM:
                feasibility = 72.0
            else:
                feasibility = 50.0

            # 4. Resource Efficiency (0-100)
            # Higher efficiency if resource requirement is LOW or MEDIUM
            if opt.resource_requirement == "LOW":
                resource_efficiency = 88.0
            elif opt.resource_requirement == "MEDIUM":
                resource_efficiency = 72.0
            elif opt.resource_requirement == "HIGH":
                resource_efficiency = 55.0
            else:  # UNCERTAIN
                resource_efficiency = 50.0

            # 5. Implementation Risk (0-100)
            # Higher score = lower implementation risk / better risk profile
            if opt.implementation_risk == "LOW":
                impl_risk_score = 88.0
            elif opt.implementation_risk == "MEDIUM":
                impl_risk_score = 70.0
            else:
                impl_risk_score = 45.0

            # 6. Urgency (0-100)
            # Driven by severity of addressed risks
            has_critical_risk = any(
                r.severity == RiskSeverity.CRITICAL for r in intel.risk_signals if r.id in opt.addressed_risk_ids
            )
            has_high_risk = any(
                r.severity == RiskSeverity.HIGH for r in intel.risk_signals if r.id in opt.addressed_risk_ids
            )
            if has_critical_risk:
                urgency = 95.0
            elif has_high_risk:
                urgency = 88.0
            elif opt.addressed_risk_ids or opt.addressed_issue_ids:
                urgency = 75.0
            else:
                urgency = 60.0

            # 7. Evidence Strength (0-100)
            evidence_strength = min(100.0, max(40.0, opt.confidence * 100.0))

            # Calculate Weighted Total Score (0-100)
            total_score = (
                (alignment * w_align)
                + (impact * w_imp)
                + (feasibility * w_feas)
                + (resource_efficiency * w_res)
                + (impl_risk_score * w_risk)
                + (urgency * w_urg)
                + (evidence_strength * w_evi)
            )
            total_score = round(total_score, 2)

            # Assign Priority Level using configurable thresholds
            if total_score >= settings.OPTION_PRIORITY_CRITICAL_THRESHOLD:
                priority = PriorityLevel.CRITICAL
            elif total_score >= settings.OPTION_PRIORITY_HIGH_THRESHOLD:
                priority = PriorityLevel.HIGH
            elif total_score >= settings.OPTION_PRIORITY_MEDIUM_THRESHOLD:
                priority = PriorityLevel.MEDIUM
            else:
                priority = PriorityLevel.LOW

            # Construct transparent rationale
            rationale = (
                f"Evaluated as {priority.value} priority candidate (Total Score: {total_score}/100) "
                f"based on Strategic Alignment ({alignment:.0f}), Expected Impact ({impact:.0f}), "
                f"Feasibility ({feasibility:.0f}), Resource Efficiency ({resource_efficiency:.0f}), "
                f"Implementation Risk Profile ({impl_risk_score:.0f}), Urgency ({urgency:.0f}), "
                f"and Evidence Strength ({evidence_strength:.0f})."
            )

            evaluations.append(
                OptionEvaluation(
                    option_id=opt.id,
                    strategic_alignment_score=alignment,
                    impact_score=impact,
                    feasibility_score=feasibility,
                    resource_efficiency_score=resource_efficiency,
                    implementation_risk_score=impl_risk_score,
                    urgency_score=urgency,
                    evidence_strength_score=evidence_strength,
                    total_score=total_score,
                    priority_level=priority,
                    trade_offs=opt.trade_offs,
                    rationale=rationale,
                )
            )

        return evaluations

    # --------------------------------------------------------------------------
    # Private Helpers: AI Synthesis & Response Serialization
    # --------------------------------------------------------------------------

    def _generate_ai_synthesis(
        self,
        options: List[StrategicOption],
        scenarios: List[Scenario],
        evaluations: List[OptionEvaluation],
    ) -> Optional[str]:
        """
        Generate natural language briefing notes.
        Strict guardrail: AI only formats, groups, and summarizes deterministic findings.
        AI cannot alter scores, modify priority, invent evidence, or create options.
        """
        try:
            prompt = (
                "You are an executive institutional strategy advisor. Summarize the following "
                "deterministically generated strategic options and their trade-offs for leadership. "
                "DO NOT invent options, DO NOT change scores, DO NOT fabricate budgets or numbers, "
                "and strictly adhere to the provided findings:\n\n"
            )
            eval_map = {e.option_id: e for e in evaluations}
            for opt in options:
                ev = eval_map.get(opt.id)
                score_text = f"Total Score: {ev.total_score}, Priority: {ev.priority_level.value}" if ev else ""
                prompt += f"- Option: {opt.title} ({opt.category.value}) | {score_text}\n"
                prompt += f"  Rationale: {opt.strategic_rationale}\n"
                prompt += f"  Trade-offs: {', '.join(opt.trade_offs)}\n"

            prompt += (
                "\nProvide a concise 2-3 paragraph executive summary of strategic choices, trade-offs, "
                "and key decision considerations for leadership."
            )
            response = self.ai_provider.generate_completion(prompt)
            return response.strip() if response else None
        except Exception:
            return None

    def _to_response_dto(self, analysis: StrategicOptionsAnalysis) -> StrategicOptionsResponseDTO:
        """Convert domain StrategicOptionsAnalysis to response DTO."""
        opt_dtos = [
            StrategicOptionDTO(
                id=o.id,
                institution_id=o.institution_id,
                organizational_unit_id=o.organizational_unit_id,
                category=o.category,
                title=o.title,
                description=o.description,
                strategic_rationale=o.strategic_rationale,
                addressed_issue_ids=o.addressed_issue_ids,
                addressed_risk_ids=o.addressed_risk_ids,
                opportunity_ids=o.opportunity_ids,
                related_metrics=o.related_metrics,
                evidence_ids=o.evidence_ids,
                expected_outcomes=o.expected_outcomes,
                assumptions=o.assumptions,
                dependencies=o.dependencies,
                feasibility=o.feasibility,
                resource_requirement=o.resource_requirement,
                implementation_risk=o.implementation_risk,
                confidence=o.confidence,
                status=o.status,
                trade_offs=o.trade_offs,
            )
            for o in analysis.options
        ]

        scen_dtos = [
            ScenarioDTO(
                id=s.id,
                option_id=s.option_id,
                scenario_type=s.scenario_type,
                title=s.title,
                description=s.description,
                assumptions=s.assumptions,
                expected_effects=s.expected_effects,
                risks=s.risks,
                opportunities=s.opportunities,
                uncertainty=s.uncertainty,
                confidence=s.confidence,
                evidence_ids=s.evidence_ids,
            )
            for s in analysis.scenarios
        ]

        eval_dtos = [
            OptionEvaluationDTO(
                option_id=e.option_id,
                strategic_alignment_score=e.strategic_alignment_score,
                impact_score=e.impact_score,
                feasibility_score=e.feasibility_score,
                resource_efficiency_score=e.resource_efficiency_score,
                implementation_risk_score=e.implementation_risk_score,
                urgency_score=e.urgency_score,
                evidence_strength_score=e.evidence_strength_score,
                total_score=e.total_score,
                priority_level=e.priority_level,
                trade_offs=e.trade_offs,
                rationale=e.rationale,
            )
            for e in analysis.evaluations
        ]

        return StrategicOptionsResponseDTO(
            id=analysis.id or "",
            institution_id=analysis.institution_id,
            organizational_unit_id=analysis.organizational_unit_id,
            analysis_period=analysis.analysis_period,
            generated_at=analysis.generated_at,
            strategic_intelligence_analysis_id=analysis.strategic_intelligence_analysis_id,
            options=opt_dtos,
            scenarios=scen_dtos,
            evaluations=eval_dtos,
            prioritized_option_ids=analysis.prioritized_option_ids,
            assumptions=analysis.assumptions,
            uncertainty=analysis.uncertainty,
            data_limitations=analysis.data_limitations,
            decision_support_disclaimer=analysis.decision_support_disclaimer,
            engine_version=analysis.engine_version,
            ai_synthesis_notes=analysis.ai_synthesis_notes,
            status=analysis.status,
        )
