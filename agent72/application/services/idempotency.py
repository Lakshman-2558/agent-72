"""Idempotency and deduplication key generation for institutional evidence."""

from datetime import date
from typing import Optional


class IdempotencyService:
    """Generates deterministic idempotency keys and fingerprints for incoming evidence."""

    @staticmethod
    def generate_idempotency_key(
        source_name: str,
        external_record_id: Optional[str],
        institution_id: str,
        unit_id: Optional[str],
        metric_key: str,
        numeric_value: Optional[float],
        text_value: Optional[str],
        period: str,
        as_of_date: date,
    ) -> str:
        clean_source = source_name.strip()

        # Rule 1: If external_record_id exists, key on source + external ID
        if external_record_id and external_record_id.strip():
            return f"{clean_source}:{external_record_id.strip()}"

        # Rule 2: Deterministic fingerprint including normalized value
        unit_part = unit_id.strip() if unit_id else ""
        if numeric_value is not None:
            val_part = f"num={numeric_value:.6f}".rstrip("0").rstrip(".")
        else:
            val_part = f"txt={text_value.strip() if text_value else ''}"

        fingerprint = (
            f"{clean_source}:"
            f"{institution_id.strip()}:"
            f"{unit_part}:"
            f"{metric_key.strip()}:"
            f"{val_part}:"
            f"{period.strip()}:"
            f"{as_of_date.isoformat()}"
        )
        return fingerprint
