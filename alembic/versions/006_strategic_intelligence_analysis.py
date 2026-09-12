"""Institutional strategic intelligence analysis snapshot persistence

Revision ID: 006_strategic_intelligence_analysis
Revises: 005_institutional_trajectory_analysis
Create Date: 2026-09-11 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006_strategic_intelligence_analysis'
down_revision: Union[str, None] = '005_institutional_trajectory_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create institutional_strategic_intelligence_analyses table
    op.create_table(
        'institutional_strategic_intelligence_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=True),
        sa.Column('analysis_period', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_position_analysis_id', sa.String(length=36), nullable=True),
        sa.Column('trajectory_analysis_id', sa.String(length=36), nullable=True),
        sa.Column('overall_confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('confidence_level', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('confidence_factors', sa.JSON(), nullable=False),
        sa.Column('strategic_issues', sa.JSON(), nullable=False),
        sa.Column('risk_signals', sa.JSON(), nullable=False),
        sa.Column('constraint_signals', sa.JSON(), nullable=False),
        sa.Column('opportunity_signals', sa.JSON(), nullable=False),
        sa.Column('external_factors', sa.JSON(), nullable=False),
        sa.Column('strategic_priority_signals', sa.JSON(), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('uncertainty_summary', sa.JSON(), nullable=False),
        sa.Column('ai_synthesis_notes', sa.Text(), nullable=True),
        sa.Column('assumptions', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='FINALIZED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['unit_id'], ['organizational_units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('institutional_strategic_intelligence_analyses', schema=None) as batch_op:
        batch_op.create_index('ix_institutional_strategic_intelligence_analyses_institution_id', ['institution_id'])
        batch_op.create_index('ix_institutional_strategic_intelligence_analyses_unit_id', ['unit_id'])
        batch_op.create_index('ix_institutional_strategic_intelligence_analyses_analysis_period', ['analysis_period'])
        batch_op.create_index('ix_strat_intel_inst_period', ['institution_id', 'analysis_period'])
        batch_op.create_index('ix_strat_intel_unit_period', ['unit_id', 'analysis_period'])


def downgrade() -> None:
    op.drop_table('institutional_strategic_intelligence_analyses')
