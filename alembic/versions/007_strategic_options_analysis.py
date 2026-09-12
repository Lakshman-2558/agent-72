"""Institutional strategic options analysis snapshot persistence (Phase 7)

Revision ID: 007_strategic_options_analysis
Revises: 006_strategic_intelligence_analysis
Create Date: 2026-09-11 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007_strategic_options_analysis'
down_revision: Union[str, None] = '006_strategic_intelligence_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create institutional_strategic_options_analyses table
    op.create_table(
        'institutional_strategic_options_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=True),
        sa.Column('analysis_period', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('strategic_intelligence_analysis_id', sa.String(length=36), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('scenarios', sa.JSON(), nullable=False),
        sa.Column('evaluations', sa.JSON(), nullable=False),
        sa.Column('prioritized_option_ids', sa.JSON(), nullable=False),
        sa.Column('assumptions', sa.JSON(), nullable=False),
        sa.Column('uncertainty', sa.JSON(), nullable=False),
        sa.Column('data_limitations', sa.JSON(), nullable=False),
        sa.Column('decision_support_disclaimer', sa.Text(), nullable=False),
        sa.Column('engine_version', sa.String(length=50), nullable=False, server_default='1.0.0'),
        sa.Column('ai_synthesis_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='FINALIZED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['unit_id'], ['organizational_units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('institutional_strategic_options_analyses', schema=None) as batch_op:
        batch_op.create_index('ix_institutional_strategic_options_analyses_institution_id', ['institution_id'])
        batch_op.create_index('ix_institutional_strategic_options_analyses_unit_id', ['unit_id'])
        batch_op.create_index('ix_institutional_strategic_options_analyses_analysis_period', ['analysis_period'])
        batch_op.create_index('ix_strat_options_strat_intel_id', ['strategic_intelligence_analysis_id'])
        batch_op.create_index('ix_strat_options_inst_period', ['institution_id', 'analysis_period'])
        batch_op.create_index('ix_strat_options_unit_period', ['unit_id', 'analysis_period'])


def downgrade() -> None:
    op.drop_table('institutional_strategic_options_analyses')
