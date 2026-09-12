"""Canonical institutional data model, evidence provenance, and execution tracking

Revision ID: 002_canonical_data_model
Revises: 001_initial_schema
Create Date: 2026-09-11 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_canonical_data_model'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. institutions table
    op.create_table(
        'institutions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('institution_type', sa.String(length=50), nullable=False, server_default='UNIVERSITY'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_institutions_code', 'institutions', ['code'], unique=True)
    op.create_index('ix_institutions_name', 'institutions', ['name'])

    # 2. organizational_units table
    op.create_table(
        'organizational_units',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('unit_type', sa.String(length=50), nullable=False, server_default='DEPARTMENT'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('parent_unit_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_unit_id'], ['organizational_units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizational_units_institution_id', 'organizational_units', ['institution_id'])
    op.create_index('ix_organizational_units_code', 'organizational_units', ['code'])
    op.create_index(
        'ix_units_institution_code',
        'organizational_units',
        ['institution_id', 'code'],
        unique=True
    )

    # 3. metric_definitions table
    op.create_table(
        'metric_definitions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('metric_key', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=False),
        sa.Column('default_unit', sa.String(length=50), nullable=False, server_default='count'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metric_definitions_metric_key', 'metric_definitions', ['metric_key'], unique=True)
    op.create_index('ix_metric_definitions_domain', 'metric_definitions', ['domain'])

    # 4. institutional_evidence table
    op.create_table(
        'institutional_evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=True),
        sa.Column('metric_key', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=False),
        sa.Column('numeric_value', sa.Float(), nullable=True),
        sa.Column('text_value', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('period', sa.String(length=50), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('as_of_date', sa.Date(), nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='MANUAL'),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_reference', sa.String(length=255), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('quality_tier', sa.String(length=50), nullable=False, server_default='VERIFIED'),
        sa.Column('is_stale', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_institutional_evidence_institution_id', 'institutional_evidence', ['institution_id'])
    op.create_index('ix_institutional_evidence_unit_id', 'institutional_evidence', ['unit_id'])
    op.create_index('ix_institutional_evidence_metric_key', 'institutional_evidence', ['metric_key'])
    op.create_index('ix_institutional_evidence_domain', 'institutional_evidence', ['domain'])
    op.create_index('ix_institutional_evidence_period', 'institutional_evidence', ['period'])
    op.create_index('ix_institutional_evidence_source_name', 'institutional_evidence', ['source_name'])
    op.create_index('ix_evidence_inst_period', 'institutional_evidence', ['institution_id', 'period'])
    op.create_index('ix_evidence_metric_period', 'institutional_evidence', ['metric_key', 'period'])
    op.create_index('ix_evidence_domain_period', 'institutional_evidence', ['domain', 'period'])
    op.create_index('ix_evidence_source_captured', 'institutional_evidence', ['source_name', 'captured_at'])

    # 5. Extend strategic_plans table
    with op.batch_alter_table('strategic_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('institution_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('existing_commitments', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('review_period', sa.String(length=50), nullable=False, server_default='ANNUAL'))
        batch_op.create_index('ix_strategic_plans_institution_id', ['institution_id'])
        batch_op.create_foreign_key('fk_strategic_plans_institution_id', 'institutions', ['institution_id'], ['id'], ondelete='SET NULL')

    # 6. Extend plan_objectives table
    with op.batch_alter_table('plan_objectives', schema=None) as batch_op:
        batch_op.add_column(sa.Column('metric_key', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('target_period', sa.String(length=50), nullable=True))
        batch_op.create_index('ix_plan_objectives_metric_key', ['metric_key'])

    # 7. plan_initiatives table
    op.create_table(
        'plan_initiatives',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('objective_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='NOT_STARTED'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['objective_id'], ['plan_objectives.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plan_initiatives_objective_id', 'plan_initiatives', ['objective_id'])

    # 8. initiative_milestones table
    op.create_table(
        'initiative_milestones',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('initiative_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['initiative_id'], ['plan_initiatives.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_initiative_milestones_initiative_id', 'initiative_milestones', ['initiative_id'])

    # 9. execution_reviews table
    op.create_table(
        'execution_reviews',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('period', sa.String(length=50), nullable=False),
        sa.Column('review_date', sa.Date(), nullable=False),
        sa.Column('progress_summary', sa.Text(), nullable=False),
        sa.Column('variance_notes', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['strategic_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_execution_reviews_plan_id', 'execution_reviews', ['plan_id'])
    op.create_index('ix_execution_reviews_period', 'execution_reviews', ['period'])


def downgrade() -> None:
    op.drop_table('execution_reviews')
    op.drop_table('initiative_milestones')
    op.drop_table('plan_initiatives')

    with op.batch_alter_table('plan_objectives', schema=None) as batch_op:
        batch_op.drop_index('ix_plan_objectives_metric_key')
        batch_op.drop_column('target_period')
        batch_op.drop_column('metric_key')

    with op.batch_alter_table('strategic_plans', schema=None) as batch_op:
        batch_op.drop_constraint('fk_strategic_plans_institution_id', type_='foreignkey')
        batch_op.drop_index('ix_strategic_plans_institution_id')
        batch_op.drop_column('review_period')
        batch_op.drop_column('existing_commitments')
        batch_op.drop_column('institution_id')

    op.drop_table('institutional_evidence')
    op.drop_table('metric_definitions')
    op.drop_table('organizational_units')
    op.drop_table('institutions')
