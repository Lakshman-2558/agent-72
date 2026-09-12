"""Current position analysis and metric directionality

Revision ID: 004_current_position_analysis
Revises: 003_evidence_ingestion_idempotency
Create Date: 2026-09-11 13:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_current_position_analysis'
down_revision: Union[str, None] = '003_evidence_ingestion_idempotency'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add direction column to metric_definitions table
    with op.batch_alter_table('metric_definitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('direction', sa.String(length=50), nullable=False, server_default='HIGHER_IS_BETTER'))

    # 2. Create institutional_analyses table
    op.create_table(
        'institutional_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('institution_id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=True),
        sa.Column('analysis_period', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('overall_confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('confidence_level', sa.String(length=20), nullable=False, server_default='HIGH'),
        sa.Column('confidence_factors', sa.JSON(), nullable=False),
        sa.Column('key_metrics', sa.JSON(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False),
        sa.Column('weaknesses', sa.JSON(), nullable=False),
        sa.Column('gaps', sa.JSON(), nullable=False),
        sa.Column('constraints', sa.JSON(), nullable=False),
        sa.Column('structural_risks', sa.JSON(), nullable=False),
        sa.Column('opportunities', sa.JSON(), nullable=False),
        sa.Column('data_gaps', sa.JSON(), nullable=False),
        sa.Column('evidence_references', sa.JSON(), nullable=False),
        sa.Column('assumptions', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='FINALIZED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['unit_id'], ['organizational_units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('institutional_analyses', schema=None) as batch_op:
        batch_op.create_index('ix_institutional_analyses_institution_id', ['institution_id'])
        batch_op.create_index('ix_institutional_analyses_unit_id', ['unit_id'])
        batch_op.create_index('ix_institutional_analyses_analysis_period', ['analysis_period'])
        batch_op.create_index('ix_analyses_inst_period', ['institution_id', 'analysis_period'])
        batch_op.create_index('ix_analyses_unit_period', ['unit_id', 'analysis_period'])


def downgrade() -> None:
    op.drop_table('institutional_analyses')
    with op.batch_alter_table('metric_definitions', schema=None) as batch_op:
        batch_op.drop_column('direction')
