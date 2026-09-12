"""Strategic plan execution framework, targets, and reviews (Phase 8)

Revision ID: 008_strategic_plan_execution
Revises: 007_strategic_options_analysis
Create Date: 2026-09-11 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '008_strategic_plan_execution'
down_revision: Union[str, None] = '007_strategic_options_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend strategic_plans table
    with op.batch_alter_table('strategic_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_analysis_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('selected_option_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('assumptions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('decision_support_disclaimer', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('engine_version', sa.String(length=50), nullable=True, server_default='1.0.0'))
        batch_op.add_column(sa.Column('previous_version_id', sa.String(length=36), nullable=True))

    # 2. Extend plan_objectives table
    with op.batch_alter_table('plan_objectives', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_option_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('strategic_issue_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('related_metrics', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True, server_default='PROPOSED'))
        batch_op.add_column(sa.Column('priority', sa.String(length=50), nullable=True, server_default='MEDIUM'))
        batch_op.add_column(sa.Column('owner_unit_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('assumptions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))

    # 3. Create strategic_targets table
    op.create_table(
        'strategic_targets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('objective_id', sa.String(length=36), nullable=False),
        sa.Column('metric_key', sa.String(length=100), nullable=False),
        sa.Column('metric_definition_id', sa.String(length=36), nullable=True),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('baseline_period', sa.String(length=50), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('target_period', sa.String(length=50), nullable=True),
        sa.Column('direction', sa.String(length=50), nullable=False, server_default='HIGHER_IS_BETTER'),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='count'),
        sa.Column('measurement_frequency', sa.String(length=50), nullable=False, server_default='ANNUAL'),
        sa.Column('evidence_ids', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('assumptions', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PROPOSED_TARGET'),
        sa.Column('gap', sa.Float(), nullable=True),
        sa.Column('gap_unit_label', sa.String(length=50), nullable=False, server_default=''),
        sa.Column('target_provenance', sa.String(length=100), nullable=False, server_default='DERIVED_FROM_EVIDENCE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['objective_id'], ['plan_objectives.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_strategic_targets_objective_id', 'strategic_targets', ['objective_id'])
    op.create_index('ix_strategic_targets_metric_key', 'strategic_targets', ['metric_key'])

    # 4. Extend plan_initiatives table
    with op.batch_alter_table('plan_initiatives', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_unit_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('supporting_units', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('source_option_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('dependencies', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('resource_requirement', sa.String(length=50), nullable=True, server_default='UNKNOWN'))
        batch_op.add_column(sa.Column('implementation_risk', sa.String(length=50), nullable=True, server_default='MEDIUM'))
        batch_op.add_column(sa.Column('start_period', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('end_period', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('success_criteria', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('evidence_ids', sa.JSON(), nullable=True))

    # 5. Extend initiative_milestones table
    with op.batch_alter_table('initiative_milestones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('due_period', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('completion_percentage', sa.Float(), nullable=True, server_default='0.0'))
        batch_op.add_column(sa.Column('evidence_ids', sa.JSON(), nullable=True))

    # 6. Extend execution_reviews table
    with op.batch_alter_table('execution_reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('overall_status', sa.String(length=50), nullable=True, server_default='ON_TRACK'))
        batch_op.add_column(sa.Column('objective_statuses', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('initiative_statuses', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('milestone_statuses', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('metric_variances', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('diagnostic_signals', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('risks', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('corrective_actions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('assumptions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('evidence_ids', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'))


def downgrade() -> None:
    with op.batch_alter_table('execution_reviews', schema=None) as batch_op:
        batch_op.drop_column('confidence')
        batch_op.drop_column('evidence_ids')
        batch_op.drop_column('assumptions')
        batch_op.drop_column('corrective_actions')
        batch_op.drop_column('risks')
        batch_op.drop_column('diagnostic_signals')
        batch_op.drop_column('metric_variances')
        batch_op.drop_column('milestone_statuses')
        batch_op.drop_column('initiative_statuses')
        batch_op.drop_column('objective_statuses')
        batch_op.drop_column('overall_status')

    with op.batch_alter_table('initiative_milestones', schema=None) as batch_op:
        batch_op.drop_column('evidence_ids')
        batch_op.drop_column('completion_percentage')
        batch_op.drop_column('due_period')
        batch_op.drop_column('description')

    with op.batch_alter_table('plan_initiatives', schema=None) as batch_op:
        batch_op.drop_column('evidence_ids')
        batch_op.drop_column('success_criteria')
        batch_op.drop_column('end_period')
        batch_op.drop_column('start_period')
        batch_op.drop_column('implementation_risk')
        batch_op.drop_column('resource_requirement')
        batch_op.drop_column('dependencies')
        batch_op.drop_column('source_option_ids')
        batch_op.drop_column('supporting_units')
        batch_op.drop_column('owner_unit_id')

    op.drop_index('ix_strategic_targets_metric_key', table_name='strategic_targets')
    op.drop_index('ix_strategic_targets_objective_id', table_name='strategic_targets')
    op.drop_table('strategic_targets')

    with op.batch_alter_table('plan_objectives', schema=None) as batch_op:
        batch_op.drop_column('confidence')
        batch_op.drop_column('assumptions')
        batch_op.drop_column('owner_unit_id')
        batch_op.drop_column('priority')
        batch_op.drop_column('status')
        batch_op.drop_column('related_metrics')
        batch_op.drop_column('strategic_issue_ids')
        batch_op.drop_column('source_option_ids')

    with op.batch_alter_table('strategic_plans', schema=None) as batch_op:
        batch_op.drop_column('previous_version_id')
        batch_op.drop_column('engine_version')
        batch_op.drop_column('decision_support_disclaimer')
        batch_op.drop_column('assumptions')
        batch_op.drop_column('selected_option_ids')
        batch_op.drop_column('source_analysis_ids')
