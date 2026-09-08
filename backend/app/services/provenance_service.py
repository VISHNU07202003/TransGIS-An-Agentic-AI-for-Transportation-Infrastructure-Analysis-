from app.schemas import Provenance
from datetime import datetime, timezone, date

def build_provenance(
    agency: str,
    dataset: str,
    source_url: str,
    record_id: str | None = None,
    observation_date: date | None = None,
    spatial_relation: str | None = None,
) -> Provenance:
    """Build a provenance record with retrieval timestamp."""
    return Provenance(
        agency=agency,
        dataset=dataset,
        source_url=source_url,
        record_id=record_id,
        observation_date=observation_date,
        retrieval_timestamp=datetime.now(timezone.utc),
        spatial_relation=spatial_relation,
    )
