import pytest
from app.services.validation_service import validate_traffic_result, create_no_data_result

def test_validate_direct_observation():
    res = validate_traffic_result(
        value=2450.0,
        metric_requested="AADT",
        metric_available="AADT",
        source_agency="FDOT",
        source_dataset="Annual Average Daily Traffic",
        source_url="https://gis.fdot.gov",
        unit="vehicles/day",
        distance_m=50.0
    )
    assert res.result_type == "DIRECT_OBSERVATION"
    assert res.value == 2450.0
    assert res.provenance is not None
    assert res.provenance.agency == "FDOT"

def test_validate_nearby_observation():
    res = validate_traffic_result(
        value=1500.0,
        metric_requested="AADT",
        metric_available="AADT",
        source_agency="FDOT",
        source_dataset="Annual Average Daily Traffic",
        source_url="https://gis.fdot.gov",
        unit="vehicles/day",
        distance_m=420.0
    )
    assert res.result_type == "NEARBY_OBSERVATION"
    assert res.value == 1500.0
    assert "420.0 meters away" in res.message

def test_validate_metric_mismatch_warning():
    res = validate_traffic_result(
        value=15000.0,
        metric_requested="hourly_traffic_volume",
        metric_available="AADT",
        source_agency="FDOT",
        source_dataset="Annual Average Daily Traffic",
        source_url="https://gis.fdot.gov",
        unit="vehicles/day",
        distance_m=50.0
    )
    assert "represents different transportation measures" in res.message or "Note: hourly_traffic_volume was requested" in res.message

def test_create_no_data_result():
    res = create_no_data_result("No authoritative records found.")
    assert res.result_type == "UNAVAILABLE"
    assert res.value is None
    assert "No authoritative records" in res.message
