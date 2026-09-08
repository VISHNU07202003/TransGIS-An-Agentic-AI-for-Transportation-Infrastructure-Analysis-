from typing import Optional, Literal
from datetime import datetime, timezone, date
from app.schemas import TrafficResult, Provenance

def validate_traffic_result(
    value: Optional[float],
    metric_requested: str,
    metric_available: str,
    source_agency: str,
    source_dataset: str,
    source_url: str,
    unit: str = "vehicles/hour",
    record_id: Optional[str] = None,
    observation_date: Optional[date] = None,
    spatial_relation: Optional[str] = None,
    distance_m: Optional[float] = None,
) -> TrafficResult:
    """Validate a traffic result and classify it according to project data rules."""
    provenance = Provenance(
        agency=source_agency,
        dataset=source_dataset,
        source_url=source_url,
        record_id=str(record_id) if record_id is not None else None,
        observation_date=observation_date,
        retrieval_timestamp=datetime.now(timezone.utc),
        spatial_relation=spatial_relation or (f"{distance_m:.1f}m from intersection" if distance_m is not None else None)
    )
    
    if value is None:
        return TrafficResult(
            value=None,
            unit=unit,
            result_type="UNAVAILABLE",
            provenance=provenance,
            message=f"No authoritative observation was found for {metric_requested}."
        )
        
    msg_parts = []
    if metric_requested != metric_available:
        msg_parts.append(
            f"Note: {metric_requested} was requested, but the authoritative record provides {metric_available}. "
            f"These metrics represent different transportation measures."
        )
        
    result_type: Literal["DIRECT_OBSERVATION", "NEARBY_OBSERVATION", "DERIVED_FROM_SOURCE_DATA", "UNAVAILABLE"] = "DIRECT_OBSERVATION"
    if distance_m is not None and distance_m > 250:
        result_type = "NEARBY_OBSERVATION"
        msg_parts.append(f"Observation was recorded at a monitoring site {distance_m:.1f} meters away from the intersection.")
        
    message = " ".join(msg_parts) if msg_parts else "Validated authoritative transportation observation."
    
    return TrafficResult(
        value=value,
        unit=unit,
        result_type=result_type,
        provenance=provenance,
        message=message
    )

def create_no_data_result(message: str) -> TrafficResult:
    """Create a standardized no-data result."""
    return TrafficResult(
        value=None,
        unit="vehicles/hour",
        result_type="UNAVAILABLE",
        provenance=None,
        message=message
    )
