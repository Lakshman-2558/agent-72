"""Institutional trajectory analysis snapshot persistence

Revision ID: 005_institutional_trajectory_analysis
Revises: 004_current_position_analysis
Create Date: 2026-09-11 14:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_institutional_trajectory_analysis'
down_revision: Union[str, None] = '004_current_position_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create institutional_trajectory_analyses table
    op.create_table(
        'institutional_trajectory_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=True),
        sa.Column('analysis_period', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('overall_confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('confidence_level', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('confidence_factors', sa.JSON(), nullable=False),
        sa.Column('metric_trends', sa.JSON(), nullable=False),
        sa.Column('trajectory_signals', sa.JSON(), nullable=False),
        sa.Column('data_limitations', sa.JSON(), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('assumptions', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='FINALIZED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['unit_id'], ['organizational_units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('institutional_trajectory_analyses', schema=None) as batch_op:
        batch_op.create_index('ix_institutional_trajectory_analyses_institution_id', ['institution_id'])
        batch_op.create_index('ix_institutional_trajectory_analyses_unit_id', ['unit_id'])
        batch_op.create_index('ix_institutional_trajectory_analyses_analysis_period', ['analysis_period'])
        batch_op.create_index('ix_traj_analyses_inst_period', ['institution_id', 'analysis_period'])
        batch_op.create_index('ix_traj_analyses_unit_period', ['unit_id', 'analysis_period'])


def downgrade() -> None:
    op.drop_table('institutional_trajectory_analyses')
