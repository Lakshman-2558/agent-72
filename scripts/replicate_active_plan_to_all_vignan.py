import sys, os
sys.path.insert(0, os.path.abspath("."))
import uuid
from datetime import datetime, timezone, date
from agent72.infrastructure.database.session import SessionLocal
from agent72.infrastructure.database.models import (
    InstitutionModel, StrategicPlanModel, PlanObjectiveModel,
    PlanInitiativeModel, InitiativeMilestoneModel, StrategicTargetModel,
    ExecutionReviewModel
)

def replicate():
    db = SessionLocal()
    try:
        # 1. Find active reference plan on DEMO-VIGNAN-P8
        ref_plan = db.query(StrategicPlanModel).filter(StrategicPlanModel.status == 'ACTIVE').first()
        if not ref_plan:
            print("No active reference plan found!")
            return

        ref_review = db.query(ExecutionReviewModel).filter(ExecutionReviewModel.plan_id == ref_plan.id).first()
        print(f"Reference plan: {ref_plan.title} (ID: {ref_plan.id})")
        print(f"Reference review: {ref_review.id if ref_review else 'None'}")

        # 2. Get all institutions
        insts = db.query(InstitutionModel).all()
        for inst in insts:
            print(f"\nProcessing {inst.name} ({inst.code}) [ID: {inst.id}]")

            existing_plans = db.query(StrategicPlanModel).filter(StrategicPlanModel.institution_id == inst.id).all()
            active_plan = next((p for p in existing_plans if p.status == 'ACTIVE'), None)

            if not active_plan and existing_plans:
                # If there's a DRAFT plan (like VIGNAN-P8), promote it to ACTIVE
                active_plan = existing_plans[0]
                active_plan.status = "ACTIVE"
                print(f"   Promoted existing plan {active_plan.id} to ACTIVE status")

            if not active_plan:
                # Create a new active plan
                new_plan_id = str(uuid.uuid4())
                active_plan = StrategicPlanModel(
                    id=new_plan_id,
                    institution_id=inst.id,
                    institution_name=inst.name,
                    title="Institutional Strategic Plan 2026-2030",
                    horizon_start_year=2026,
                    horizon_end_year=2030,
                    status="ACTIVE",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(active_plan)
                db.flush()

                # Clone objectives from ref_plan
                for obj in ref_plan.objectives:
                    new_obj_id = str(uuid.uuid4())
                    new_obj = PlanObjectiveModel(
                        id=new_obj_id,
                        plan_id=active_plan.id,
                        title=obj.title,
                        description=obj.description,
                        target_metric=obj.target_metric,
                        metric_key=obj.metric_key,
                        target_period=obj.target_period,
                        baseline_value=obj.baseline_value,
                        target_value=obj.target_value,
                        weight=obj.weight,
                        owner=obj.owner,
                        status=obj.status,
                        priority=obj.priority,
                        owner_unit_id=obj.owner_unit_id,
                        source_option_ids=obj.source_option_ids,
                        strategic_issue_ids=obj.strategic_issue_ids,
                        related_metrics=obj.related_metrics,
                        assumptions=obj.assumptions,
                        confidence=obj.confidence
                    )
                    db.add(new_obj)
                    db.flush()

                    # Clone targets
                    for tgt in obj.targets:
                        new_tgt = StrategicTargetModel(
                            id=str(uuid.uuid4()),
                            objective_id=new_obj_id,
                            metric_key=tgt.metric_key,
                            metric_definition_id=tgt.metric_definition_id,
                            baseline_value=tgt.baseline_value,
                            baseline_period=tgt.baseline_period,
                            target_value=tgt.target_value,
                            target_period=tgt.target_period,
                            direction=tgt.direction,
                            unit=tgt.unit,
                            measurement_frequency=tgt.measurement_frequency,
                            evidence_ids=tgt.evidence_ids or [],
                            confidence=tgt.confidence,
                            assumptions=tgt.assumptions or [],
                            status=tgt.status,
                            gap=tgt.gap,
                            gap_unit_label=tgt.gap_unit_label or '',
                            target_provenance=tgt.target_provenance,
                            created_at=datetime.now(timezone.utc)
                        )
                        db.add(new_tgt)

                    # Clone initiatives
                    for init in obj.initiatives:
                        new_init_id = str(uuid.uuid4())
                        new_init = PlanInitiativeModel(
                            id=new_init_id,
                            objective_id=new_obj_id,
                            title=init.title,
                            description=init.description,
                            owner=init.owner,
                            budget=init.budget,
                            status=init.status,
                            start_date=init.start_date,
                            end_date=init.end_date,
                            owner_unit_id=init.owner_unit_id,
                            supporting_units=init.supporting_units or [],
                            source_option_ids=init.source_option_ids or [],
                            dependencies=init.dependencies or [],
                            resource_requirement=init.resource_requirement,
                            implementation_risk=init.implementation_risk,
                            start_period=init.start_period,
                            end_period=init.end_period,
                            success_criteria=init.success_criteria or [],
                            evidence_ids=init.evidence_ids or [],
                            created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc)
                        )
                        db.add(new_init)
                        db.flush()

                        # Clone milestones
                        for ms in init.milestones:
                            new_ms = InitiativeMilestoneModel(
                                id=str(uuid.uuid4()),
                                initiative_id=new_init_id,
                                title=ms.title,
                                target_date=ms.target_date,
                                status=ms.status,
                                completion_date=ms.completion_date,
                                description=ms.description,
                                due_period=ms.due_period,
                                completion_percentage=ms.completion_percentage,
                                evidence_ids=ms.evidence_ids or [],
                                created_at=datetime.now(timezone.utc)
                            )
                            db.add(new_ms)
                print(f"   Created active strategic plan {active_plan.id} for {inst.code}")

            # Now check execution reviews for active_plan
            existing_reviews = db.query(ExecutionReviewModel).filter(ExecutionReviewModel.plan_id == active_plan.id).all()
            if not existing_reviews and ref_review:
                new_rev = ExecutionReviewModel(
                    id=str(uuid.uuid4()),
                    plan_id=active_plan.id,
                    period="2026-2027",
                    review_date=date.today(),
                    progress_summary=ref_review.progress_summary,
                    variance_notes=ref_review.variance_notes,
                    recommendations=ref_review.recommendations,
                    overall_status=ref_review.overall_status,
                    objective_statuses=ref_review.objective_statuses,
                    initiative_statuses=ref_review.initiative_statuses,
                    milestone_statuses=ref_review.milestone_statuses,
                    metric_variances=ref_review.metric_variances,
                    diagnostic_signals=ref_review.diagnostic_signals,
                    risks=ref_review.risks,
                    corrective_actions=ref_review.corrective_actions,
                    assumptions=ref_review.assumptions,
                    evidence_ids=ref_review.evidence_ids,
                    confidence=ref_review.confidence,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_rev)
                print(f"   Created Execution Review {new_rev.id} for plan {active_plan.id}")
            else:
                print(f"   Plan {active_plan.id} already has {len(existing_reviews)} execution review(s)")

        db.commit()
        print("\nSUCCESS: All institutions in DB now have ACTIVE plans and Execution Reviews!")
    finally:
        db.close()

if __name__ == "__main__":
    replicate()
