"""Initial relational schema for Agent 72

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-11 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. strategic_plans table
    op.create_table(
        'strategic_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('institution_name', sa.String(length=255), nullable=False),
        sa.Column('horizon_start_year', sa.Integer(), nullable=False),
        sa.Column('horizon_end_year', sa.Integer(), nullable=False),
        sa.Column('vision_statement', sa.Text(), nullable=True),
        sa.Column('mission_statement', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_strategic_plans_title', 'strategic_plans', ['title'])
    op.create_index('ix_strategic_plans_institution_name', 'strategic_plans', ['institution_name'])
    op.create_index('ix_strategic_plans_status', 'strategic_plans', ['status'])
    op.create_index(
        'ix_plans_institution_horizon',
        'strategic_plans',
        ['institution_name', 'horizon_start_year', 'horizon_end_year']
    )

    # 2. plan_objectives table
    op.create_table(
        'plan_objectives',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_metric', sa.String(length=255), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['strategic_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plan_objectives_plan_id', 'plan_objectives', ['plan_id'])

    # 3. strategic_options table
    op.create_table(
        'strategic_options',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('resource_intensity', sa.String(length=50), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['strategic_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_strategic_options_plan_id', 'strategic_options', ['plan_id'])

    # 4. plan_scenarios table
    op.create_table(
        'plan_scenarios',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assumptions', sa.Text(), nullable=False),
        sa.Column('projected_outcome', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['strategic_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plan_scenarios_plan_id', 'plan_scenarios', ['plan_id'])


def downgrade() -> None:
    op.drop_table('plan_scenarios')
    op.drop_table('strategic_options')
    op.drop_table('plan_objectives')
    op.drop_table('strategic_plans')
