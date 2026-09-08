import pytest
from app.gis.spatial import haversine_distance_m, create_point_wkt
from app.gis.intersection import resolve_intersection
from app.schemas import IntersectionCandidate

def test_haversine_distance_calculation():
    # University of Florida (29.6436, -82.3549) to Downtown Gainesville (29.6516, -82.3248)
    dist = haversine_distance_m(29.6436, -82.3549, 29.6516, -82.3248)
    # Approx 3 km (3000m)
    assert 2500 < dist < 3500

    # Same point distance should be 0
    assert haversine_distance_m(29.6516, -82.3248, 29.6516, -82.3248) == 0.0

def test_create_point_wkt():
    wkt = create_point_wkt(-82.3248, 29.6516)
    assert wkt == "POINT(-82.3248 29.6516)"

def test_resolve_intersection_not_found():
    res = resolve_intersection([])
    assert res["status"] == "not_found"

def test_resolve_intersection_single():
    c = IntersectionCandidate(
        id=1,
        name="Main St & University Ave",
        latitude=29.6516,
        longitude=-82.3248,
        distance_m=15.0
    )
    res = resolve_intersection([c])
    assert res["status"] == "resolved"
    assert res["intersection"].id == 1

def test_resolve_intersection_ambiguity_needs_clarification():
    c1 = IntersectionCandidate(
        id=1,
        name="Main St & University Ave",
        latitude=29.6516,
        longitude=-82.3248,
        distance_m=45.0
    )
    c2 = IntersectionCandidate(
        id=2,
        name="Main St & 1st Ave",
        latitude=29.6520,
        longitude=-82.3248,
        distance_m=55.0
    )
    res = resolve_intersection([c1, c2])
    assert res["status"] == "needs_clarification"
    assert len(res["candidates"]) == 2

def test_resolve_intersection_clear_dominant():
    c1 = IntersectionCandidate(
        id=1,
        name="Main St & University Ave",
        latitude=29.6516,
        longitude=-82.3248,
        distance_m=12.0 # very close
    )
    c2 = IntersectionCandidate(
        id=2,
        name="Main St & 8th Ave",
        latitude=29.6580,
        longitude=-82.3248,
        distance_m=200.0 # far away
    )
    res = resolve_intersection([c1, c2])
    assert res["status"] == "resolved"
    assert res["intersection"].id == 1
