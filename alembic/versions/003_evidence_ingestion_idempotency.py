"""Evidence ingestion idempotency, batch linkage, and audit logging

Revision ID: 003_evidence_ingestion_idempotency
Revises: 002_canonical_data_model
Create Date: 2026-09-11 13:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_evidence_ingestion_idempotency'
down_revision: Union[str, None] = '002_canonical_data_model'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update institutional_evidence table with batch_id and idempotency keys
    with op.batch_alter_table('institutional_evidence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_record_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('idempotency_key', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ingestion_batch_id', sa.String(length=36), nullable=True))
        batch_op.create_index('ix_institutional_evidence_external_record_id', ['external_record_id'])
        batch_op.create_index('ix_institutional_evidence_idempotency_key', ['idempotency_key'])
        batch_op.create_index('ix_institutional_evidence_ingestion_batch_id', ['ingestion_batch_id'])
        batch_op.create_index('ix_evidence_source_idempotency', ['source_name', 'idempotency_key'])

    # 2. Create ingestion_batch_logs table
    op.create_table(
        'ingestion_batch_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('batch_id', sa.String(length=36), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('received_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('inserted_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicate_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rejected_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ingestion_batch_logs_batch_id', 'ingestion_batch_logs', ['batch_id'], unique=True)
    op.create_index('ix_ingestion_batch_logs_source_name', 'ingestion_batch_logs', ['source_name'])


def downgrade() -> None:
    op.drop_table('ingestion_batch_logs')

    with op.batch_alter_table('institutional_evidence', schema=None) as batch_op:
        batch_op.drop_index('ix_evidence_source_idempotency')
        batch_op.drop_index('ix_institutional_evidence_ingestion_batch_id')
        batch_op.drop_index('ix_institutional_evidence_idempotency_key')
        batch_op.drop_index('ix_institutional_evidence_external_record_id')
        batch_op.drop_column('ingestion_batch_id')
        batch_op.drop_column('idempotency_key')
        batch_op.drop_column('external_record_id')
